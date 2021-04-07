"""

 == GRAMMAR == 

program        → declaration* EOF

declaration    → varDecl
               | statement

varDecl        → "var" IDENTIFIER ( "=" expression  )? ";"
statement      → exprStmt
               | printStmt
               | assertStmt
               | block
               | ifStmt

exprStmt       → expression ";"
printStmt      → "print" expression ";"
assertStmt     → "assert" expression ";"
block          → "{" declaration* "}"
ifStmt         → "if" "(" expression ")" statement
               ( "else" statement  )? ;


# == expressions
# might seem weird but assignment is an expression with lowest precedence
expression     → assignment ;
assignment     → IDENTIFIER "=" assignment
                | equality ;
equality       → comparison ( ( "!=" | "=="  ) comparison  )*
comparison     → term ( ( ">" | ">=" | "<" | "<="  ) term  )*
term           → factor ( ( "-" | "+"  ) factor  )*
factor         → unary ( ( "/" | "*"  ) unary  )*
unary          → ( "!" | "-"  ) unary
               | primary
primary        → NUMBER | STRING | "true" | "false" | "nil"
              | "(" expression ")" | IDENTIFIER

"""

from tokens import *
from expressions import *
from statements import *
from lox import Lox

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.at_end():
            statements.append(self.declaration())

        return statements

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()

            return self.statement()
        except ParseError:
            self.synchronize()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        expr = None
        if self.match(TokenType.EQUAL):
            expr = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return VarStmt(name, expr)


    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.ASSERT):
            return self.assert_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block_statement()
        if self.match(TokenType.IF):
            return self.if_statement()

        return self.expression_statement()

    def print_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value")
        return PrintStmt(expr)

    def assert_statement(self):
        token = self.previous()
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value")
        return AssertStmt(token, expr)

    def block_statement(self):
        stmts = []
        while not self.at_end() and not self.check(TokenType.RIGHT_BRACE):
            stmts.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return BlockStmt(stmts)

    def if_statement(self):
        self.consume(TokenType.LEFT_PARENT, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PARENT, "Expect ')' after 'if' condition.")

        then = self.statement()
        otherwise = None
        if self.match(TokenType.ELSE):
            otherwise = self.statement()

        return IfStmt(condition, then, otherwise)


    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return ExpressionStmt(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.equality()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            right = self.assignment()  # right associative
            if isinstance(expr, VariableExpr):
                return AssignExpr(expr.name, right)

            self.error(equals, 'Invalid assignment target.')

        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            op = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, op, right)

        return expr

    def comparison(self):
        expr = self.term()
        while self.match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            op = self.previous()
            right = self.term()
            expr = BinaryExpr(expr, op, right)

        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            op = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, op, right)

        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, op, right)

        return expr

    def unary(self):
        if self.match(TokenType.MINUS, TokenType.BANG):
            op = self.previous()
            right = self.unary()
            return UnaryExpr(op, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.NIL):
            return LiteralExpr(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)

        raise self.error(self.peek(), "Expect expression.")

    def consume(self, type, msg):
        if self.check(type):
            self.advance()
            return self.previous()

        raise self.error(self.peek(), msg)

    def error(self, token, msg):
        Lox.parsing_error(token, msg)
        return ParseError()

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def peek(self):
        return self.tokens[self.current]

    def at_end(self):
        return self.peek().type == TokenType.EOF

    def check(self, type):
        if self.at_end():  # can't check for EOF
            return False
        return self.peek().type == type

    def advance(self):
        if self.at_end():
            return
        self.current += 1

    def previous(self):
        return self.tokens[self.current - 1]


    def synchronize(self):
        self.advance()

        ok = set([
            TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR,
            TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN
            ])

        while not self.at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            type = self.peek().type
            if type in ok:
                return

            self.advance()
