from abc import abstractmethod, ABC

expression_types = [
        "literal",
        "unary",
        "binary",
        "grouping",

        "assign",
        "call",
        "get",
        "logical",
        "set",
        "super",
        "this",
        "variable"
]


class Expr(ABC):
    @abstractmethod
    def accept(visitor):
        pass


class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


class UnaryExpr(Expr):
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class BinaryExpr(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class GroupingExpr(Expr):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)
