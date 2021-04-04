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


def ExpressionStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_expr_stmt(self)
