import pandas as pd
from datetime import datetime
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os

# check if database/csv is exits
def csv_exists(filename):
    """Check if the given CSV file exists."""
    return os.path.exists(filename)

# Load and preprocess data
def load_data(filename):
    if csv_exists(filename):
        daa = pd.read_csv(filename, parse_dates=['ACCIDENT_DATE'])
        return daa.copy()
    else:
        print(f"Error: The file '{filename}' does not exist.")
        return pd.DataFrame()  # Return an empty DataFrame

# Extract accident dates
def extract_accident_dates(data):
    return [i for i in data['ACCIDENT_DATE']]

# Sort accident dates
def sort_dates(listi):
    return sorted(listi, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))

# Preprocess data

def preprocess_data(sorted_dates):
    listi = extract_accident_dates(sorted_dates)
    list_i = sort_dates(listi)
    list_x = [list_i[0]]
    list_y = [round(listi.count(list_i[0]) / 24, 2)]
    for i in range(1, len(list_i)):
        if list_i[i] != list_i[i - 1]:
            list_x.append(list_i[i])
            list_y.append(round(list_i.count(list_i[i]) / 24, 2))
    return list_x, list_y

data = load_data('Crash Statistics Victoria.csv')
list_x, list_y = preprocess_data(data)

# Chart generation functions
def generate_bar_chart(selected_dates, filtered_data):

    list_i = sorted(filtered_data['ACCIDENT_DATE'], key=lambda x: datetime.strptime(x, '%d/%m/%Y'))

    list_y = [round(list_i.count(date) / 24, 2) for date in selected_dates]
    trace = go.Bar(
        x=selected_dates,
        y=list_y,
        name="citations",
        marker=dict(color='rgba(255, 174, 255, 0.5)',
                    line=dict(color='rgb(0, 0, 0)', width=1.5)),
        text=list_y
    )
    layout = go.Layout(
        barmode="group",
        title="The Number Of Accidents Per Hour",
        xaxis=dict(rangeslider_visible=True)
    )
    return go.Figure(data=[trace], layout=layout)

