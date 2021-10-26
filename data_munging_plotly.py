import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from time import process_time
import plotly.graph_objects as go
from plotly.offline import plot

################################################################################
# Get file paths of all data sets
################################################################################

# Define the base path to the data
base_path = Path('eco')

# Create list of all plug numbers
plugs = ['0'+str(i) for i in range(1,9)]

# Create list of all house numbers
houses = ['0'+str(i) for i in range(4,7)]

# Instantiate dic of dic of empty lists to store the plugs datasets file paths
plug_paths = {h:{p:[] for p in plugs} for h in houses}

# Instantiate empty list to store the sm datasets file paths
sm_paths = []

# Recursively iterate over the base directory 
for file in base_path.rglob('*'):
    
    # Check if the path is a csv file
    if os.path.isfile(file) and '.csv' in str(file) and ' ' not in str(file):
        
        # Check if plugs dataset and month of August
        if 'plugs' in str(file) and '-08-' in str(file):
            
            # Get the plug number of the file
            plug_num = file.parents[0].name
            
            # Get the house numver of the file
            house_num = file.parents[1].name
            
            # Add file path to plugs datasets dic
            plug_paths[house_num][plug_num].append(file)
        
        # Check if smart meter dataset
        elif 'sm' in str(file):
            # Add file path to smart meter datasets list
            sm_paths.append(str(file))
        
        
################################################################################
# Read in the plugs datasets
################################################################################

# Define a function to read in the dataset, create a datetime feature,
# ....................
def read_plug_data(path):
    
    # Get the date from the file path and split out file extension
    date = path.name.split('.')[0]
    
    # Convert to datetime object
    date = datetime.fromisoformat(date)
    
    # Get the day of week
    #week_day = date.weekday()
    
    # Create list of all datetimes in dataset
    date_col = [date + timedelta(seconds=i) for i in range(0, 86400)]
    
    # Get the plug number
    plug_num = int(path.parents[0].name)
    
    # Get the house number
    house_num = int(path.parents[1].name)
    
    # Create the dataframe with the date feature
    df = pd.DataFrame(data={'date':date_col})
    
    # Create hour feature
    df['hour'] = df.date.apply(lambda x: x.hour)

    
    # Read in the plug dataset indicate -1 as missing values
    df['power'] = pd.read_csv(path, na_values=(-1), header=None)
    
    # Fill missing power values with the nearest values
    df['power'] = df['power'].interpolate(method='nearest')
    
    #df['power'] = df['power'].fillna(method='ffill')
    
    # Take the aggreagrated mean of each min thorughout the data to reduce the
    # complexity of the data
    df = df.groupby(['hour']).agg('mean').reset_index()
    
    # Add plug and house number to data frame
    df['house'] = house_num
    df['plug'] = plug_num
    
    # Recreate a new date column
    df['date'] = df.apply(lambda x: date + timedelta(hours = x.hour), axis=1)
    
    # Select the desired features and re-order columns
    df = df[['date', 'hour', 'house', 'plug', 'power']]
    
    return df


# Define a function to combine datasets of the same house number and plug number
def combine_plug_data(house_num, plug_num):
    
    # Get all paths of given house and plug number
    paths = plug_paths[house_num][plug_num]
    
    # Instantiate empty dataframe
    df = pd.DataFrame()
    
    # Iterate over all paths
    for path in paths:
        
        print('Processing dataset: {}'.format(path.parents[1].name+'/'+path.parents[0].name+'/'+path.name))
        
        # Read in the dataset
        temp = read_plug_data(path)
    
        # Add the dataset to the dataframe
        df = pd.concat([df, temp])
        
        print('New length of df: {}'.format(len(df)))
    
    # Reset the index and select desried features
    df = df.reset_index()
    df = df[['date', 'hour', 'house', 'plug', 'power']]
    
    return df
    
# Create empty dic to store the data
plug_data = {}

start = process_time()

# Iterate over all 8 plugs
for plug in plugs:
    
    print('Combining plug: {}'.format(plug))
    
    # Read in data and store in dic
    plug_data[plug] = combine_plug_data('04', plug)

stop = process_time()

print("Elapsed time during the whole program in seconds:", stop - start) 


# Write intermediate datasets to file
for plug,df in plug_data.items():
    df.to_csv('plug_data/'+plug+'.csv', index=False)


