"""Run on desktop python: python -m unittest discover tests"""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code", "lib"))
import termio  # noqa: E402

E = "\x1b["


def out(func, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()


def render(func, *args, width=40, height=12, **kwargs):
    """Interpret the cursor moves and return the screen as a list of lines."""
    data = out(func, *args, **kwargs)
    screen = [[" "] * width for _ in range(height)]
    x = y = 0
    i = 0
    while i < len(data):
        if data.startswith(E, i):
            j = i + 2
            while not data[j].isalpha():
                j += 1
            if data[j] == "r":
                i = j + 1
                continue
            if data[j] == "H":
                params = data[i + 2:j]
                if params:
                    row, col = params.split(";")
                    y, x = int(row) - 1, int(col) - 1
                else:
                    x = y = 0
            i = j + 1
            continue
        screen[y][x] = data[i]
        x += 1
        i += 1
    return ["".join(r).rstrip() for r in screen]


class TestTermio(unittest.TestCase):
    def tearDown(self):
        termio.set_offset(0, 0)

    def test_cls_has_no_newline(self):
        self.assertEqual(out(termio.cls), E + "2J" + E + "H")

    def test_printat_zero_based(self):
        self.assertEqual(out(termio.printat, 0, 0, "A"), E + "1;1HA")
        self.assertEqual(out(termio.printat, 4, 2, 42), E + "3;5H42")

    def test_offset(self):
        termio.set_offset(1, 2)
        self.assertEqual(out(termio.printat, 0, 0, "A"), E + "3;2HA")

    def test_colors(self):
        s = out(termio.printat, 0, 0, "A", fg=termio.RED, bg=termio.BRIGHT_BLUE, style=termio.BOLD)
        self.assertEqual(s, E + "1;1H" + E + "1;31;104mA" + E + "0m")

    def test_rect_ascii(self):
        self.assertEqual(render(termio.rect, 1, 1, 4, 3)[:4],
                         ["", " +--+", " |  |", " +--+"])

    def test_rect_legacy_char(self):
        self.assertEqual(render(termio.rect, 0, 0, 3, 3, "#")[:3],
                         ["###", "# #", "###"])

    def test_fillrect_legacy_signature(self):
        self.assertEqual(render(termio.fillrect, 0, 0, 4, 3, "#", "_")[:3],
                         ["####", "#__#", "####"])

    def test_fillrect_default_border(self):
        self.assertEqual(render(termio.fillrect, 0, 0, 4, 3, "", ".")[:3],
                         ["+--+", "|..|", "+--+"])

    def test_box_styles(self):
        self.assertEqual(render(termio.rect, 0, 0, 3, 2, termio.BOX_DOUBLE)[:2],
                         ["╔═╗", "╚═╝"])

    def test_tiny_rects(self):
        self.assertEqual(render(termio.rect, 0, 0, 1, 1)[:1], ["|"])
        self.assertEqual(render(termio.rect, 0, 0, 3, 1)[:1], ["+-+"])
        self.assertEqual(out(termio.rect, 0, 0, 0, 5), "")

    def test_lines(self):
        self.assertEqual(render(termio.hline, 1, 0, 3)[0], " ---")
        self.assertEqual(render(termio.vline, 0, 0, 2)[:3], ["|", "|", ""])

    def test_progress(self):
        self.assertEqual(render(termio.progress, 0, 0, 12, 50)[0], "[#####.....]  50%")
        self.assertEqual(render(termio.progress, 0, 0, 12, 200)[0], "[##########] 100%")
        self.assertEqual(render(termio.progress, 0, 0, 12, 1, 0)[0], "[..........]   0%")

    def test_center(self):
        self.assertEqual(render(termio.center, 0, "ab", 6)[0], "  ab")

    def test_window_title(self):
        self.assertEqual(render(termio.window, 0, 0, 12, 3, "Hi")[:3],
                         ["+- Hi -----+", "|          |", "+----------+"])


    def test_clear_rect(self):
        self.assertEqual(out(termio.clear_rect, 1, 0, 2, 2), E + "1;2H  " + E + "2;2H  ")

    def test_scroll_region(self):
        self.assertEqual(out(termio.scroll_region, 2, 9), E + "3;10r")
        self.assertEqual(out(termio.scroll_region), E + "r")

    def test_wrap(self):
        self.assertEqual(termio.wrap("the quick brown fox", 10), ["the quick", "brown fox"])
        self.assertEqual(termio.wrap("abcdefghij", 4), ["abcd", "efgh", "ij"])
        self.assertEqual(termio.wrap("a\nb", 4), ["a", "b"])

    def test_textbox(self):
        self.assertEqual(render(termio.textbox, 0, 0, 10, 4, "hello big world")[:4],
                         ["+--------+", "|hello   |", "|big     |", "+--------+"])

    def test_table(self):
        lines = render(termio.table, 0, 0, [["id", "name"], [1, "Bob"]])[:5]
        self.assertEqual(lines, ["+----+------+", "| id | name |", "+----+------+",
                                 "| 1  | Bob  |", "+----+------+"])

    def test_spinner(self):
        self.assertEqual(render(termio.spinner, 0, 0, 5)[0], "/")


class TestInput(unittest.TestCase):
    def feed(self, text):
        old = sys.stdin
        sys.stdin = io.StringIO(text)
        self.addCleanup(setattr, sys, "stdin", old)

    def test_getkey(self):
        self.feed("a\x1b[A\x1b[B\r\x7f")
        keys = [termio.getkey() for _ in range(6)]
        self.assertEqual(keys, ["a", termio.UP, termio.DOWN, termio.ENTER,
                                termio.BACKSPACE, None])

    def test_menu_choose(self):
        # down x3 wraps back to "a", up wraps to "c"
        self.feed("\x1b[B\x1b[B\x1b[B\x1b[A\r")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(termio.menu(0, 0, ["a", "b", "c"]), 2)

    def test_menu_wraps_and_escape(self):
        self.feed("\x1b[Aq")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertIsNone(termio.menu(0, 0, ["a", "b", "c"]))
        self.assertTrue(buf.getvalue().endswith(E + "?25h"))


if __name__ == "__main__":
    unittest.main()
