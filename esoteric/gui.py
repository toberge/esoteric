import curses
import time
from functools import partial
from esoteric.interpreter import Actions
from itertools import islice


class Gui:
    def __init__(self, screen, interpreter):
        curses.halfdelay(1)
        screen.clear()
        self.screen = screen
        self.interpreter = interpreter
        self.result = ""

        # Layout:
        # code | stack
        # code | result
        lines, cols = screen.getmaxyx()
        self.lines = lines
        self.cols = cols
        self.codepane = curses.newwin(lines, cols // 2)
        self.stackpane = curses.newwin(lines // 2, cols // 2, 0, cols // 2)
        self.resultpane = curses.newwin(lines // 2, cols // 2, lines // 2, cols // 2)

    def display_code(self):
        self.codepane.border()
        for i, line in enumerate(self.interpreter.board):
            self.codepane.addstr(i + 1, 1, "".join(line))

    def display_stack(self):
        # Clear old stack, to avoid issues when it empties
        blank = " " * (self.cols // 2 - 2)
        for i in range(2, self.lines // 2):
            self.stackpane.addstr(i, 1, blank)

        self.stackpane.border()
        self.stackpane.addstr(1, 1, "Stack:")
        for i, line in islice(
            enumerate(self.interpreter.internal_state()), self.lines // 2 - 3
        ):
            self.stackpane.addstr(i + 2, 1, "".join(line))

    def display_result(self):
        self.resultpane.border()
        self.resultpane.addstr(1, 1, "Result:")
        for i, line in enumerate(self.result.splitlines()):
            self.resultpane.addstr(i + 2, 1, "".join(line))

    def render(self):
        for pos, action, output in self.interpreter:
            key = self.codepane.getch()
            if key == ord("q"):
                break

            if action == Actions.OUTPUT:
                self.result += output

            self.display_stack()
            self.display_result()

            self.display_code()
            self.codepane.move(pos.y + 1, pos.x + 1)

            self.stackpane.refresh()
            self.resultpane.refresh()
            self.codepane.refresh()


def run(interpreter):
    def _run(screen):
        gui = Gui(screen, interpreter)
        gui.render()

    return _run


def main(interpreter):
    curses.wrapper(run(interpreter))
