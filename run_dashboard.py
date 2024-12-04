import dash
from dash import dcc, html
from dash import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__)

# Load existing data
def load_data():
    try:
        return pd.read_csv('data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Player', 'Location', 'Score'])

# Save data to CSV
def save_data(df):
    df.to_csv('data.csv', index=False)

# Layout of the app
app.layout = html.Div([
    html.H1('Pub Golf Dashboard'),
    dcc.Input(id='player-name', type='text', placeholder='Enter player name'),
    dcc.Input(id='location', type='text', placeholder='Enter location'),
    dcc.Input(id='score', type='number', placeholder='Enter score'),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='output-message'),
    html.H2('Score Table'),
    html.Div(id='table-container'),
    html.H2('Scores by Location'),
    dcc.Graph(id='score-chart')
])

# Callback to handle form submission and update chart
@app.callback(
    [Output('output-message', 'children'),
     Output('table-container', 'children'),
     Output('score-chart', 'figure')],
    Input('submit-button', 'n_clicks'),
    State('player-name', 'value'),
    State('location', 'value'),
    State('score', 'value')
)
def update_dashboard(n_clicks, player_name, location, score):
    df = load_data()
    
    if n_clicks > 0 and player_name and location and score:
        # Create new row as DataFrame
        new_data = pd.DataFrame({
            'Player': [player_name],
            'Location': [location],
            'Score': [score]
        })
        
        # Concatenate with existing data
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        message = 'Data submitted successfully!'
    else:
        message = 'Please fill all fields'
    
    # Create table
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
    )
    
    # Create figure
    fig = px.bar(df, x='Location', y='Score', color='Player',
                 title='Scores by Location and Player',
                 barmode='group') if not df.empty else {}
    
    return message, table, fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
