import colorama as color

#TODO Unpack the styling into a more readable format.
sRESET_ALL = color.Style.RESET_ALL
sBRIGHT = color.Style.BRIGHT
sNORMAL = color.Style.NORMAL
sDIM = color.Style.DIM

fRED = color.Fore.RED
fGREEN = color.Fore.GREEN
fBLUE = color.Fore.BLUE
fCYAN = color.Fore.CYAN
fYELLOW = color.Fore.YELLOW
fMAGENTA = color.Fore.MAGENTA
fWHITE = color.Fore.WHITE
fLIGHTBLUE_EX = color.Fore.LIGHTBLUE_EX

bBLACK = color.Back.BLACK
bBLUE = color.Back.BLUE

def colour (s, style = (color.Style.NORMAL,)):
    s_colored = ''.join([st for st in style])
    s_colored = ''.join((s_colored, s, color.Style.RESET_ALL))
    return s_colored