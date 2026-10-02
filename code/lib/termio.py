"""
Simple terminal io lib for circuitpython
by BeBoX (c)

Draws text, boxes, colors and progress bars on any ANSI/VT100 compatible
terminal: the REPL shown on a board display (Wio Terminal, PyPortal...) or a
serial console (screen, minicom, Mu, Thonny...).

Coordinates are 0-based: (0, 0) is the top left corner of the screen.
"""

__version__ = "2.1.0"

import sys

ESC = "\x1b["

# Colors (use with color(), printat(..., fg=, bg=) etc.)
BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
# Bright variants
BRIGHT_BLACK = 8
BRIGHT_RED = 9
BRIGHT_GREEN = 10
BRIGHT_YELLOW = 11
BRIGHT_BLUE = 12
BRIGHT_MAGENTA = 13
BRIGHT_CYAN = 14
BRIGHT_WHITE = 15

# Text styles
RESET = 0
BOLD = 1
DIM = 2
UNDERLINE = 4
BLINK = 5
REVERSE = 7

# Box styles: (top-left, top-right, bottom-left, bottom-right, horizontal, vertical)
BOX_ASCII = ("+", "+", "+", "+", "-", "|")
BOX_SINGLE = ("┌", "┐", "└", "┘", "─", "│")
BOX_DOUBLE = ("╔", "╗", "╚", "╝", "═", "║")
BOX_ROUND = ("╭", "╮", "╰", "╯", "─", "│")

# Keys returned by getkey()
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
ENTER = "enter"
ESCAPE = "esc"
BACKSPACE = "backspace"
_KEYS = {"A": UP, "B": DOWN, "C": RIGHT, "D": LEFT}

SPINNER = "|/-\\"

# Offset added to every coordinate (see set_offset())
_offset_x = 0
_offset_y = 0


def _write(text):
    print(text, end="")


def _goto(x, y):
    # ANSI positions are 1-based, ours are 0-based
    return "{}{};{}H".format(ESC, y + _offset_y + 1, x + _offset_x + 1)


def _sgr(fg=None, bg=None, style=None):
    """Return the escape sequence selecting colors / style ("" if nothing)."""
    codes = []
    if style is not None:
        codes.append(str(style))
    if fg is not None:
        codes.append(str(30 + fg if fg < 8 else 90 + fg - 8))
    if bg is not None:
        codes.append(str(40 + bg if bg < 8 else 100 + bg - 8))
    if not codes:
        return ""
    return ESC + ";".join(codes) + "m"


def _styled(text, fg, bg, style):
    sgr = _sgr(fg, bg, style)
    if sgr:
        return sgr + text + ESC + "0m"
    return text


def set_offset(x=0, y=0):
    """Shift every drawing by (x, y).

    Useful on displays where the first lines are hidden or used by the
    status bar, e.g. set_offset(0, 1) on a Wio Terminal.
    """
    global _offset_x, _offset_y
    _offset_x = x
    _offset_y = y


# ---------------------------------------------------------------- screen ---

def cls():
    """Clear the screen and move the cursor to the top left corner."""
    _write(ESC + "2J" + ESC + "H")


def home():
    """Move the cursor to the top left corner without clearing."""
    _write(ESC + "H")


def clear_line(y=None):
    """Clear a whole line (the current one if y is None)."""
    if y is None:
        _write(ESC + "2K")
    else:
        _write(_goto(0, y) + ESC + "2K")


def clear_rect(x, y, width, height):
    """Blank a rectangular area."""
    if width > 0:
        _write("".join(_goto(x, y + n) + " " * width for n in range(height)))


def scroll_region(top=None, bottom=None):
    """Only scroll lines top..bottom (inclusive), e.g. to keep a fixed header.

    Call without arguments to scroll the whole screen again.
    """
    if top is None:
        _write(ESC + "r")
    else:
        _write("{}{};{}r".format(ESC, top + _offset_y + 1, bottom + _offset_y + 1))


def clear_eol():
    """Clear from the cursor to the end of the line."""
    _write(ESC + "K")


# ---------------------------------------------------------------- cursor ---

def goto(x, y):
    """Move the cursor to column x, line y."""
    _write(_goto(x, y))


