import curses
from enum import IntEnum, auto
from esoteric.interpreter import Actions, coord
from itertools import islice


class Colors(IntEnum):
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    YELLOW = auto()
    BLUE = auto()
    MAGENTA = auto()
    CYAN = auto()
    WHITE = auto()


class Gui:
    def __init__(self, screen, interpreter):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)

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
        colsplit = cols // 2 + cols % 2
        linesplit = lines // 2 + lines % 2
        interpreter.limit = coord(colsplit - 2, lines - 2)
        self.codepane = curses.newwin(lines, colsplit)
        self.stackpane = curses.newwin(linesplit, cols // 2, 0, colsplit)
        self.resultpane = curses.newwin(lines // 2, cols // 2, linesplit, colsplit)

    def display_code(self):
        self.codepane.border()
        for i, line in enumerate(self.interpreter.board):
            for j, c in enumerate(line):
                self.codepane.addch(
                    i + 1,
                    j + 1,
                    c,
                    curses.color_pair(self.interpreter.color_of(coord(j, i))),
                )

    def display_stack(self):
        # Clear old stack, to avoid issues when it empties
        blank = " " * (self.cols // 2 - 2)
        for i in range(2, self.lines // 2):
            self.stackpane.addstr(i, 1, blank)

        self.stackpane.border()
        for i, line in islice(
            enumerate(self.interpreter.internal_state()), self.lines // 2 - 3
        ):
            self.stackpane.addstr(i + 1, 1, "".join(line))

    def display_result(self):
        self.resultpane.border()
        self.resultpane.addstr(1, 1, "Result:", curses.A_BOLD)
        for i, line in enumerate(self.result.splitlines()):
            self.resultpane.addstr(i + 2, 1, "".join(line))

    def render(self):
        for pos, action, output in self.interpreter:
            key = self.codepane.getch()
            if key == ord("q"):
                break

            if action == Actions.OUTPUT:
                self.result += output
            elif action == Actions.ERROR:
                self.resultpane.addstr(1, 1, "An error occurred:", curses.A_BOLD)
                message, error = output
                for i, line in enumerate(message.split("\n")):
                    self.resultpane.addstr(i + 2, 1, line)
                self.resultpane.refresh()
                curses.halfdelay(100)
                self.codepane.getch()
                raise error

            self.display_stack()
            self.display_result()
            self.display_code()

            if (
                0 <= pos.x < self.interpreter.limit.x
                and 0 <= pos.y < self.interpreter.limit.y
            ):
                self.codepane.move(pos.y + 1, pos.x + 1)
            else:
                self.resultpane.addstr(1, 1, "Cursor is out of bounds", curses.A_BOLD)

            self.stackpane.refresh()
            self.resultpane.refresh()
            self.codepane.refresh()
        else:  # On execution end
            self.resultpane.addstr(
                1, 1, "Finished. Press any key or wait 10 seconds.", curses.A_BOLD
            )
            self.resultpane.refresh()
            curses.halfdelay(100)
            self.codepane.getch()


def run(interpreter):
    def _run(screen):
        gui = Gui(screen, interpreter)
        gui.render()

    return _run


def main(interpreter):
    curses.wrapper(run(interpreter))
