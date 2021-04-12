import sys

class Lox:
    had_error = False
    had_runtime_error = False
    had_assert_error = False

    @staticmethod
    def error(token, msg):
        Lox.report(token.line, "", msg)

    @staticmethod
    def parsing_error(token, msg):
        from tokens import TokenType

        if token.type == TokenType.EOF:
            Lox.report(token.line, "at end", msg)
        else:
            Lox.report(token.line, "at '" + token.lexeme + "'", msg)

    @staticmethod
    def runtime_error(error):
        print(f"[line {error.token.line}] {error.args[0]}")
        Lox.had_runtime_error = True

    @staticmethod
    def report(line, where, msg):
        print(f"[line {line}] Error: {where}: {msg}", file=sys.stderr)
        Lox.had_error = True
