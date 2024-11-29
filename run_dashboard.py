import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as go
import pandas as pd

CORRECT_PASSWORD = "secret123"  # Change this to your desired password

app = dash.Dash(__name__)

# Initialize empty DataFrame
df = pd.DataFrame(columns=['Player', 'Location', 'Score'])

app.layout = html.Div([
    html.H1("Pub Golf Scoreboard"),
    html.Div([
        dcc.Input(id='player-name', type='text', placeholder='Enter player name'),
        dcc.Input(id='location-name', type='text', placeholder='Enter location'),
        dcc.Input(id='score-input', type='number', placeholder='Enter score'),
        dcc.Input(id='password-input', type='password', placeholder='Password'),  # New password field
        html.Button('Submit Score', id='submit-button', n_clicks=0),
    ], style={'display': 'flex', 'gap': '10px', 'margin': '10px'}),
    
    html.Div(id='score-table'),
    
    dcc.Tabs([
        dcc.Tab(label='Graphs', children=[
            dcc.Graph(id='score-graph'),
            dcc.Graph(id='total-score-graph')
        ]),
        dcc.Tab(label='Rankings', children=[
            html.Div(id='rankings-div', style={'margin': '20px'})
        ])
    ])
])

@app.callback(
    [Output('score-table', 'children'),
     Output('player-name', 'value'),
     Output('location-name', 'value'),
     Output('score-input', 'value'),
     Output('password-input', 'value')],  # Add password reset
    Input('submit-button', 'n_clicks'),
    [State('player-name', 'value'),
     State('location-name', 'value'),
     State('score-input', 'value'),
     State('password-input', 'value')]  # Add password state
)
def update_table(n_clicks, player, location, score, password):
    global df
    if n_clicks > 0 and player and location and score is not None:
        if password == CORRECT_PASSWORD:
            new_row = pd.DataFrame({
                'Player': [player],
                'Location': [location],
                'Score': [score]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            # Sort DataFrame by Player name
            df = df.sort_values('Player', ignore_index=True)
    
    # Create table with consistent ID
    table = dash_table.DataTable(
        id='table',  # Simplified ID
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        row_deletable=True,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
            'padding': '10px'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )
    return table, '', '', None, ''

@app.callback(
    Output('score-graph', 'figure'),
    Input('score-table', 'children')
)
def update_graph(_):
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

@app.callback(
    Output('total-score-graph', 'figure'),
    Input('score-table', 'children')
)
def update_total_scores(_):
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

@app.callback(
    Output('rankings-div', 'children'),
    Input('score-table', 'children')
)
def update_rankings(_):
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
    app.run_server(debug=False)