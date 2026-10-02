"""termio demo - copy code/lib/termio.py to the lib folder of your board"""
import time
import termio
from termio import cls, printat, rect, fillrect, window, progress, center

WIDTH = 50  # screen width in chars (50 on a Wio Terminal)

termio.cursor(False)
cls()

# plain text, then colored text
printat(5, 1, "TEST")
printat(12, 1, "colors!", fg=termio.YELLOW, style=termio.BOLD)
time.sleep(1)

# rectangle outline using + - |
rect(2, 3, 10, 5)
# rectangle outline made with # and filled with _
fillrect(15, 3, 20, 6, "#", "_")
# filled rectangle with default border, in cyan
fillrect(37, 3, 10, 4, "", ".", fg=termio.CYAN)

# window with a title
window(2, 10, 30, 4, "Status", fg=termio.GREEN)
printat(4, 11, "All systems online")

# progress bar
for i in range(0, 101, 5):
    progress(2, 15, 30, i, fg=termio.GREEN)
    time.sleep(0.1)

center(17, "End", WIDTH, fg=termio.MAGENTA)
termio.cursor(True)
print()
time.sleep(10)
cls()

# --- 2.1: keyboard menu (type in the serial console), text box, table ---
choice = termio.menu(2, 2, ["Show table", "Show text", "Quit"])
cls()
if choice == 0:
    termio.table(2, 2, [["sensor", "value"], ["temp", "21.5C"], ["hum", "40%"]])
elif choice == 1:
    termio.textbox(2, 2, 30, 6, "termio draws text, boxes and menus on the REPL.", "Info")
print()
