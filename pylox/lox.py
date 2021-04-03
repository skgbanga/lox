from tokens import *

has_error = False


def error(line, msg):
    report(line, "", msg)


def parsing_error(token, msg):
    if token.type == TokenType.EOF:
        report(token.line, " at end", msg)
    else:
        report(token.line, "at '" + token.lexeme + "'", msg)


def report(line, where, msg):
    print(f"[line {line}] Error: {where}: {msg}")
    has_error = True
