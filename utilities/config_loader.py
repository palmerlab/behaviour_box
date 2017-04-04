import ConfigParser         #library used for saving and loading ini files
import os

def write_out_config(params, ID):

    '''
    writes a subset of parameters to an ini file which can then be
    used to recover variable values.
    '''

    write = ( 'mode',
              'lickThres',
              'break_wrongChoice',
              'punish_tone',
              'minlickCount',
              't_noLickPer',
              'timeout',
              't_stimONSET',
              't_rewardDEL',
              't_rewardDUR',
              'audio',
              )
    
    with open('comms.ini','a') as cfgfile:
        Config = ConfigParser.ConfigParser()
        Config.read('comms.ini')

        if ID not in Config.sections():
            Config.add_section(ID)
        for key, value in params.iteritems():
            if key not in write:
                continue
            if type(value) == str:
                Config.set(ID, key, '"%s"' %value)
            else:
                Config.set(ID, key, value)
        Config.write(cfgfile)

def ConfigSectionMap(section, Config):
    '''
    Helper function for reading configuration objects to a dictionary
    '''

    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def restore_old_config(ID):
    '''
    reads the old ini file.
    checks to see if the current ID is in the ini sections
    restores the varible values in the global namespace
    (Hacky solution)
    '''

    if not os.path.exists('comms.ini'):
        return

    with open('comms.ini','r+') as cfgfile:
        Config = ConfigParser.ConfigParser()
        Config.read('comms.ini')

    print Config.sections()
    if ID in Config.sections():
        print 'previous config found for', ID
        exec_string = []
        for name, value in ConfigSectionMap(ID, Config).iteritems():
            print name, ':', value
            exec_string.append('global {name}\n'.format(name = name, value = value) +
                               '{name} = {value}\n'.format(name = name, value = value))
        exec('\n'.join(exec_string))
    else:
        print 'No previous paramaters found'