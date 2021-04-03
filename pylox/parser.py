"""
 == simple grammar ==
expression     → literal
               | unary
               | binary
               | grouping ;

literal        → NUMBER | STRING | "true" | "false" | "nil" ;
unary          → ( "-" | "!" ) expression ;
binary         → expression operator expression ;
grouping       → "(" expression ")" ;
operator       → "==" | "!=" | "<" | "<=" | ">" | ">="
               | "+"  | "-"  | "*" | "/" ;


 == precedence/associativity for operators ==
Name            Operators       Associates
Equality        == !=           Left
Comparison      > >= < <=       Left
Term            - +             Left
Factor          / *             Left
Unary           ! -             Right


 == Bake precedence into grammar == 
expression     → equality
equality       → comparison ( ( "!=" | "=="  ) comparison  )*
comparison     → term ( ( ">" | ">=" | "<" | "<="  ) term  )*
term           → factor ( ( "-" | "+"  ) factor  )*
factor         → unary ( ( "/" | "*"  ) unary  )*
unary          → ( "!" | "-"  ) unary
               | primary
primary        → NUMBER | STRING | "true" | "false" | "nil"
              | "(" expression ")"
"""

from tokens import *
from expressions import *
import lox


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None

    def expression(self):
        return self.equality()

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

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)

        raise self.error(self.peek(), "Expect expression.")

    def consume(self, type, msg):
        if self.check(type):
            self.advance()
            return

        raise self.error(self.peek(), msg)

    def error(self, token, msg):
        lox.parsing_error(token, msg)
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
