"""
Simple terminal io lib for circuitpython
by BeBoX (c)

Draws text, boxes, colors and progress bars on any ANSI/VT100 compatible
terminal: the REPL shown on a board display (Wio Terminal, PyPortal...) or a
serial console (screen, minicom, Mu, Thonny...).

Coordinates are 0-based: (0, 0) is the top left corner of the screen.
"""

__version__ = "2.0.0"

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
