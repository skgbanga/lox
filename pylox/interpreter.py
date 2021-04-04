import lox
from tokens import *


class RunTimeError(Exception):
    def __init__(self, token, msg):
        super().__init__(msg)
        self.token = token


class Interpreter:
    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RunTimeError as ex:
            lox.runtime_error(ex)

    def execute(self, stmt):
        stmt.accept(self)

    def evaluate(self, expr):
        return expr.accept(self)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expr)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        op = expr.op
        if op.type == TokenType.MINUS:
            self.check_number(op, right)
            return -right
        if op.type == TokenType.BANG:
            return not self.is_truthy(right)

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        op = expr.op
        if op.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right

            raise RunTimeError(op, "Operands must be two numbers or two strings.")
        if op.type == TokenType.MINUS:
            self.check_numbers(op, left, right)
            return left - right
        if op.type == TokenType.STAR:
            self.check_numbers(op, left, right)
            return left * right
        if op.type == TokenType.SLASH:
            self.check_numbers(op, left, right)
            try:
                return left / right
            except ZeroDivisionError:
                raise RunTimeError(op, "Division by zero.")
        if op.type == TokenType.GREATER:
            self.check_numbers(op, left, right)
            return left > right
        if op.type == TokenType.GREATER_EQUAL:
            self.check_numbers(op, left, right)
            return left >= right
        if op.type == TokenType.LESS:
            self.check_numbers(op, left, right)
            return left < right
        if op.type == TokenType.LESS_EQUAL:
            self.check_numbers(op, left, right)
            return left <= right
        # lox's equality/inequality semantics are same as python
        # You can’t ask lox if 3 is less than "three", but you can ask if it’s equal to it.
        if op.type == TokenType.EQUAL_EQUAL:
            return left == right
        if op.type != TokenType.BANG_EQUAL:
            return left != right

    def is_truthy(self, value):
        # false and nil are falsey, and everything else is truthy.
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def check_number(self, op, operand):
        if isinstance(operand, float):
            return

        raise RunTimeError(op, "Operand must be a number.")

    def check_numbers(self, op, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RunTimeError(op, "Operands must be numbers.")

    def stringify(self, value):
        if value is None:
            return "nil"

        if isinstance(value, bool):
            return str(value).lower()

        value = str(value)
        if value.endswith(".0"):
            return value[:-2]

        return value
