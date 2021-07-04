import sys
from esoteric.befunge import Befunge

if __name__ == "__main__":
    code = ""
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as file:
            code = file.read()
    else:
        code = sys.stdin.read()

    if code == "":
        print("No code in stdin or file", file=sys.stderr)
        exit(1)

    Befunge.from_string(code).run()
