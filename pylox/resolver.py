from enum import Enum, auto
from lox import *


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()


class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE

    def resolve(self, stmts_or_exprs):
        if not isinstance(stmts_or_exprs, list):
            stmts_or_exprs = [stmts_or_exprs]

        for stmt_or_expr in stmts_or_exprs:
            stmt_or_expr.accept(self)

    # interesting statements
    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.stmts)
        self.end_scope()

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.expr:
            self.resolve(stmt.expr)
        self.define(stmt.name)

    def visit_func_statement(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)  # for recursive functions
        self.resolve_function(stmt, FunctionType.FUNCTION)

    # lame statements
    def visit_print_stmt(self, stmt):
        self.resolve(stmt.expr)

    def visit_assert_stmt(self, stmt):
        self.resolve(stmt.expr)

    def visit_expr_stmt(self, stmt):
        self.resolve(stmt.expr)

    def visit_if_statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then)
        if stmt.otherwise:
            self.resolve(stmt.otherwise)

    def visit_while_statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.stmt)

    def visit_return_statement(self, stmt):
        if self.current_function == FunctionType.NONE:
            Lox.error(stmt.keyword, "Can't return from top-level code.")
            return

        if stmt.expr:
            self.resolve(stmt.expr)

    # interesting expressions
    def visit_variable_expr(self, expr):
        if self.scopes and not self.scopes[-1].get(expr.name.lexeme, True):
            Lox.error(expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr):
        self.resolve(expr.expr)
        self.resolve_local(expr, expr.name)

    # lame expressions
    def visit_literal_expr(self, _expr):
        pass

    def visit_grouping_expr(self, expr):
        self.resolve(expr.expr)

    def visit_unary_expr(self, expr):
        self.resolve(expr.right)

    def visit_binary_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_logical_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr):
        self.resolve(expr.callee)
        for arg in expr.args:
            self.resolve(arg)

    def begin_scope(self):
        self.scopes.append(dict())

    def end_scope(self):
        self.scopes.pop()

    def declare(self, token):
        if not self.scopes:  # global scope
            return

        scope = self.scopes[-1]
        if token.lexeme in scope:
            Lox.error("A variable with same name already exists in this scope.")
            return

        scope[token.lexeme] = False

    def define(self, token):
        if not self.scopes:
            return

        self.scopes[-1][token.lexeme] = True

    def resolve_local(self, expr, name):
        for idx, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, idx)
                return

    def resolve_function(self, stmt, type):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in stmt.params:
            self.declare(param)
            self.define(param)

        self.resolve(stmt.body)
        self.end_scope()
        self.current_function = enclosing_function
