import sys
from lox import Lox

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 2:
        print("Usage: ./lox [script]")
        sys.exit(64)

    from scanner import Scanner
    from parser import Parser, ParseError
    from interpreter import Interpreter

    if len(args) == 2:
        filename = args[1]
        with open(filename, 'r') as f:
            data = f.read()

        tokens = Scanner(data).scan_tokens()
        statements = Parser(tokens).parse()
        if not Lox.had_error:
            Interpreter().interpret(statements)
    else:
        print("Lox 0.1.0")
        interpreter = Interpreter()
        try:
            while True:
                line = input("> ")
                tokens = Scanner(line).scan_tokens()
                statements = Parser(tokens).parse()
                if not Lox.had_error:
                    interpreter.interpret(statements)

                Lox.had_error = False
        except EOFError:
            print()
