from termio import cls as cls
from termio import printat as printat
from termio import rect as rect
from termio import fillrect as fillrect
import time
# clear screen
cls()
# set cursor at x=5 and y=4 (from top left of screen) and write TEST
printat(5,4,"TEST")
time.sleep(1)
# Draw a rectangle from x=2, y=2 with 10 chars wide and 5 lines down no specified char for line
rect(2,2,10,5,"")
# Draw a filled rectangle from 15,10 with 20 char wide and 6 lines down lines are made with # and filled with _
fillrect(15,10,20,6,"#","_")
# Draw a filled rectangke with no char specified for line and filled with .
fillrect(30,6,10,4,"",".")
# set cursor at start of line 17 and show End
printat(0,17,"End")
print()
time.sleep(10)
cls()
