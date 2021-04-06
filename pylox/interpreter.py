from lox import Lox
from tokens import *


class RunTimeError(Exception):
    def __init__(self, token, msg):
        super().__init__(msg)
        self.token = token

class Environment:
    def __init__(self):
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def assign(self, name, value):
        if name.lexeme not in self.values:
            raise RunTimeError(name, f"Undefined variable '{name.lexeme}'.")

        self.values[name.lexeme] = value

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise RunTimeError(name, f"Undefined variable '{name.lexeme}'.")


class Interpreter:
    def __init__(self):
        self.env = Environment()

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RunTimeError as ex:
            Lox.runtime_error(ex)

    # statements
    def execute(self, stmt):
        stmt.accept(self)

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))

    def visit_expr_stmt(self, stmt):
        value = self.evaluate(stmt.expr)

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.expr:
            value = self.evaluate(stmt.expr)

        self.env.define(stmt.name.lexeme, value)

    # expressions
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

    def visit_variable_expr(self, expr):
        return self.env.get(expr.name)

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.expr)
        self.env.assign(expr.name, value)
        return value

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
