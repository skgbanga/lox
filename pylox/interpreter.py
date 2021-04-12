from lox import Lox
from tokens import *
from loxcallable import LoxCallable


class RunTimeError(Exception):
    def __init__(self, token, msg):
        super().__init__(msg)
        self.token = token


class Return(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            return self.enclosing.assign(name, value)

        raise RunTimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, depth, name, value):
        self.ancestor(depth).values[name.lexeme] = value

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing:
            return self.enclosing.get(name)

        raise RunTimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, depth, lexeme):
        return self.ancestor(depth).values[lexeme]

    def ancestor(self, depth):
        env = self
        for i in range(depth):
            env = env.enclosing
        return env

class LoxFunction(LoxCallable):
    def __init__(self, stmt, closure):
        self.stmt = stmt
        self.closure = closure

    def arity(self):
        return len(self.stmt.params)

    def call(self, interpreter, args):
        env = Environment(enclosing=self.closure)
        for param, arg in zip(self.stmt.params, args): # strict zip
            env.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.stmt.body, env)
        except Return as ex:
            return ex.value


class Interpreter:
    def __init__(self):
        class Clock(LoxCallable):
            def arity(self):
                return 0

            def call(self, _interpreter, _args):
                import time
                return time.time()

        self.globals = Environment()
        self.globals.define("clock", Clock())
        self.env = self.globals
        self.locals = {}

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RunTimeError as ex:
            Lox.runtime_error(ex)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def lookup_variable(self, name, expr):
        depth = self.locals.get(expr)
        if depth is not None:
            return self.env.get_at(depth, name.lexeme)
        return self.globals.get(name)

    # statements
    def execute(self, stmt):
        stmt.accept(self)

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))

    def visit_assert_stmt(self, stmt):
        value = self.evaluate(stmt.expr)
        if not self.is_truthy(value):
            raise RunTimeError(stmt.token, "Assert Failed.")

    def visit_expr_stmt(self, stmt):
        value = self.evaluate(stmt.expr)

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.expr:
            value = self.evaluate(stmt.expr)

        self.env.define(stmt.name.lexeme, value)

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.stmts, Environment(self.env))

    def execute_block(self, stmts, env):
        previous = self.env
        try:
            self.env = env
            for stmt in stmts:
                self.execute(stmt)
        finally:
            self.env = previous

    def visit_if_statement(self, stmt):
        value = self.evaluate(stmt.condition)
        if self.is_truthy(value):
            self.execute(stmt.then)
        else:
            if stmt.otherwise:
                self.execute(stmt.otherwise)

    def visit_while_statement(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.stmt)

    def visit_func_statement(self, func):
        self.env.define(func.name.lexeme, LoxFunction(func, self.env))

    def visit_return_statement(self, stmt):
        value = None
        if stmt.expr:
            value = self.evaluate(stmt.expr)

        raise Return(value)

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

    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)
        truthy = self.is_truthy(left)
        op = expr.op
        if op.type == TokenType.OR and truthy or op.type == TokenType.AND and not truthy:
            return left

        return self.evaluate(expr.right)


    def visit_variable_expr(self, expr):
        return self.lookup_variable(expr.name, expr)

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.expr)
        depth = self.locals.get(expr)
        if depth is not None:
            self.env.assign_at(depth, expr.name, value)
        else:
            self.env.assign(expr.name, value)

        return value

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        if not hasattr(callee, "call"):
            raise RunTimeError(expr.paren, "can only call functions.")

        args = [self.evaluate(arg) for arg in expr.args]
        if len(args) != callee.arity():
            raise RunTimeError(expr.paren, f"Expected {callee.arity()} arguments, {len(args)} provided.")
        return callee.call(self, args)

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
