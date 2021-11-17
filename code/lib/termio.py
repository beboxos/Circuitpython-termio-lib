"""
Simple terminal io lib for circuitpython
by BeBoX (c)
"""

def cls():
    print(chr(27)+"[2J")
    
def printat(x,y,text):
    print(chr(27)+"["+str(y)+";"+str(x)+"H", end="")
    print(text, end="")

def rect(x,y,width,height,char):
    if char == "":
        printat(x,y,"+"+"-"*(width-2)+"+")
    else:
        printat(x,y,char*width)
    for n in range(1,(height-1)):
        if char == "":
            printat(x,y+n,"|")
            printat(x+(width-1),y+n,"|")            
        else:
            printat(x,y+n,char)
            printat(x+(width-1),y+n,char)
    if char == "":
        printat(x,y+(height-1),"+"+"-"*(width-2)+"+")
    else:
        printat(x,y+(height-1),char*width)

def fillrect(x,y,width,height,char,fillchar):
    if char == "":
        printat(x,y,"+"+"-"*(width-2)+"+")
    else:
        printat(x,y,char*width)
    for n in range(1,(height-1)):
        if char == "":
            printat(x,y+n,"|")
            printat(x+1,y+n,fillchar*(width-2))
            printat(x+(width-1),y+n,"|")
        else:
            printat(x,y+n,char)
            printat(x+1,y+n,fillchar*(width-2))
            printat(x+(width-1),y+n,char)
    if char == "":
        printat(x,y+(height-1),"+"+"-"*(width-2)+"+")
    else:
        printat(x,y+(height-1),char*width)
    
