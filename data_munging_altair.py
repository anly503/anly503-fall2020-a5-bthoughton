import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import re


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
sm_paths = {h:[] for h in houses}

# Compile regex expression to extract the month
month_re = re.compile('(?<=-).*(?=-)')

# Recursively iterate over the base directory 
for file in base_path.rglob('*'):
    
    # Check if the path is a csv file
    if os.path.isfile(file) and '.csv' in str(file) and ' ' not in str(file):
        
        # Get the month from the file name
        month = month_re.search(file.name)[0]
    
        # Check if plugs dataset and month of August
        if 'plugs' in str(file) and '-08-' in str(file):
            
            # Get the plug number of the file
            plug_num = file.parents[0].name
            
            # Get the house numver of the file
            house_num = file.parents[1].name
            
            # Add file path to plugs datasets dic
            plug_paths[house_num][plug_num].append(file)
        
        # Check if smart meter dataset
        elif 'sm' in str(file) and month in ['06', '07', '08', '09', '10']:
            
            # Get the house number of the file
            house_num = file.parent.name
            
            # Add file path to smart meter datasets list
            sm_paths[house_num].append(file)


################################################################################
# Read in the smart meter datasets
################################################################################

# Define a function to read in the dataset, create a datetime feature,
# ....................
def read_sm_data(path):
    
    # Get the date from the file path and split out file extension
    date = path.name.split('.')[0]
    
    # Convert to datetime object
    date = datetime.fromisoformat(date)
    
    # Get the day of week
    #week_day = date.weekday()
    
    # Create list of all datetimes in dataset
    date_col = [date + timedelta(seconds=i) for i in range(0, 86400)]
    
    # Get the house number
    house_num = str(path.parent.name)
    
    # Read in the plug dataset indicate -1 as missing values
    df = pd.read_csv(path, na_values=(-1), header=None)
    
    # Add date feature to the dataframe
    df['date'] = date_col
    
    # Create the dataframe with the date feature
    #df = pd.DataFrame(data={'date':date_col})
    
    # Create hour feature
    df['day'] = df.date.apply(lambda x: x.day)

    
    # Change the name of all 3 power phases
    df = df.rename(columns={0:'tot', 1:'phase1', 2:'phase2',3:'phase3'})
    
    # Fill missing power values with the nearest values
    df = df.interpolate(method='ffill')
    
    # Take the aggreagrated mean of each min thorughout the data to reduce the
    # complexity of the data
    df = df.groupby(['day']).agg('mean').reset_index()
    
    # Recreate a new date column
    df['date'] = date
    
    # Add plug and house number to data frame
    df['house'] = house_num
    
    # Select the desired features and re-order columns
    df = df[['date', 'day', 'house', 'tot', 'phase1', 'phase2', 'phase3']]
    
    return df


test1 = read_sm_data(sm_paths['04'][0])

# Define a function to combine datasets of the same house number and plug number
def combine_plug_data(house_num):
    
    # Get all paths of given house and plug number
    paths = sm_paths[house_num]
    
    # Instantiate empty dataframe
    df = pd.DataFrame()
    
    # Iterate over all paths
    for path in paths:
        
        print('Processing dataset: {}'.format(path.parent.name+'/'+path.name))
        
        # Read in the dataset
        temp = read_sm_data(path)
    
        # Add the dataset to the dataframe
        df = pd.concat([df, temp])
        
        print('New length of df: {}'.format(len(df)))
    
    # Reset the index and select desried features
    df = df.reset_index()
    df = df[['date', 'house', 'tot', 'phase1', 'phase2', 'phase3']]
    
    return df


# Create empty data frame to store the data of all 3 houses
df = pd.DataFrame()

# Iterate over the 3 houses
for house in houses:
    
    print('Processing House {}'.format(house))
    
    # Read in the data for the house and combine into data frame of all 3 houses
    df = pd.concat([df, combine_plug_data(house)])


# Pivot data to long format
dfl = pd.wide_to_long(df, stubnames='phase', i=['house', 'date', 'tot'], j='phase_number')

# Reset index, altair will not work with hierarchical inidices
dfl = dfl.reset_index()

# Write the data set to file
dfl.to_csv('sm_data/sm_data.csv', index=False)