def generate_table_analysis(selected_dates, filtered_data):
    account_data = []
    table_data = []
    for date, SEVERITY, NODE_TYPE, collision_vehicle_set, youngDriver, oldDriver, unlicenced, \
            heavyVehicle, publicVehicle, Motorcycle in zip(filtered_data['ACCIDENT_DATE'],
                                                           filtered_data['SEVERITY'],
                                                           filtered_data['NODE_TYPE'],
                                                           filtered_data['ACCIDENT_TYPE'],
                                                           filtered_data['YOUNG_DRIVER'],
                                                           filtered_data['OLD_DRIVER'],
                                                           filtered_data['UNLICENCSED'],
                                                           filtered_data['HEAVYVEHICLE'],
                                                           filtered_data['PUBLICVEHICLE'],
                                                           filtered_data['MOTORCYCLE']):
        if date in selected_dates:
            account_data.append([date, SEVERITY, NODE_TYPE, collision_vehicle_set, youngDriver, oldDriver,
                                 unlicenced, heavyVehicle, publicVehicle, Motorcycle])

    serious_injury = len([i[1] for i in account_data if 'Serious injury' in i[1]])
    serious_injury_percentage = f"{(round(serious_injury / len(account_data)* 100,2))}%"

    node_type = len([i[2] for i in account_data if i[2] == 'Intersection'])
    node_type_percentage = f"{round(node_type / len(account_data)* 100, 2)}%"

    collision_vehicle = len([i[3] for i in account_data if i[3] == 'Collision with vehicle'])
    collision_vehicle_percentage = f"{round(collision_vehicle / len(account_data)* 100, 2)}%"

    collision_object = len([i[3] for i in account_data if i[3] == 'Collision with a fixed object'])
    collision_object_percentage = f"{round(collision_object / len(account_data)* 100, 2)}%"

    young_driver = len([i[4] for i in account_data if i[4] == 1])
    young_driver_percentage = f"{round(young_driver / len(account_data)* 100, 2)}%"

    old_driver = len([i[5] for i in account_data if i[5] == 1])
    old_driver_percentage = f"{round(old_driver / len(account_data)* 100, 2)}%"

    nolicenced = len([i[6] for i in account_data if i[6] == 1])
    nolicenced_percentage = f"{round(nolicenced / len(account_data)* 100, 2)}%"

    heavy_vehicle = len([i[7] for i in account_data if i[7] != 0])
    heavy_vehicle_percentage = f"{round(heavy_vehicle / len(account_data)* 100, 2)}%"

    public_vehicle = len([i[8] for i in account_data if i[8] != 0])
    public_vehicle_percentage = f"{round(public_vehicle / len(account_data)* 100, 2)}%"

    motorCycle = len([i[9] for i in account_data if i[9] != 0])
    motorCycle_percentage = f"{round(motorCycle / len(account_data)* 100, 2)}%"

    state = ['Cause serious injury', 'Happened in intersection',
             'Collision with vehicle', 'Collision with fixed object',
             'Young Driver', 'Old Driver', 'Unlicensed driving',
             'Heavy vehicle involved', 'Public vehicle involved', 'Motorcycle involved']

    numb = [serious_injury, node_type, collision_vehicle, collision_object, young_driver, old_driver, nolicenced,
            heavy_vehicle, public_vehicle, motorCycle]
    percentage = [serious_injury_percentage,
                  node_type_percentage,
                  collision_vehicle_percentage,
                  collision_object_percentage,
                  young_driver_percentage,
                  old_driver_percentage,
                  nolicenced_percentage,
                  heavy_vehicle_percentage,
                  public_vehicle_percentage,
                  motorCycle_percentage]

    for i in range(len(state)):
        table_data.append({'State': state[i], 'Number of times': numb[i], 'Percentage': percentage[i]})

    table = dash_table.DataTable(
        id='table',
        columns=[
            {'name': 'State', 'id': 'State'},
            {'name': 'Number of times', 'id': 'Number of times'},
            {'name': 'Percentage', 'id': 'Percentage'}
        ],
        style_cell={
            'textAlign': 'center',
            'backgroundColor': 'lightgrey',
            'color': 'black',
            'fontSize': '28px',
            'fontWeight': 'normal',
            'border': '2px solid black'
        },
        style_table={
            'maxHeight': '800px',  # Set maximum height
            'overflowY': 'scroll',  # Enable vertical scrolling
            'maxWidth': '1500px',  # Set maximum width
        },
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'Percentage',
                    'filter_query': '{Percentage} > 62%'
                },
                'backgroundColor': 'red',
                'color': 'white'
            }
        ],
        style_as_list_view=True,
        style_header={'backgroundColor': 'lightblue',
                      'color': 'darkblue',
                      'fontSize': '32px',
                      'fontWeight': 'bold'},
        data=table_data
    )
    return [html.H3("Accidents Analysis for Selected Dates"), table]

def generate_pie_chart(selected_dates, filtered_data):
    # Filter the data based on selected dates
    filtered_data = filtered_data[filtered_data['ACCIDENT_DATE'].isin(selected_dates)]

    # Calculate the distribution of accident severity
    severity_counts = filtered_data['SEVERITY'].value_counts()
    labels = severity_counts.index.tolist()
    values = severity_counts.values.tolist()

    # Create a pie chart based on accident severity
    trace = go.Pie(labels=labels, values=values, hole=.3)
    layout = go.Layout(title="Accident Severity Distribution for Selected Dates")
    fig = go.Figure(data=[trace], layout=layout)

    return fig


def generate_pie_charts_for_severity_and_speed_zone(selected_dates, filtered_data):
    # Extract unique severity types
    severity_types = filtered_data['SEVERITY'].unique()

    # Create a pie chart for each severity type showing the distribution of SPEED_ZONE
    figures = []
    for severity in severity_types:
        severity_data = filtered_data[filtered_data['SEVERITY'] == severity]
        speed_zone_counts = severity_data['SPEED_ZONE'].value_counts()
        labels = speed_zone_counts.index.tolist()
        values = speed_zone_counts.values.tolist()

        trace = go.Pie(labels=labels, values=values, hole=.3)
        layout = go.Layout(title=f"Speed Zone Distribution for {severity} Accidents")
        fig = go.Figure(data=[trace], layout=layout)
        figures.append(dcc.Graph(figure=fig))

    return figures

# Data filtering functions
def filter_by_keyword(data, keyword):
    return data[data['ACCIDENT_TYPE'].str.contains(keyword, case=False)]