def cursor(visible=True):
    """Show or hide the cursor."""
    _write(ESC + ("?25h" if visible else "?25l"))


def save_cursor():
    _write("\x1b7")


def restore_cursor():
    _write("\x1b8")


# ------------------------------------------------------------------ text ---

def color(fg=None, bg=None, style=None):
    """Set colors / style for everything printed afterwards."""
    _write(_sgr(fg, bg, style))


def reset():
    """Restore default colors and style."""
    _write(ESC + "0m")


def printat(x, y, text, fg=None, bg=None, style=None):
    """Print text at column x, line y, optionally colored."""
    _write(_goto(x, y) + _styled(str(text), fg, bg, style))


def center(y, text, width, fg=None, bg=None, style=None):
    """Print text centered on line y for a screen `width` chars wide."""
    text = str(text)
    printat(max(0, (width - len(text)) // 2), y, text, fg, bg, style)


def wrap(text, width):
    """Split text into lines of at most `width` chars, breaking on spaces."""
    lines = []
    for paragraph in str(text).split("\n"):
        line = ""
        for word in paragraph.split(" "):
            while len(word) > width:
                if line:
                    lines.append(line)
                    line = ""
                lines.append(word[:width])
                word = word[width:]
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= width:
                line += " " + word
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def textat(x, y, text, width, height=None, fg=None, bg=None, style=None):
    """Print text word-wrapped in a `width` wide column, return lines used."""
    lines = wrap(text, width)
    if height is not None:
        lines = lines[:height]
    for n, line in enumerate(lines):
        printat(x, y + n, line, fg, bg, style)
    return len(lines)


# --------------------------------------------------------------- drawing ---

def hline(x, y, length, char="-", fg=None, bg=None):
    """Draw a horizontal line of `length` chars."""
    if length > 0:
        printat(x, y, char * length, fg, bg)


def vline(x, y, length, char="|", fg=None, bg=None):
    """Draw a vertical line of `length` chars."""
    if length > 0:
        piece = _styled(char, fg, bg, None)
        _write("".join(_goto(x, y + n) + piece for n in range(length)))


def _box(x, y, width, height, char, fillchar, fg, bg, style):
    if width < 1 or height < 1:
        return
    if isinstance(char, tuple):
        tl, tr, bl, br, h, v = char
    elif char:
        tl = tr = bl = br = h = v = char
    else:
        tl, tr, bl, br, h, v = BOX_ASCII
    if width == 1:
        tl = tr = bl = br = v
    if height == 1:
        bl, br = tl, tr

    def line(left, mid, right):
        if width == 1:
            return left
        return left + mid * (width - 2) + right

    out = [_goto(x, y) + _styled(line(tl, h, tr), fg, bg, style)]
    side = _styled(v, fg, bg, style)
    for n in range(1, height - 1):
        if fillchar is not None and width > 2:
            out.append(_goto(x, y + n) + side + fillchar * (width - 2) + side)
        else:
            out.append(_goto(x, y + n) + side)
            if width > 1:
                out.append(_goto(x + width - 1, y + n) + side)
    if height > 1:
        out.append(_goto(x, y + height - 1) + _styled(line(bl, h, br), fg, bg, style))
    _write("".join(out))


def rect(x, y, width, height, char="", fg=None, bg=None, style=None):
    """Draw a rectangle outline.

    char can be "" (ASCII + - |), a single char used everywhere, or one of
    the BOX_* styles (BOX_SINGLE, BOX_DOUBLE, BOX_ROUND...).
    """
    _box(x, y, width, height, char, None, fg, bg, style)


def fillrect(x, y, width, height, char="", fillchar=" ", fg=None, bg=None, style=None):
    """Draw a rectangle outline filled with fillchar."""
    _box(x, y, width, height, char, fillchar, fg, bg, style)


def window(x, y, width, height, title="", char=BOX_ASCII, fg=None, bg=None):
    """Draw an empty box with an optional title on its top border."""
    fillrect(x, y, width, height, char, " ", fg, bg)
    if title and width > 4:
        title = " " + str(title)[: width - 4] + " "
        printat(x + 2, y, title, fg, bg, BOLD)


def progress(x, y, width, value, maximum=100, fg=None, bg=None, full="#", empty="."):
    """Draw a progress bar [####....] width chars wide, followed by a %."""
    inner = width - 2
    if inner < 1:
        return
    if maximum <= 0:
        ratio = 0
    else:
        ratio = min(max(value / maximum, 0), 1)
    done = int(inner * ratio + 0.5)
    bar = "[" + _styled(full * done, fg, bg, None) + empty * (inner - done) + "]"
    _write(_goto(x, y) + bar + " {:3d}%".format(int(ratio * 100 + 0.5)))


def textbox(x, y, width, height, text, title="", char=BOX_ASCII, fg=None, bg=None):
    """Draw a window and fill it with word-wrapped text (cut if too long)."""
    window(x, y, width, height, title, char, fg, bg)
    if width > 2 and height > 2:
        textat(x + 1, y + 1, text, width - 2, height - 2)


def spinner(x, y, step, fg=None):
    """Draw one frame of a | / - \\ spinner; call again with step + 1."""
    printat(x, y, SPINNER[step % len(SPINNER)], fg)


def table(x, y, rows, widths=None, header=True, fg=None):
    """Draw rows (lists of values) as an ASCII table, return its height.

    widths defaults to the widest value of each column.
    With header=True a separator is drawn under the first row.
    """
    rows = [[str(cell) for cell in row] for row in rows]
    if not rows:
        return 0
    if widths is None:
        widths = [0] * max(len(row) for row in rows)
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))
    sep = _styled("+" + "+".join("-" * (w + 2) for w in widths) + "+", fg, None, None)
    bar = _styled("|", fg, None, None)
    out = [sep]
    for n, row in enumerate(rows):
        cells = []
        for i, w in enumerate(widths):
            cell = row[i] if i < len(row) else ""
            cells.append(" " + cell[:w] + " " * (w - len(cell[:w])) + " ")
        out.append(bar + bar.join(cells) + bar)
        if n == 0 and header and len(rows) > 1:
            out.append(sep)
    out.append(sep)
    _write("".join(_goto(x, y + n) + line for n, line in enumerate(out)))
    return len(out)


