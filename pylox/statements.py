from abc import abstractmethod, ABC

class Stmt(ABC):
    @abstractmethod
    def accept(visitor):
        pass

class PrintStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class ExpressionStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_expr_stmt(self)


class VarStmt(Stmt):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)
