from tokens import *
import lox

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0  # token start
        self.current = 0
        self.line = 1;

    def scan_tokens(self):
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if   c == '(': add_token(TokenType.LEFT_PAREN)
        elif c == ')': add_token(TokenType.RIGHT_PAREN)
        elif c == '{': add_token(TokenType.LEFT_BRACE)
        elif c == '}': add_token(TokenType.RIGHT_BRACE)
        elif c == ',': add_token(TokenType.COMMA)
        elif c == '.': add_token(TokenType.DOT)
        elif c == '-': add_token(TokenType.MINUS)
        elif c == '+': add_token(TokenType.PLUS)
        elif c == ';': add_token(TokenType.SEMICOLON)
        elif c == '*': add_token(TokenType.STAR)
        elif c == '!': add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=': add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<': add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>': add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c == '/':
            if match('/'):  # a comment, consume till \n
                while not self.at_end() and self.peek() != '\n':
                    self.advance()
            else:
                add_token(TokenType.SLASH)
        elif c == ' ': pass
        elif c == '\r': pass
        elif c == '\t': pass
        elif c == '\n': line += 1
        elif c == '"': string()
        elif c.isdigit(): number()
        else:
            lox.error(line, 'Unexpected character.')


    def add_token(type, literal=None):
        text = self.source[start:current]
        tokens.append(Token(type, text, literal, line))

    def at_end(self):
        return self.current >= len(self.source)

    # advance: consume character
    # peek: see next character, but don't consume
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
            return '\0'
        return self.source[self.current]


    def string(self):
        while not self.at_end() and self.peek() != '"':
            if self.peek() == '\n':   # multi line comments
                self.line += 1
            self.advance()

        if self.at_end():
            lox.error(line, "Unterminated string.")
            return

        self.advance()  # final "
        literal = self.source[self.start + 1, self.current - 1]
        self.add_token(TokenType.STRING, literal)

    def number(self):
        pass