# ----------------------------------------------------------------- input ---

def _available():
    try:
        import supervisor
    except ImportError:
        return True
    return supervisor.runtime.serial_bytes_available


def getkey(blocking=True):
    """Read one key from the serial console.

    Returns the char typed, or UP, DOWN, LEFT, RIGHT, ENTER, ESCAPE,
    BACKSPACE. With blocking=False, returns None when no key is waiting.
    Only works over USB serial (not with a keyboard attached to the board).
    """
    if not blocking and not _available():
        return None
    c = sys.stdin.read(1)
    if not c:
        return None
    if c == "\x1b":
        if not _available():
            return ESCAPE
        c = sys.stdin.read(1)
        if c in "[O":
            c = sys.stdin.read(1)
            return _KEYS.get(c, c)
        return ESCAPE
    if c in "\r\n":
        return ENTER
    if c in "\x08\x7f":
        return BACKSPACE
    return c


def menu(x, y, items, selected=0, fg=None, bg=None):
    """Show a vertical menu driven by the arrow keys.

    Returns the index of the item chosen with Enter, or None on Escape / q.
    """
    if not items:
        return None
    width = max(len(str(item)) for item in items) + 2
    selected = min(max(selected, 0), len(items) - 1)
    cursor(False)
    try:
        while True:
            for n, item in enumerate(items):
                text = " " + str(item) + " " * (width - 1 - len(str(item)))
                printat(x, y + n, text, fg, bg, REVERSE if n == selected else None)
            key = getkey()
            if key == UP:
                selected = (selected - 1) % len(items)
            elif key == DOWN:
                selected = (selected + 1) % len(items)
            elif key == ENTER:
                return selected
            elif key in (ESCAPE, "q"):
                return None
    finally:
        cursor(True)


def input_at(x, y, prompt="", fg=None, bg=None, style=None):
    """Print prompt at x, y and return the line typed by the user."""
    printat(x, y, prompt, fg, bg, style)
    return input()
