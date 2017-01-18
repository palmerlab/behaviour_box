#plot_stats.py
from __future__ import division
import numpy as np
import pandas as pd
import os
import time

import sys

from bokeh.io import hplot, output_notebook, gridplot
from bokeh.client import push_session
from bokeh.driving import cosine
from bokeh.plotting import figure, curdoc, show
from bokeh.models import Span
from bokeh.charts import Bar

from bokeh.models import HoverTool, BoxSelectTool
TOOLS = [BoxSelectTool(), HoverTool()]

from scipy.stats import norm

def Z(x): 
    return norm.ppf(x)

usage = '''bokeh serve
           plot_stats.py ID DATAPATH
'''



colors = {
    'test' : 'dodgerblue',
    'F2' : 'magenta',
    'F3' : 'magenta',
}

def today():
    import datetime
    """provides today's date as a string in the form YYMMDD"""
    return datetime.date.today().strftime('%y%m%d')

df = pd.DataFrame([])
df_summary = pd.DataFrame([])


# ## 1. Read the data

ID = sys.argv[1]
bin = int(sys.argv[2])

if len(sys.argv) == 4:
    DATAPATH = sys.argv[3]
else:
    DATAPATH = '/'.join((r'R:\Andrew\161222_GOnoGO_Perception_III', today()))

infile = ['/'.join((DATAPATH,f)) for f in os.listdir(DATAPATH) 
                    if ID in f 
                    if f.endswith('.csv')][-1]
                    
#first_loop = True
last_mod = 0

#STYLING -------------------------------------------------
# wining, living it up in the city,

total_line = {
    'line_color' : colors[ID],
    #'line_dash' : [4,2],
    'line_width' : 2,
    }

total_marker = {
    'fill_color' : 'white',
    'line_color' : colors[ID],
    'line_width' : 2,
    'size' : 7.5,
    }
# --------------------------------------------------------

def read_data(df = pd.DataFrame([])):   

    try:
        if df.empty:
            df = pd.read_csv(infile)
        else:
            last_line = df['Unnamed: 0'].values[-1]
            df = df.append(pd.read_csv(infile, 
                                       names = df.columns, 
                                       skiprows = last_line))
            
            if df['Unnamed: 0'].values[-1] == last_line:
                return df, False

        df = df.drop_duplicates()
        df = df.dropna(subset = ['t_stimDUR'])
        df.minlickCount = df.minlickCount.fillna(method = 'ffill')
        #df = df[df.minlickCount > 0]

        #df.loc[df.t_stimDUR == 100, 'trialType'] = 'G'
        #df.loc[df.t_stimDUR != 100, 'trialType'] = 'N'
        
        if 'time' in df.columns:
            df = df.drop_duplicates(subset  = 'time')
        
        date = infile.split('/')[3]
        animal = infile.split('/')[4]

        df['trial_num'] = np.arange(0, df.shape[0])

        return df, True
    except:
        return df, False

def update():
    global df
    global last_mod
    global changed
    
    mod_time = time.ctime(os.path.getmtime(infile))
    
    if  (mod_time > last_mod):
        last_mod = mod_time

        print mod_time, '\r',
    else:
        #print last_mod, '\r',
        time.sleep(1)
        return
        
    df, changed = read_data(df)
    
    
    ###############################################################################
    
    was_operant  = (df.minlickCount < 1).values

    did_respond  = (df['delta'] >= df.minlickCount).values
    was_go_trial = (df.trialType == 'G').values
    was_nogo_trial = (df.trialType == 'N').values
    reward       = df.Water.astype(bool)

    hit  = was_go_trial & did_respond
    miss = was_go_trial & ~did_respond
    FA   = did_respond & was_nogo_trial 
    CR   = ~did_respond & was_nogo_trial 

    N = { 'go'   : was_go_trial.cumsum(), 
          'no go': was_nogo_trial.cumsum(),
        }

    p_hit_go = hit.cumsum() / N['go']
    p_miss_go = miss.cumsum() / N['go']
    p_FA_ngo = FA.cumsum() / N['no go']
    p_CR_ngo = CR.cumsum() / N['no go']

    p_hit_go[p_hit_go == 0]  = 1 / (2*N['go'][p_hit_go == 0])
    p_hit_go[p_hit_go == 1]  = 1 - ( 1 / (2*N['go'][p_hit_go == 1]))
    p_FA_ngo[p_FA_ngo == 0]  = 1 / (2*N['no go'][p_FA_ngo == 0])
    p_FA_ngo[p_FA_ngo == 1]  = 1 - ( 1 / (2*N['no go'][p_FA_ngo == 1]))

    d_prime = [Z(phit) - Z(pFA) for phit, pFA in zip(p_hit_go, p_FA_ngo)]
    d_prime = np.array(d_prime)
    
    correct = hit | CR
    wrong = miss | FA

    trial = np.arange(df.shape[0])

    p_reward = pd.rolling_mean(reward, bin)
    p_response = pd.rolling_mean(did_respond, bin)
    
    p_correct = pd.rolling_mean(correct, bin)
    
    d_prime_col = 'limegreen'# if d else 'red' for d in (d_prime>1.5)]
             
    ###############################################################################
    #Rendering of the lines ---------------------------------------
 
    p1_DPRIME['tot'].data_source.data = {'x' : trial[::bin], 'y' :  d_prime}
    p1_DPRIME['marker'].data_source.data = {'x' : trial[::bin], 'y' :  d_prime, 
                            'fill_color':d_prime_col,
                            'line_color':d_prime_col,
                            }
    
    p2_CORRECT['tot'].data_source.data = {'x': trial, 'y': p_correct}
    p2_CORRECT['marker'].data_source.data = {'x' : trial[::bin], 'y' : p_correct[::bin]}
    
    p3_REWARD['tot'].data_source.data = {'x': trial, 'y' : p_response}
    p3_REWARD['marker'].data_source.data = {'x': trial[::bin], 'y' : p_response[::bin]}
    
    p4_CUMREWARD['tot'].data_source.data = {'x': trial, 'y' : reward.cumsum() * 10}
    p4_CUMREWARD['marker'].data_source.data = {'x': trial[::bin], 'y' : reward.cumsum()[::bin] * 10}
    
    p5_HITS['tot'].data_source.data = {'x': trial, 'y' : p_hit_go}
    p5_HITS['marker'].data_source.data = {'x': trial[::bin], 'y' : p_hit_go[::bin]}
   
    p6_FALSEALARMS['tot'].data_source.data = {'x': trial, 'y' : p_FA_ngo}
    p6_FALSEALARMS['marker'].data_source.data = {'x': trial[::bin], 'y' : p_FA_ngo[::bin]}
    
    print '                               updated:', mod_time, '\r',
    
    #import pdb; pdb.set_trace()

    
