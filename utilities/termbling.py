def update_progress(progress):

    """
    Prints a wicked progress bar to the screen, 
    with the form
    ` [######                                ] 030% `
    """

    line = '  %s  %3d%%\r' %((' '*50), progress) + \
        '  %s]\r' %(' '*50) + \
        ' [%s\r' %('#'*(progress/2))
    
    print line,
    
    if progress == 100: print "" 