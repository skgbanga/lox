import sys

class Lox:
    had_error = False
    had_runtime_error = False

    @staticmethod
    def error(line, msg):
        Lox.report(line, "", msg)

    @staticmethod
    def parsing_error(token, msg):
        from tokens import TokenType

        if token.type == TokenType.EOF:
            Lox.report(token.line, "at end", msg)
        else:
            Lox.report(token.line, "at '" + token.lexeme + "'", msg)


    @staticmethod
    def runtime_error(error):
        print(error.args[0] + f"\n[line {error.token.line}]")
        Lox.had_runtime_error = True


    @staticmethod
    def report(line, where, msg):
        print(f"[line {line}] Error: {where}: {msg}", file=sys.stderr)
        Lox.had_error = True