def generate_keyword_table(selected_dates, filtered_data):
    table_data = []
    filtered_data = filtered_data.copy()
    filtered_data['HOUR'] = filtered_data['ACCIDENT_TIME'].str.replace('.', ':')
    for date, light_condition, accident_type, accident_time, severity, fatality, police_attend, speed_zone, day_of_week in zip(filtered_data['ACCIDENT_DATE'],filtered_data['LIGHT_CONDITION'],
                                                  filtered_data['ACCIDENT_TYPE'], filtered_data['HOUR'],filtered_data['SEVERITY'],
                                                                   filtered_data['FATALITY'],filtered_data['POLICE_ATTEND'],
                                                                   filtered_data['SPEED_ZONE'],filtered_data['DAY_OF_WEEK']):
        if date in selected_dates:
            table_data.append({'Date': date, 'Accident Type': accident_type,
                               'Accident Time': accident_time,'Light Condition': light_condition,
                               'Severity':severity,'Fatality':fatality,'Police Attend':police_attend,
                               'Speed Zone':speed_zone,'Day of Week':day_of_week})

    table = dash_table.DataTable(
        id='table',
        columns=[
            {'name': 'Date', 'id': 'Date'},
            {'name': 'Accident Time', 'id': 'Accident Time'},
            {'name': 'Accident Type', 'id': 'Accident Type'},
            {'name': 'Light Condition', 'id': 'Light Condition'},
            {'name': 'Severity', 'id': 'Severity'},
            {'name': 'Fatality', 'id': 'Fatality'},
            {'name': 'Police Attend', 'id': 'Police Attend'},
            {'name': 'Speed Zone', 'id': 'Speed Zone'},
            {'name': 'Day of Week', 'id': 'Day of Week'}
        ],
        style_as_list_view=True,
        style_header={'backgroundColor': 'lightblue',
                      'color': 'darkblue',
                      'fontSize': '15px',
                      'fontWeight': 'bold'},
        style_cell={'textAlign': 'center'},
        style_table={
            'maxHeight': '800px',  # Set maximum height
            'overflowY': 'scroll',  # Enable vertical scrolling
            'maxWidth': '1800px',  # Set maximum width
            'overflowX': 'scroll'  # Enable horizontal scrolling
        },
        data=table_data
    )
    return [html.H3("Filtered Accidents by Keyword for Selected Dates"), table]

def generate_alcohol_graph(selected_dates, list_i):
    # analysis and graphical generation of alcohol-related data is handled here
    # Calculate the number of alcohol-related accidents on a monthly basis
    monthly_alcohol_accidents = []
    # the date year is between 2013-2019
    for year in range(2013, 2019):
        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            alcohol_accidents_count = len([date for date in selected_dates if
                                           start_date <= datetime.strptime(date, '%d/%m/%Y') < end_date and
                                           data['ALCOHOLTIME'][
                                               list_i.index(date)] == 'Yes'])
            monthly_alcohol_accidents.append(
                {'Month': start_date.strftime('%Y-%m'), 'Alcohol Accidents': alcohol_accidents_count})

    # Creating Plotly Charts
    trace = go.Bar(
        x=[entry['Month'] for entry in monthly_alcohol_accidents],
        y=[entry['Alcohol Accidents'] for entry in monthly_alcohol_accidents],
        name="Alcohol Accidents",
        marker=dict(color='rgba(255, 0, 0, 0.5)',
                    line=dict(color='rgb(0, 0, 0)', width=1.5)),
        text=[entry['Alcohol Accidents'] for entry in monthly_alcohol_accidents]
    )

    layout = go.Layout(
        barmode="group",
        title="Monthly Alcohol-Related Accidents",
        xaxis=dict(rangeslider_visible=True),
        xaxis_title="Month",
        yaxis_title="Number of Alcohol Accidents"
    )

    fig = go.Figure(data=[trace], layout=layout)
    return dcc.Graph(id='alcohol-impact-graph', figure=fig)

# Extract hour from accident time
def extract_hour_from_time(filtered_data):
    return filtered_data['ACCIDENT_TIME'].str.replace('.', ':').str.split(':').str[0].astype(int)

# Group by hour and count accidents
def group_by_hour_and_count_accidents(filtered_data):
    return filtered_data.groupby('HOUR').size()

