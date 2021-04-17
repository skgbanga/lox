"""

 == GRAMMAR == 

program        → declaration* EOF

declaration    → classDecl
               | varDecl
               | funcDecl
               | statement

classDecl      → "class" IDENTIFIER ( "<" IDENTIFIER )? "{" function* "}" ;
varDecl        → "var" IDENTIFIER ( "=" expression  )? ";"
funDecl        → "fun" function ;
function       → IDENTIFIER "(" parameters? ")" block ;
parameters     → IDENTIFIER ( "," IDENTIFIER  )* ;
statement      → exprStmt
               | printStmt
               | assertStmt
               | block
               | ifStmt
               | whileStmt
               | forStmt
               | returnStmt

exprStmt       → expression ";"
printStmt      → "print" expression ";"
assertStmt     → "assert" expression ";"
block          → "{" declaration* "}"
ifStmt         → "if" "(" expression ")" statement
               ( "else" statement  )?
whileStmt      → "while" "(" expression ")" statement
forStmt        → "for" "(" ( varDecl | exprStmt | ";"  )
                 expression? ";"
                 expression? ")" statement ;
returnStmt     → "return" expression? ";" ;


# == expressions
# might seem weird but assignment is an expression with lowest precedence
expression     → assignment ;
assignment     → (call ".")? IDENTIFIER "=" assignment
               | logic_or ;
logic_or       → logic_and ( "or" logic_and  )* ;
logic_and      → equality ( "and" equality  )* ;
equality       → comparison ( ( "!=" | "=="  ) comparison  )*
comparison     → term ( ( ">" | ">=" | "<" | "<="  ) term  )*
term           → factor ( ( "-" | "+"  ) factor  )*
factor         → unary ( ( "/" | "*"  ) unary  )*
unary          → ( "!" | "-"  ) unary | call
call           → primary ( "(" arguments? ")" | "." IDENTIFIER )* ;

primary        → NUMBER | STRING | "true" | "false" | "nil"
                 | "(" expression ")" | IDENTIFIER
                 | "super" "." IDENTIFIER
arguments      → expression ( "," expression  )* ;

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
            if self.match(TokenType.FUN):
                return self.func_declaration()
            if self.match(TokenType.CLASS):
                return self.class_declaration()

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

    def func_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")
        params = [] if self.match(TokenType.RIGHT_PAREN) else self.parameters()

        self.consume(TokenType.LEFT_BRACE, "Expect '{' after function.")
        return FuncStmt(name, params, self.block())

    def parameters(self):
        # called if function has atleast one parameter
        params = []
        while True:
            params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter"))
            if not self.match(TokenType.COMMA):
                break

        assert params
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after function params")
        return params

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        supercls = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            supercls = VariableExpr(self.previous())

        self.consume(TokenType.LEFT_BRACE, "Expect '{' after class name.")
        funcs = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.at_end():
            funcs.append(self.func_declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return ClassStmt(name, supercls, funcs)

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.ASSERT):
            return self.assert_statement()
        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()

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

    def block(self):
        stmts = []
        while not self.at_end() and not self.check(TokenType.RIGHT_BRACE):
            stmts.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return stmts

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if' condition.")

        then = self.statement()
        otherwise = None
        if self.match(TokenType.ELSE):
            otherwise = self.statement()

        return IfStmt(condition, then, otherwise)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if' condition.")

        stmt = self.statement()
        return WhileStmt(condition, stmt)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        init = None
        if self.match(TokenType.SEMICOLON):  # match also consumes if true
            pass
        elif self.match(TokenType.VAR):
            init = self.var_declaration()
        else:
            self.expression_statement()

        condition = None if self.check(TokenType.SEMICOLON) else self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")

        increment = None if self.check(TokenType.RIGHT_PAREN) else self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clause")

        body = self.statement()

        # we are going to transform this `for` loop into a `while` loop
        # increment happens at the end
        if increment:
            body = BlockStmt([body, increment])
        if not condition:
            condition = LiteralExpr(True)

        body = WhileStmt(condition, body)
        if init:
            body = BlockStmt([init, body])  # new scope
        return body

    def return_statement(self):
        keyword = self.previous()
        expr = None if self.check(TokenType.SEMICOLON) else self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return.")
        return ReturnStmt(keyword, expr)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return ExpressionStmt(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            right = self.assignment()  # right associative
            if isinstance(expr, VariableExpr):
                return AssignExpr(expr.name, right)
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.obj, expr.name, right)

            self.error(equals, "Invalid assignment target.")  # not an lvalue

        return expr

    def logic_or(self):
        expr = self.logic_and()
        while self.match(TokenType.OR):
            op = self.previous()
            right = self.logic_and()
            expr = LogicalExpr(expr, op, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous()
            right = self.equality()
            expr = LogicalExpr(expr, op, right)
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

        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'"
                )
                expr = GetExpr(expr, name)
            else:
                break

        return expr

    def finish_call(self, callee):
        args = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                args.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
        return CallExpr(callee, self.previous(), args)

    def primary(self):
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.NIL):
            return LiteralExpr(None)
        if self.match(TokenType.THIS):
            return ThisExpr(self.previous())
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after super.")
            method = self.consume(
                TokenType.IDENTIFIER, "Expect superclass method name."
            )
            return SuperExpr(keyword, method)

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

        ok = set(
            [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]
        )

        while not self.at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            type = self.peek().type
            if type in ok:
                return

            self.advance()
