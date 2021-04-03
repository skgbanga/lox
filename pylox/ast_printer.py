from expressions import *
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
        s = ' '.join(expr.accept(self) for expr in exprs)
        return f'({name} {s})'


if __name__ == '__main__':
    expr = BinaryExpr(
            UnaryExpr(
                Token(TokenType.MINUS, "-", None, 1),
                LiteralExpr(123)
            ),
            Token(TokenType.STAR, "*", None, 1),
            GroupingExpr(LiteralExpr(20.2))
           )
    s = ASTPrinter().print(expr)
    print(s)
