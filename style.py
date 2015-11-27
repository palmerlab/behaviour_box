import colorama as c


def colour (x, fc = c.Fore.WHITE, bc = c.Back.BLACK, style = c.Style.NORMAL):
    return "%s%s%s%s%s" %(fc, bc, style, x , c.Style.RESET_ALL)
