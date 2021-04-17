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
    "variable",
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


class LogicalExpr(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)


class GroupingExpr(Expr):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


class VariableExpr(Expr):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


class AssignExpr(Expr):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)


class CallExpr(Expr):
    def __init__(self, callee, paren, args):
        self.callee = callee
        self.paren = paren
        self.args = args

    def accept(self, visitor):
        return visitor.visit_call_expr(self)


class GetExpr(Expr):
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

    def accept(self, visitor):
        return visitor.visit_get_expr(self)


class SetExpr(Expr):
    def __init__(self, obj, name, value):
        self.obj = obj
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_set_expr(self)


class ThisExpr(Expr):
    def __init__(self, keyword):
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visit_this_expr(self)


class SuperExpr(Expr):
    def __init__(self, keyword, method):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor):
        return visitor.visit_super_expr(self)
