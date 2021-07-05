"""
Implementation of Befunge-93

See https://esolangs.org/wiki/Befunge#Instructions in particular
"""

from esoteric.interpreter import Actions, coord, Interpreter
import random

DELTA_CHANGERS = {
    ">": coord(1, 0),
    "v": coord(0, 1),
    "<": coord(-1, 0),
    "^": coord(0, -1),
}

BINARY_OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: b - a,
    "*": lambda a, b: b * a,
    "%": lambda a, b: b % a,
    "`": lambda a, b: int(b > a),
}

STACK_MODIFIERS = {
    "!": lambda stack: stack.append(int(not stack.pop())),
    ":": lambda stack: stack.append(stack[-1] if len(stack) else 0),
    "\\": lambda stack: stack.extend(
        [stack.pop(), 0] if len(stack) < 2 else [stack.pop(), stack.pop()]
    ),
    "$": lambda stack: stack.pop(),
}

NUMBERS = list(str(i) for i in range(10))

DIRECTIONS = list(DELTA_CHANGERS.values())


class Befunge(Interpreter):
    delta = coord(1, 0)
    stack = []
    stringmode = False

    def step(self):
        try:
            res = self._step()
            if res[1] == Actions.HALT:
                self.halted = True
        except Exception as err:
            print(self.pos, self.delta, self.cell, self.stack)
            raise err
        return res

    def _step(self):
        action = Actions.NONE
        value = None
        if self.stringmode:
            if self.cell == '"':
                self.stringmode = False
            else:
                # Stringmode overrides everything
                self.stack.append(ord(self.cell))
        elif self.cell == "@":
            return (self.pos, Actions.HALT, None)
        elif self.cell == '"':
            self.stringmode = True
        elif self.cell == ".":
            action = Actions.OUTPUT
            value = str(self.stack.pop())
        elif self.cell == ",":
            action = Actions.OUTPUT
            value = chr(self.stack.pop())
        elif self.cell == "&":
            action = Actions.INT_INPUT
        elif self.cell == "~":
            action = Actions.STRING_INPUT
        elif self.cell == "g":
            y, x = self.stack.pop(), self.stack.pop()
            try:
                self.stack.append(ord(self.board[y][x]))
            except KeyError:
                self.stack.append(0)
        elif self.cell == "p":
            y, x, v = self.stack.pop(), self.stack.pop(), self.stack.pop()
            try:
                self.board[y][x] = chr(v)
            except KeyError:
                action = Actions.ERROR
                value = f"No such position ({x}, {y})"
        elif self.cell in DELTA_CHANGERS:
            self.delta = DELTA_CHANGERS[self.cell]
        elif self.cell == "?":
            self.delta = random.choice(DIRECTIONS)
        elif self.cell == "_":
            # Left if true, right if false
            v = not len(self.stack) or self.stack.pop()
            self.delta = coord(-1, 0) if v else coord(1, 0)
        elif self.cell == "|":
            # Up if true, down if false
            v = not len(self.stack) or self.stack.pop()
            self.delta = coord(0, -1) if v else coord(0, 1)
        elif self.cell in BINARY_OPS:
            self.stack.append(BINARY_OPS[self.cell](self.stack.pop(), self.stack.pop()))
        elif self.cell == "/":
            a, b = self.stack.pop(), self.stack.pop()
            if a == 0:
                # If division by 0, ask user what the answer is
                # (according to the spec)
                action = Actions.INT_INPUT
            else:
                self.stack.append(b // a)
        elif self.cell in STACK_MODIFIERS:
            STACK_MODIFIERS[self.cell](self.stack)
        elif self.cell in NUMBERS:
            self.stack.append(int(self.cell))

        # Update position, wrap around source code
        if self.cell == "#" and not self.stringmode:
            self.pos = (self.pos + self.delta + self.delta) % self.maxpos
        else:
            self.pos = (self.pos + self.delta) % self.maxpos
        return (self.pos, action, value)

    def recv(self, value):
        self.stack.append(value)

    def internal_state(self):
        return [str(i) for i in reversed(self.stack)]
