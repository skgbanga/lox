has_error = False

def error(line, msg):
    report(line, '', msg)

def report(line, where, msg):
    print(f'[line {line}] Error: {where}: {msg}')
    has_error = True
