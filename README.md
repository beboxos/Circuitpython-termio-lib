# Circuitpython-termio-lib
a simple REPL display lib for circuitpython
![img](images/img1.png)
# Fonctions

## cls
clear terminal screen and set cursor on top left : coords 0,0

usage :

from termio import cls as cls<br/>
cls()

## printat
set cursor position and print 

syntax : printat(x,y,value)

coords start from top left and depend on you display size. 

example on wio terminal 50 chars wide on 20 lines
then x is between 0 and 49 
and lines are from 0 to 19 (on wio terminal it's strange display line start on 2 , then think to add a 2 offset on your code)

usage :

from termio import printat as printat<br/>
printat(5,10,"Hello World!")<br/>

## rect
draw a rectangle with char (if empty char , make rectangle with  + - and  )

syntax : rect(x,y,width,height,char)

draw a rectangle from x,y with width chars wide and height line down

usage : 

from termio import rect as rect<br/>
rect(5,4,20,5,"")<br/>

## fillrect
draw a rectangle with char (if empty char , make rectangle with  + - and  )

syntax : fillrect(x,y,width,height,char,fillchar)

draw a filled rectangle from x,y with width chars wide and height line down and filled with a char

usage : 

from termio import fillrect as fillrect<br/>
rect(5,4,20,5,"#","O")<br/>
