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

usage = '''bokeh serve
           plot_stats.py ID DATAPATH
'''

#STYLING -------------------------------------------------
# wining, living it up in the city,

left_line = {
    'line_color' : 'red',
    'line_dash' : [4,2],
    'line_width' : 3.5,
    }
left_marker = {
    'fill_color' : 'red',
    'size' : 5,
    }
    
    
    
right_line = {
    'line_color' : 'blue',
    'line_dash' : [4,2],
    'line_width' : 3.5,
    }

right_marker = {
    'fill_color' : 'blue',
    'size' : 5,
    }
    
total_line = {
    'line_color' : 'purple',
    #'line_dash' : [4,2],
    'line_width' : 5,
    }

total_marker = {
    'fill_color' : 'purple',
    'size' : 10,
    }
# --------------------------------------------------------


def today():
    import datetime
    """provides today's date as a string in the form YYMMDD"""
    return datetime.date.today().strftime('%y%m%d')

df = pd.DataFrame([])
df_summary = pd.DataFrame([])


# ## 1. Read the data

ID = sys.argv[1]
bin = sys.argv[2]

DATAPATH = '/'.join(('C:/DATA/Andrew/wavesurfer', today()))

infile = ['/'.join((DATAPATH,f)) for f in os.listdir(DATAPATH) 
                    if ID in f 
                    if f.endswith('.csv')][-1]

first_loop = True
last_mod = time.ctime(os.path.getmtime(infile))

def read_data(df = pd.DataFrame([])):   
    
    if df.empty:
        df = pd.read_csv(infile)
        print df.columns
    else:
        last_line = df['Unnamed: 0'].values[-1]
        df = df.append(pd.read_csv(infile, 
                                   names = df.columns, 
                                   skiprows = last_line))
        
        if df['Unnamed: 0'].values[-1] == last_line:
            return df

    if 'time' in df.columns:
        df = df.drop_duplicates(subset  = 'time')

    if 'OFF[0]' in df.columns:
        df = df.dropna(subset = ['OFF[0]'])

    df['trial_num'] = np.arange(0, df.shape[0])
    df.index = df.trial_num
    df['reward'] = df['WaterPort[0]'] + df['WaterPort[1]']
    
    return df

def update():
    global df
    global last_mod
    global first_loop
    
    
    
    mod_time = time.ctime(os.path.getmtime(infile))
    
    if  (mod_time > last_mod) or first_loop:
        last_mod = mod_time
        
        print mod_time
    else:
        print last_mod, '\r',
        #time.sleep(bin)
        return
    
    df = read_data(df)
    
    df_raw = df.copy()

    # Given the animal did respond:
    # One of the ports will have recorded a count,
    # response = (response on port 0) OR (response on port 1)
    response = (df['count[0]'] > 0).values | (df['count[1]'] > 0).values

    # Lets care only about the ones where the animal made a move
    df = df[response]
    df = df[df.minlickCount > 0]

   reward = df.reward.astype(bool).values
    reward_L = (df.rewardCond == 'L').values
    reward_R = (df.rewardCond == 'R').values
    response_L = (df.response.str.upper() == 'L').values
    response_R = (df.response.str.upper() == 'R').values

    correct = (df.rewardCond == df.response).values
    wrong = (df.rewardCond != df.response).values

    total_trials = np.arange(df_raw.shape[0])

    total_responses = (df_raw.response == '-').values
    total_responses = pd.rolling_mean(total_responses, bin)

    trials = np.arange(df.shape[0])

    trials_L = pd.rolling_sum(reward_L, bin)
    trials_R = pd.rolling_sum(reward_R, bin)

    N_rewards = pd.rolling_sum(reward, bin)
    N_rewards_L = pd.rolling_sum(reward & reward_L, bin)
    N_rewards_R = pd.rolling_sum(reward & reward_R, bin)

    frac = N_rewards / bin
    frac_L = N_rewards_L / trials_L
    frac_R = N_rewards_R / trials_R

    p_correct = pd.rolling_mean(correct, bin)
    p_correct_L = pd.rolling_sum(correct & response_L, bin) / trials_L
    p_correct_R = pd.rolling_sum(correct & response_R, bin) / trials_R

    delta = (( pd.rolling_sum(response_R, bin) 
             - pd.rolling_sum(response_L, bin)) / bin)


    trials_bin = trials[::bin]
             
    #Rendering of the lines ---------------------------------------

    
    p1_resp['line'].data_source.data = {'x' : total_trials[::bin],
                                        'y' : total_responses[::bin]
                                    }
    p1_resp['marker'].data_source.data = {'x' : total_trials[::bin],
                                          'y' : total_responses[::bin]
                                    }
    
    
    p2_frac['tot'].data_source.data = {'x' : trials, 'y' : frac}
    p2_frac['L'  ].data_source.data = {'x' : trials, 'y' : frac_L}
    p2_frac['R'  ].data_source.data = {'x' : trials, 'y' : frac_R}

    p2_frac['marker'].data_source.data = {'x' : trials_bin, 'y' : frac[::bin]}
    p2_frac['Lm'  ].data_source.data = {'x' : trials_bin, 'y' : frac_L[::bin]}
    p2_frac['Rm'  ].data_source.data = {'x' : trials_bin, 'y' : frac_R[::bin]}
    
    
    p3_cor['tot'].data_source.data = {'x': trials, 'y': p_correct}
    p3_cor['L'  ].data_source.data = {'x': trials, 'y': p_correct_L}
    p3_cor['R'  ].data_source.data = {'x': trials, 'y': p_correct_R}
    
    p3_cor['marker'].data_source.data = {'x' : trials_bin, 'y' : p_correct[::bin]}
    p3_cor['Lm'  ].data_source.data = {'x' : trials_bin, 'y' : p_correct_L[::bin]}
    p3_cor['Rm'  ].data_source.data = {'x' : trials_bin, 'y' : p_correct_R[::bin]}
    

    p4_delta['marker'].data_source.data = {'x': trials[::bin], 'y' : delta[::bin]}
    p4_delta['line'].data_source.data = {'x': trials, 'y' : delta}

             
      
