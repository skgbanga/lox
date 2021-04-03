from tokens import *


class Interpreter:
    def interpret(self, expr):
        return expr.accept(self)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self.interpret(expr.expr)

    def visit_unary_expr(self, expr):
        right = self.interpret(expr.right)

        op = expr.op
        if op.type == TokenType.MINUS:
            return -1 * right
        if op.type == TokenType.BANG:
            return not right

    def visit_binary_expr(self, expr):
        left = self.interpret(expr.left)
        right = self.interpret(expr.right)

        op = expr.op
        if op.type == TokenType.PLUS:
            return left + right
        if op.type == TokenType.MINUS:
            return left - right
        if op.type == TokenType.STAR:
            return left * right
        if op.type == TokenType.SLASH:
            return left / right
        if op.type == TokenType.GREATER:
            return left > right
        if op.type == TokenType.GREATER_EQUAL:
            return left >= right
        if op.type == TokenType.LESS:
            return left < right
        if op.type == TokenType.LESS_EQUAL:
            return left <= right
        if op.type == TokenType.EQUAL_EQUAL:
            return left == right
        if op.type != TokenType.BANG_EQUAL:
            return left != right


if __name__ == "__main__":
    from scanner import Scanner
    from parser import Parser
    from ast_printer import ASTPrinter

    code = "3 == 's'"
    tokens = Scanner(code).scan_tokens()
    expr = Parser(tokens).parse()
    print(ASTPrinter().print(expr))

    value = Interpreter().interpret(expr)
    print(value)