##generate_plots## ===========================================================#
#=============================================================================#
## static lines ##

dprime_cutoff = Span(location = 1.5, dimension = 'width', 
                            line_dash = [1,1], 
                            line_color = 'firebrick',
                            line_width = 4
                    )

water_target = Span(location = 1000, dimension = 'width')

##plot 1
# signal detection

p1 = figure(title='signal detection',
                    height = 200,
                    width = 400,
                    y_range = (-2, 2.0),
                    x_axis_label = 'trial (%d bins)' %bin,
                    y_axis_label = 'd`',
                    
            )

##plot 2
p2 = figure(title="fraction 'correct'",
                    height = 200,
                    width = 400,
                    y_range= (-.05, 1.05),
                    x_range = p1.x_range,
                    x_axis_label = 'trial (%d bins)' %bin,
                    y_axis_label = 'fraction',
                    #tools=TOOLS,
            )
 
p3 = figure(title="fraction Responded",
                    height = 200,
                    width = 400,
                    y_range=(-.05,1.05),
                    x_range = p1.x_range,
                    x_axis_label = 'trial (%d bins)' %bin,
                    y_axis_label = 'fraction',
                    #tools=TOOLS,
            )

p4 = figure(title="Cumulative Reward",
                    height = 200,
                    width = 400,
                    x_range = p1.x_range,
                    y_range=(-.05, 1500),
                    x_axis_label = 'trial (%d bins)' %bin,
                    y_axis_label = 'uL',
                   # tools=TOOLS,
            )

p5 = figure(title="Hit ratio",
                    height = 200,
                    width = 400,
                    x_range = p1.x_range,
                    y_range = (0.05, 1.05),
                    x_axis_label = 'trial (%d bins)' %bin,
                    y_axis_label = 'fraction',
                   # tools=TOOLS,
            )

p6 = figure(title="False Alarm ratio",
                    height = 200,
                    width = 400,
                    x_range = p1.x_range,
                    y_range = (0.05, 1.05),
                    x_axis_label = 'trial (%d bins)' %bin,
                    y_axis_label = 'fraction',
                    #tools=TOOLS,
            )

p1.renderers.extend([dprime_cutoff])
p4.renderers.extend([water_target])
p4.add_tools(HoverTool())

p = gridplot([[p1, p2],
              [p3, p4],
              [p5, p6]],
              
              #tools=TOOLS,
            )
#-----------------------------------------------------------------------------#
#=============================================================================#

#Initialisation of the lines ---------------------------------------

p1_DPRIME = {
        'tot' : p1.line([0,0], [0,0],
                            line_color = 'red', 
                            line_dash = [4,4]
                        ),

        'marker' : p1.circle(x = [], y = [], 
                            fill_color = [], 
                            line_color = [], 
                            size = 10,
                        ),
        }


p2_CORRECT = {
        'tot'    : p2.line([0,0], [0,0], **total_line),
        'marker' : p2.circle([0,0], [0,0], **total_marker),
    }

p3_REWARD = { 
        'tot'    : p3.line([0,0], [0,0], **total_line),
        'marker' : p3.circle([0,0], [0,0], **total_marker),
    }

p4_CUMREWARD = {
        'tot'    : p4.line([0,0], [0,0], **total_line),
        'marker' : p4.circle([0,0], [0,0], **total_marker),
    }

p5_HITS = {
        'tot'    : p5.line([0,0], [0,0], **total_line),
        'marker' : p5.circle([0,0], [0,0], **total_marker),
    }

p6_FALSEALARMS = {
        'tot'    : p6.line([0,0], [0,0], **total_line),
        'marker' : p6.circle([0,0], [0,0], **total_marker),
    }

#first_loop = False

###############################################################################

df, changed = read_data(df)

update()

###############################################################################

#-----------------------------------------------------------------#


# open a session to keep our local document in sync with server
session = push_session(curdoc())
 
curdoc().add_periodic_callback(update, 10000)

session.show() # open the document in a browser

session.loop_until_closed() # run forever






