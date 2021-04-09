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

class AssertStmt(Stmt):
    def __init__(self, token, expr):
        self.token = token  # for printing line number
        self.expr = expr
    
    def accept(self, visitor):
        return visitor.visit_assert_stmt(self)


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


class BlockStmt(Stmt):
    def __init__(self, stmts):
        self.stmts = stmts

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


class IfStmt(Stmt):
    def __init__(self, condition, then, otherwise):
        self.condition = condition
        self.then = then
        self.otherwise = otherwise

    def accept(self, visitor):
        return visitor.visit_if_statement(self)


class WhileStmt(Stmt):
    def __init__(self, condition, stmt):
        self.condition = condition
        self.stmt = stmt

    def accept(self, visitor):
        return visitor.visit_while_statement(self)
