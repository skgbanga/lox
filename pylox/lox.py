import sys
from tokens import *

had_error = False
had_runtime_error = False


def error(line, msg):
    report(line, "", msg)


def parsing_error(token, msg):
    if token.type == TokenType.EOF:
        report(token.line, " at end", msg)
    else:
        report(token.line, "at '" + token.lexeme + "'", msg)


def runtime_error(error):
    print(error.args[0] + f"\n[line {error.token.line}]")
    had_runtime_error = True


def report(line, where, msg):
    print(f"[line {line}] Error: {where}: {msg}", file=sys.stderr)
    had_error = True


if __name__ == "__main__":
    from scanner import Scanner
    from parser import Parser
    from interpreter import Interpreter

    args = sys.argv
    if len(args) > 2:
        print("Usage: ./lox [script]")
        sys.exit(64)
    if len(args) == 2:
        # add file reading support
        pass
    else:
        print("Lox 0.1.0")
        try:
            while True:
                line = input("> ")
                tokens = Scanner(line).scan_tokens()
                if len(tokens) == 1:   # only EOF
                    continue
                expr = Parser(tokens).parse()
                if expr:
                    Interpreter().interpret(expr)
        except EOFError:
            print()
