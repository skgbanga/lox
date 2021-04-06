from tokens import *
from lox import Lox


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0  # token start
        self.current = 0
        self.line = 1
        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }

    def scan_tokens(self):
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif c == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            )
        elif c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif c == ">":
            self.add_token(
                TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            )
        elif c == "/":
            if self.match("/"):  # a comment, consume till \n
                while not self.at_end() and self.peek() != "\n":
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c == " ":
            pass
        elif c == "\r":
            pass
        elif c == "\t":
            pass
        elif c == "\n":
            line += 1
        elif c == '"':
            self.string()
        elif c.isdigit():
            self.number()
        elif self.isalpha(c):
            self.identifier()
        else:
            Lox.error(self.line, f"Unexpected character '{c}'.")

    def add_token(self, type, literal=None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def at_end(self):
        return self.current >= len(self.source)

    # advance: consume character
    # peek: see next character, but don't consume
    # peek_next: see next to next character, don't consume
    # match: conditionally consume character
    def advance(self):
        ch = self.source[self.current]
        self.current += 1
        return ch

    def match(self, ch):
        if self.at_end() or self.source[self.current] != ch:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def string(self):
        while not self.at_end() and self.peek() != '"':
            if self.peek() == "\n":  # multi line comments
                self.line += 1
            self.advance()

        if self.at_end():
            Lox.error(line, "Unterminated string.")
            return

        self.advance()  # final "
        literal = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, literal)

    def number(self):
        def consume_digits():
            while not self.at_end() and self.peek().isdigit():
                self.advance()

        consume_digits()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            consume_digits()

        literal = float(self.source[self.start : self.current])
        self.add_token(TokenType.NUMBER, literal)

    def identifier(self):
        while self.isalnum(self.peek()):
            self.advance()

        lexeme = self.source[self.start : self.current]
        type = self.keywords.get(lexeme, TokenType.IDENTIFIER)
        self.add_token(type)

    def isalpha(self, ch):
        return ch.isalpha() or ch == "_"

    def isalnum(self, ch):
        return ch.isalnum() or ch == "_"
