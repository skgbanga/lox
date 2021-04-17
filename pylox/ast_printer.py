from tokens import *


class ASTPrinter:
    def print(self, expr):
        return expr.accept(self)

    def visit_literal_expr(self, expr):
        if not expr.value:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.op.lexeme, expr.right)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.op.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expr)

    def parenthesize(self, name, *exprs):
        s = " ".join(expr.accept(self) for expr in exprs)
        return f"({name} {s})"


if __name__ == "__main__":
    from scanner import Scanner
    from parser import Parser

    # code = "3 + 4 * 5 - 5 == 5 > 8 < -10"
    code = "3 + "
    tokens = Scanner(code).scan_tokens()
    # print(tokens)
    expr = Parser(tokens).parse()

    assert expr is not None
    s = ASTPrinter().print(expr)
    print(s)
