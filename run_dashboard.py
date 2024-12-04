import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as go
import pandas as pd
import os
from dash import callback_context

CORRECT_PASSWORD = "test"  # Change this to your desired password

app = dash.Dash(__name__)

# Initialize empty DataFrame
df = pd.DataFrame(columns=['Player', 'Location', 'Score'])

input_style = {
    'padding': '10px',
    'margin': '5px',
    'border': '1px solid #ccc',
    'border-radius': '5px',
    'width': '200px'
}

# Add these functions at the top
def save_to_csv(data):
    df = pd.DataFrame(data)
    df.to_csv('scores.csv', index=False)

def load_from_csv():
    if os.path.exists('scores.csv'):
        return pd.read_csv('scores.csv')
    return pd.DataFrame(columns=['Player', 'Location', 'Score'])

app.layout = html.Div([
    dcc.Store(id='store-data'),
    html.H1("Pub Golf Scoreboard"),
    html.Div([
        dcc.Input(id='player-name', type='text', placeholder='Enter player name', style=input_style),
        dcc.Input(id='location-name', type='text', placeholder='Enter location', style=input_style),
        dcc.Input(id='score-input', type='number', placeholder='Enter score', style=input_style),
        dcc.Input(id='password-input', type='password', placeholder='Password', style=input_style),
        html.Button('Submit Score', id='submit-button', n_clicks=0),
    ], style={'display': 'flex', 'gap': '10px', 'margin': '10px'}),
    
    dcc.Tabs([
        dcc.Tab(label='Table', children=[
            html.Div(id='score-table'),  # Add this div for table container
            dash_table.DataTable(
                id='table',
                columns=[
                    {
                        "name": "Player", 
                        "id": "Player", 
                        "type": "text",
                        "filter_options": {
                            "case": "insensitive",
                            "operators": ["contains", "not contains", "equals"]
                        }
                    },
                    {
                        "name": "Location", 
                        "id": "Location", 
                        "type": "text",
                        "filter_options": {
                            "case": "insensitive",
                            "operators": ["contains", "not contains", "equals"]
                        }
                    },
                    {
                        "name": "Score", 
                        "id": "Score", 
                        "type": "numeric",
                        "filter_options": {
                            "operators": [">=", "<=", "=", "<", ">"]
                        }
                    }
                ],
                data=[],
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'minWidth': '100px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'border': '1px solid black'
                },
                style_filter={
                    'backgroundColor': 'rgb(240, 240, 240)',
                    'padding': '8px'
                },
                row_deletable=True
            )
        ]),
        dcc.Tab(label='Graphs', children=[
            dcc.Graph(id='score-graph'),
            dcc.Graph(id='total-score-graph')
        ]),
        dcc.Tab(label='Rankings', children=[
            html.Div(id='rankings-div', style={'margin': '20px'})
        ])
    ])
])

# Modify update_data_and_table callback
@app.callback(
    [Output('store-data', 'data', allow_duplicate=True),
     Output('score-table', 'children')],
    [Input('submit-button', 'n_clicks'),
     Input('table', 'data')],
    [State('player-name', 'value'),
     State('location-name', 'value'),
     State('score-input', 'value'),
     State('password-input', 'value'),
     State('store-data', 'data')],
    prevent_initial_call=True
)
def update_data_and_table(n_clicks, table_data, player, location, score, password, stored_data):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    df = load_from_csv()
    
    if trigger_id == 'submit-button':
        if all([player, location, score is not None]) and password == CORRECT_PASSWORD:
            new_row = pd.DataFrame({
                'Player': [player],
                'Location': [location],
                'Score': [score]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df = df.sort_values('Player', ignore_index=True)
            save_to_csv(df)
    
    elif trigger_id == 'table':
        df = pd.DataFrame(table_data)
        save_to_csv(df)
    
    table = dash_table.DataTable(
        id='table',
        columns=[
            {
                "name": "Player", 
                "id": "Player", 
                "type": "text",
                "filter_options": {
                    "case": "insensitive",
                    "operators": ["contains", "not contains", "equals"]
                }
            },
            {
                "name": "Location", 
                "id": "Location", 
                "type": "text",
                "filter_options": {
                    "case": "insensitive",
                    "operators": ["contains", "not contains", "equals"]
                }
            },
            {
                "name": "Score", 
                "id": "Score", 
                "type": "numeric",
                "filter_options": {
                    "operators": [">=", "<=", "=", "<", ">"]
                }
            }
        ],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px', 'minWidth': '100px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_filter={'backgroundColor': 'rgb(240, 240, 240)', 'padding': '8px'},
        row_deletable=True
    )
    
    return df.to_dict('records'), table

# Add callback to reset input fields
@app.callback(
    [Output('player-name', 'value'),
     Output('location-name', 'value'),
     Output('score-input', 'value'),
     Output('password-input', 'value')],
    Input('submit-button', 'n_clicks')
)
def reset_inputs(n_clicks):
    return '', '', None, ''

# Update delete callback
@app.callback(
    Output('store-data', 'data'),
    Input('table', 'data'),
    State('store-data', 'data')
)
def sync_deleted_data(table_data, stored_data):
    if table_data is None:
        return stored_data
    return table_data

# Update graph callbacks to use CSV
@app.callback(
    Output('score-graph', 'figure'),
    Input('store-data', 'data')
)
def update_graph(_):
    df = load_from_csv()
    if df.empty:
        return {}
    
    fig = go.Figure()
    
    # Add bars for each player
    for player in df['Player'].unique():
        player_data = df[df['Player'] == player]
        fig.add_trace(go.Bar(
            x=player_data['Location'],
            y=player_data['Score'],
            name=player,
        ))
    
    fig.update_layout(
        title='Scores by Location',
        xaxis_title='Location',
        yaxis_title='Score',
        barmode='group',  # Group bars by location
        hovermode='x unified'
    )
    
    return fig

# Update graph callbacks to use CSV
@app.callback(
    Output('total-score-graph', 'figure'),
    Input('store-data', 'data')
)
def update_total_scores(_):
    df = load_from_csv()
    if df.empty:
        return {}
    
    # Calculate total scores for each player
    total_scores = df.groupby('Player')['Score'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=total_scores['Player'],
        y=total_scores['Score'],
        name='Total Score'
    ))
    
    fig.update_layout(
        title='Total Scores by Player',
        xaxis_title='Player',
        yaxis_title='Total Score',
        barmode='group',
        showlegend=False
    )
    
    return fig

# Update graph callbacks to use CSV
@app.callback(
    Output('rankings-div', 'children'),
    Input('store-data', 'data')
)
def update_rankings(_):
    df = load_from_csv()
    if df.empty:
        return html.P("No scores submitted yet")
    
    # Calculate total scores for each player
    total_scores = df.groupby('Player')['Score'].sum().reset_index()
    total_scores = total_scores.sort_values('Score')  # Sort by score (lowest is best)
    
    rankings = []
    medals = ['🥇 ', '🥈 ', '🥉 ']
    
    for i, (_, row) in enumerate(total_scores.head(3).iterrows()):
        if i < len(medals):
            rankings.append(html.H3(f"{medals[i]}{row['Player']} - Total Score: {row['Score']}"))
    
    return html.Div(rankings)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)