def generate_alcohol_hourly_graph(selected_dates, filtered_data):
    # Extract the hour from the ACCIDENT_TIME column
    filtered_data = filtered_data.copy()
    filtered_data['HOUR'] = extract_hour_from_time(filtered_data)

    # Group by hour and count the number of accidents
    hourly_counts = group_by_hour_and_count_accidents(filtered_data)

    # Calculate the average number of accidents for each hour
    hourly_avg = hourly_counts / len(selected_dates)

    # Creating Plotly Charts
    trace = go.Bar(
        x=hourly_avg.index,
        y=hourly_avg.values,
        name="Average Accidents",
        marker=dict(color='rgba(0, 128, 255, 0.5)',
                    line=dict(color='rgb(0, 0, 0)', width=1.5)),
        text=[round(value, 2) for value in hourly_avg.values]
    )

    layout = go.Layout(
        barmode="group",
        title="Average Number of Accidents Per Hour",
        xaxis_title="Hour",
        yaxis_title="Average Number of Accidents"
    )

    fig = go.Figure(data=[trace], layout=layout)
    return dcc.Graph(id='alcohol-hourly-graph', figure=fig)

# Dash layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Victoria State Accident DataSet Analysis"),

    dcc.Dropdown(
        id='filter-method',
        options=[
            {'label': 'Number of accidents in each hour', 'value': 'period'},
            {'label': 'Filter by Keyword', 'value': 'keyword'},
            {'label': 'All Accidents Analysis', 'value': 'analysis'},
            {'label': 'Alcohol Impact Analysis', 'value': 'alcohol_impact'},
            {'label': 'Pie Chart Analysis', 'value': 'pie_chart'}  # New option, the 5th feature
        ],
        value='period'
    ),

    dcc.RangeSlider(
        id='date-range-slider',
        min=0,
        max=len(list_x) - 1,
        value=[0, len(list_x) - 1],
        marks={0: list_x[0], len(list_x) - 1: list_x[-1]}  # Initially show the first and last date
    ),

    dcc.Input(id='keyword-input',
              type='text',
              placeholder='Enter a keyword of Accident Type',  # Placeholder text
              style={
                  'display': 'none',
                  'width': '500px',  # Increase the width
                  'height': '80px',  # Increase the height
                  'fontSize': '30px',  # Increase font size
                  'color': 'black',  # Text color
                  'backgroundColor': 'lightyellow',  # Background color
                  'border': '2px solid black',  # Border styling
                  'padding': '5px',  # Padding for text
                  'borderRadius': '5px'  # Rounded corners
              }),

    # Hidden keyword input

    html.Div(id='graph-or-table')  # Placeholder for either graph or table
])

# Dash callbacks
@app.callback(
    Output('keyword-input', 'style'),
    [Input('filter-method', 'value')]
)
def show_hide_keyword_input(filter_method):
    if filter_method == 'keyword':
        return {'display': 'block', 'width': '500px', 'fontSize': '20px', 'color': 'black',
                'backgroundColor': 'lightyellow', 'border': '2px solid black', 'padding': '5px',
                'borderRadius': '5px', 'marginBottom': '20px'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('date-range-slider', 'marks'),
    [Input('date-range-slider', 'value')]
)
def update_slider_marks(selected_range):
    return {selected_range[0]: list_x[selected_range[0]], selected_range[1]: list_x[selected_range[1]]}


@app.callback(
    Output('graph-or-table', 'children'),
    [Input('filter-method', 'value'),
     Input('date-range-slider', 'value'),
     Input('keyword-input', 'value')]
)
def update_graph_or_table(filter_method, selected_range, keyword):
    # Extract the selected dates based on the range slider values
    selected_dates = list_x[selected_range[0]:selected_range[1] + 1]

    # Filter the data based on the selected dates
    filtered_data = data[data['ACCIDENT_DATE'].isin(selected_dates)]

    # Check the filter method and generate the appropriate graph or table
    if filter_method == 'period':
        #return [dcc.Graph(id='bar-chart', figure=generate_bar_chart(selected_dates, filtered_data)), generate_alcohol_hourly_graph(selected_dates, filtered_data)]
        return generate_alcohol_hourly_graph(selected_dates, filtered_data)
    elif filter_method == 'keyword':
        if keyword:
            filtered_data = filter_by_keyword(filtered_data, keyword)
            return generate_keyword_table(selected_dates, filtered_data)
        else:
            return generate_keyword_table(selected_dates, filtered_data)
    elif filter_method == 'analysis':
        return generate_table_analysis(selected_dates, filtered_data)
    elif filter_method == 'alcohol_impact':
        return generate_alcohol_graph(selected_dates, list_x)
    elif filter_method == 'pie_chart':
        return [dcc.Graph(id='pie-chart', figure=generate_pie_chart(selected_dates, filtered_data))] + \
            generate_pie_charts_for_severity_and_speed_zone(selected_dates, filtered_data)
    else:
        return html.Div("Invalid filter method selected.")

if __name__ == '__main__':
    app.run_server(debug=True)
