#plot_stats.py
from __future__ import division
import numpy as np
import pandas as pd
import os
import time

import sys

#sys.path.append('D:/GoogleDrive/02 PROTOCOLS/Python')
from utilitybelt.numerical import downsample

from bokeh.io import hplot, output_notebook, gridplot
from bokeh.client import push_session
from bokeh.driving import cosine
from bokeh.plotting import figure, curdoc, show
from bokeh.models import Span
from bokeh.charts import Bar

output_notebook()
usage = '''bokeh serve
           plot_stats.py ID DATAPATH
'''

df = pd.DataFrame([])
df_summary = pd.DataFrame([])


# ## 1. Read the data

ID = sys.argv[1]
DATAPATH = sys.argv[2]
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
        time.sleep(10)
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

    #compute the values:

    total_trials = np.arange(df_raw.shape[0])
    total_responses = (df_raw.response == '-').values

    total_trials = np.arange(0,total_trials.shape[0], 10) 

    total_responses = downsample(total_responses, 10, np.nansum)/10


    trials = np.arange(df.shape[0])
    trials = downsample(trials, 10, np.nanmax)

    trials_L = downsample(reward_L, 10, np.nansum)
    trials_R = downsample(reward_R, 10, np.nansum)

    N_rewards = downsample(reward, 10, np.nansum)
    N_rewards_L = downsample(reward & reward_L, 10, np.nansum)
    N_rewards_R = downsample(reward & reward_R, 10, np.nansum)

    frac = N_rewards / 10
    frac_L = N_rewards_L / trials_L
    frac_R = N_rewards_R / trials_R

    p_correct = downsample(correct, 10, np.nansum) / 10
    p_correct_L = downsample(correct & response_L, 10, np.nansum) / trials_L
    p_correct_R = downsample(correct & response_R, 10, np.nansum) / trials_R

    delta = (( downsample(response_R, 10, np.nansum) 
             - downsample(response_L, 10, np.nansum)) / 10)


    p1_responses.data_source.data = {'x' : total_trials,
                                    'y' : total_responses
                                    }
    
    p2_frac.data_source.data = {'x' : trials,
                                'y' : frac}
    
    p2_frac_L.data_source.data = {'x' : trials,
                                 'y' : frac_L
                                 }
    
    p2_frac_R.data_source.data = {'x': trials,
                                  'y': frac_R
                                 }
    
    
    p3_cor.data_source.data = { 'x': trials,
                                'y': p_correct
                              }
    
    p3_cor_L.data_source.data = {'x' : trials,
                                 'y' : p_correct_L
                                }
    
    p3_cor_R.data_source.data =  {'x' :trials,
                               'y' :p_correct_R
                               }
    
    
    p4_delta.data_source.data = {'x': trials,
                                 'y' : delta
                                 }

    p4_deltam.data_source.data = {'x' :trials,
                                  'y' :delta
                                  }
    
        
        
             
if first_loop:             
    ##generate_plots##
    
    
    goodline = Span(location = 0.75, dimension = 'width', line_dash = [1,1], line_color = 'tomato', line_width = 2)
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

    #compute the values:

    total_trials = np.arange(df_raw.shape[0])
    total_responses = (df_raw.response == '-').values

    total_trials = np.arange(0,total_trials.shape[0], 10) 

    total_responses = downsample(total_responses, 10, np.nansum)/10


    trials = np.arange(df.shape[0])
    trials = downsample(trials, 10, np.nanmax)

    trials_L = downsample(reward_L, 10, np.nansum)
    trials_R = downsample(reward_R, 10, np.nansum)

    N_rewards = downsample(reward, 10, np.nansum)
    N_rewards_L = downsample(reward & reward_L, 10, np.nansum)
    N_rewards_R = downsample(reward & reward_R, 10, np.nansum)

    frac = N_rewards / 10
    frac_L = N_rewards_L / trials_L
    frac_R = N_rewards_R / trials_R

    p_correct = downsample(correct, 10, np.nansum) / 10
    p_correct_L = downsample(correct & response_L, 10, np.nansum) / trials_L
    p_correct_R = downsample(correct & response_R, 10, np.nansum) / trials_R

    delta = (( downsample(response_R, 10, np.nansum) 
             - downsample(response_L, 10, np.nansum)) / 10)

    if first_loop:
    
        p1_responses = p1.line(total_trials, total_responses, 
                            line_color = 'red', 
                            line_dash = [4,4])
                    
        p2_frac = p2.line(trials, frac, line_color = 'black', line_width = 5)
        p2_frac_L = p2.line(trials, frac_L, line_color = 'red', line_dash = [4,1,2,1])
        p2_frac_R = p2.line(trials, frac_R, line_color = 'blue', line_dash = [4,1,2,1])

        p3_cor = p3.line(trials, p_correct, line_color = 'black', line_width = 5)
        p3_cor_L = p3.line(trials, p_correct_L, line_color = 'red', line_dash = [4,1,2,1])
        p3_cor_R = p3.line(trials, p_correct_R, line_color = 'blue', line_dash = [4,1,2,1])

        p4_deltam = p4.circle(trials, delta, size = 4)
        p4_delta = p4.line(trials, delta)

        p4.text(1, 0.5, text = ['Right'], text_color = 'blue')
        p4.text(1, -0.5, text = ['Left'], text_color = 'Red')
     
        print "I drew the things"
        first_loop = False

#-----------------------------------------------------------------#

# open a session to keep our local document in sync with server
session = push_session(curdoc())
 
curdoc().add_periodic_callback(update, 50)

session.show() # open the document in a browser

session.loop_until_closed() # run forever