##generate_plots##


goodline = Span(location = 0.75, dimension = 'width', line_dash = [1,1], line_color = 'firebrick', line_width = 4)
chanceline = Span(location = 0.5, dimension = 'width', line_dash = [1,1])
u_chanceline = Span(location = -.5, dimension = 'width', line_dash = [4,8])
l_chanceline = Span(location = .5, dimension = 'width', line_dash = [4,8])
z_line = Span(location = 0, dimension = 'width')


##plot 1
p1 = figure(height = 200,
             title='no responses',
             y_range=(-.05,1.05),
             x_axis_label = 'trial',
             y_axis_label = 'fraction'
             )

##plot 2

p2 = figure(title="fraction of trials where reward given",
            y_range=(-.05,1.05),
            x_range = p1.x_range,
            x_axis_label = 'trial',
            y_axis_label = 'fraction'
            )

p3 = figure(title="fraction of trials 'correct'",
                      y_range= p2.y_range,
                      x_range = p1.x_range,
                      x_axis_label = 'trial',
                      y_axis_label = 'fraction'
                     )
                     
p4 = figure(title="BIAS",
                   height = 200,
                      y_range=(-1.05,1.05),
                      x_range = p1.x_range,
                      x_axis_label = 'trial',
                      y_axis_label = 'Delta'
                     )
                     
p2.renderers.extend([u_chanceline, goodline, chanceline])
p3.renderers.extend([u_chanceline, goodline, chanceline])
p4.renderers.extend([u_chanceline, z_line, l_chanceline])

p = gridplot([[p2, p3],
             [p1, p4]])
             
             
df = read_data(df)

df_raw = df.copy()

# Given the animal did respond:
# One of the ports will have recorded a count,
# response = (response on port 0) OR (response on port 1)
response = (df['count[0]'] > 0).values | (df['count[1]'] > 0).values

df = df[response]
df = df[df.minlickCount > 0]

# Lets care only about the ones where the animal made a move

reward = df.reward.astype(bool).values
reward_L = (df.rewardCond == 'L').values
reward_R = (df.rewardCond == 'R').values
response_L = (df.response.str.upper() == 'L').values
response_R = (df.response.str.upper() == 'R').values

correct = (df.rewardCond == df.response).values
wrong = (df.rewardCond != df.response).values

total_trials = np.arange(df_raw.shape[0])

total_responses = (df_raw.response == '-').values
total_responses = pd.rolling_mean(total_responses, bin)

trials = np.arange(df.shape[0])

trials_L = pd.rolling_sum(reward_L, bin)
trials_R = pd.rolling_sum(reward_R, bin)

N_rewards = pd.rolling_sum(reward, bin)
N_rewards_L = pd.rolling_sum(reward & reward_L, bin)
N_rewards_R = pd.rolling_sum(reward & reward_R, bin)

frac = N_rewards / bin
frac_L = N_rewards_L / trials_L
frac_R = N_rewards_R / trials_R

p_correct = pd.rolling_mean(correct, bin)
p_correct_L = pd.rolling_sum(correct & response_L, bin) / trials_L
p_correct_R = pd.rolling_sum(correct & response_R, bin) / trials_R

delta = (( pd.rolling_sum(response_R, bin) 
         - pd.rolling_sum(response_L, bin)) / bin)


trials_bin = trials[::bin]
         


#Initialisation of the lines ---------------------------------------


p1_resp = {
        'line' : p1.line(total_trials[::bin], total_responses[::bin],
                            line_color = 'red', 
                            line_dash = [4,4]
                        ),
                        
        'marker' : p1.circle(p1_X, p1_Y, 
                            fill_color = 'red', 
                        ),
        }    


p2_frac = {
        'tot' : p2.line(trials, frac, **total_line,),
        'L'   : p2.line(trials, frac_L, **left_line,),
        'R'   : p2.line(trials, frac_R, **right_line, ),
                        
        'marker' :  p2.line(trials_bin, frac[::bin],   **total_marker),
        'Lm'     :  p2.line(trials_bin, frac_L[::bin],  **left_marker,),
        'Rm'     :  p2.line(trials_bin, frac_R[::bin], **right_marker,),
        
    }            
    
p3_cor = { 
        'tot': p3.line(trials, p_correct, **total_line),
        'L'  : p3.line(trials, p_correct_L, **left_line,),
        'R'  : p3.line(trials, p_correct_R, **right_line,),
        
        'marker' :  p3.line(trials_bin, p_correct[::bin],   **total_marker),
        'Lm'     :  p3.line(trials_bin, p_correct_L[::bin],  **left_marker,),
        'Rm'     :  p3.line(trials_bin, p_correct_R[::bin], **right_marker,),
    }
    
p4_delta = {
        'marker' : p4.circle(trials[::bin], delta[::bin], size = 10),
        'line'   : p4.line(trials, delta),
    }         
         
         
p4.text(1, 0.5, text = ['Right'], text_color = 'blue')
p4.text(1, -0.5, text = ['Left'], text_color = 'Red')


first_loop = False

#-----------------------------------------------------------------#






# open a session to keep our local document in sync with server
session = push_session(curdoc())
 
curdoc().add_periodic_callback(update, 50)

session.show() # open the document in a browser

session.loop_until_closed() # run forever

