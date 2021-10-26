import pandas as pd
import altair as alt
import altair_viewer

################################################################################
# Read in the intermediate data set
################################################################################

# Read in data
df = pd.read_csv('sm_data/sm_data.csv', dtype={'house':str})

# Convert date to datetime object
df['date'] = pd.to_datetime(df['date'])

################################################################################
# Create the altair plot
################################################################################

# Define the chart selector to select certain house
selector = alt.selection_single(empty='all', fields=['house'])

# Define a domain and range for color scake
domain2 =['04-1', '04-2','04-3','05-1','05-2','05-3','06-1','06-2','06-3']
range2 = ['#197278','#772E25','#D5B09A','#B388EB','#C44536','#283D3B','#8093F1','#D17B0F', '#1FC3AA']

# Specify a color scale for both plots
color_scale1 = alt.Scale(domain=['04', '05', '06'], range=['#1FC3AA', '#8624F5', '#E96460'])
color_scale2 = alt.Scale(domain=domain2, range=range2)

# Define the base chart and add the selector
base = alt.Chart(df).properties(
    width=600,
    height=400
).add_selection(
    selector
)

# Define object to mark selected records
area = base.mark_area(opacity=0.3).encode(
    x=alt.X('date:T', stack=None, title='Date', axis=alt.Axis(grid=False)),
    y=alt.Y('tot:Q', stack=None, title='Total Power Usage (W)'),
    color=alt.condition(selector,'house:N',alt.value('lightgray'), scale=color_scale1, title='House Number - Power Phase')
).transform_filter(
    selector
).properties(
        
)

# Define the line plot
lines = base.transform_calculate(
    cat="datum.house + '-' +datum.phase_number"
).mark_line().encode(
    x=alt.X('date:T', title='Date', axis=alt.Axis(grid=False)),
    y=alt.Y('phase:Q', title='Phase Power Usage (W)'),
    #color='cat:N'
    color=alt.condition(selector,
                        'cat:N',
                        alt.value('lightgray'),
                        scale=color_scale2)
)


# Combine the area and line plots
plot = area | lines

# Specify fonts and title
plot = plot.properties(
    title='Power Usage of 3 Households'
).configure(
    font='monospace'
).configure_title(
    fontSize = 20,
    font='monospace'
)

# Save the plot
plot.save('altair.html', scale_factor=2.0)
#plot.show()
