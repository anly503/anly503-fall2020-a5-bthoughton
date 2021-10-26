import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.offline import plot

################################################################################
# Read in intermediate data set
################################################################################

# Create list of all plug numbers
plugs = ['0'+str(i) for i in range(1,9)]

# Create empty dic to store data sets
plug_data = {}

# Iterate over the plugs
for plug in plugs:
    
    # Read data and store in dic
    plug_data[plug] = pd.read_csv('plug_data/' + plug + '.csv')

################################################################################
# Create plotly.html
################################################################################

# Create empty list and dic to store frame data and plug data
frames = []
frame_data = {plug:np.array([]) for plug in plugs}
frame_data['x'] = np.array([])

# Define the plug names
plug_names = {
    '01':'Fridge', 
    '02':'Kitchen Appliances', 
    '03':'Lamp', 
    '04':'Stereo and Laptop', 
    '05':'Freezer',
    '06':'Tablet',
    '07':'Entertainement',
    '08':'Microwave'
    }

# Define plug colors
plug_colors ={
    '01':'#197278', 
    '02':'#772E25',
    '03':'#D5B09A', 
    '04':'#B388EB', 
    '05':'#C44536',
    '06':'#283D3B',
    '07':'#8093F1',
    '08':'#D17B0F'
    }


# Iterate over each day in the selected month
for i in range(1,32):

    print('Current Frame: {}'.format(i))
    
    # Add the date (x-axis) to the frame data
    frame_data['x'] = np.append(frame_data['x'], list(plug_data['01'].date[(i-1)*24:i*24]))
    
    # Iterate over all 8 plugs
    for plug in plugs:
        
        # Get the plug data for that frame
        frame_data[plug] = np.append(frame_data[plug], plug_data[plug].power[(i-1)*24:i*24])
    
    # Dfine the frame with data from each plug and the date
    frame = go.Frame(data=[
        go.Scatter(x=frame_data['x'], y=frame_data[plug], stackgroup='one', groupnorm='percent') for plug in plugs
        ])
    
    # Add the frame to the list of frames
    frames.append(frame)

# Define the plot 
fig = go.Figure(
    
    # Define starting point values specify stacked precentage line plot
    data=[
        go.Scatter(x=np.array([plug_data[plug].date[0]]), 
                   y=np.array([plug_data[plug].power[0]]), 
                   name=plug_names[plug],
                   line_color=plug_colors[plug],
                   stackgroup='one',
                   groupnorm='percent'
                   ) for plug in plugs
        ],
    
    # Define the layout with a play button 
    layout={'updatemenus':[
                {'type':'buttons','buttons':[
                    {'label':'Play','method':'animate','args':[None,{'frame':{'duration':1, 
                                                                              'redraw':False},
                                                                'fromcurrent':True,
                                                                #'mode':'immediate',
                                                                'transition':{'duration':0}}]}]}],
            
            # Define the x and y range
            'xaxis':{'range':[datetime.fromisoformat('2012-08-01'), datetime.fromisoformat('2012-08-31')]}#,
            #'yaxis':{'range':[0,3]}
            },
    
    # Pass previously defined frames object which is list of frames for the
    # animation
    frames=frames
    )

# Update titles and fonts
fig.update_layout(title='Which Appliances Use the Most Power?', 
                  xaxis_title='Date', 
                  yaxis_title='Power %',
                  font=dict(family='Anonymous Pro, monospace', size=16))

# Update formatting of x-axis tick marks
fig.update_layout(xaxis_tickformat = '%d %B (%a)<br>%Y')

# Update the plot background color to white
fig.update_layout(plot_bgcolor='#ffffff')

# Update the y axis gridline colors
fig.layout.yaxis.gridcolor='#E8E8E8'

# Update the frame duration and transition time
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 50
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 0

# Save the plot to file and open it
plot(fig, filename='plotly.html', auto_open=True, auto_play=False)


