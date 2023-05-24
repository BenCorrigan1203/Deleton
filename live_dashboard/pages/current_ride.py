from dash import html, callback, Output, Input, dcc
import dash
from dash_utils import get_db_connection, get_current_rider_data, heart_rate_status_colour, heart_rate_graph, resistance_graph, power_graph
from dotenv import load_dotenv


dash.register_page(__name__, path="/")
load_dotenv()
engine = get_db_connection()



DIV_STYLE = {
    'display': 'inline-block',
    'width': '30%',  # Divide the available width evenly among the six divs
    'textAlign': 'left',
    'verticalAlign': 'middle',
}

GRAPH_STYLE = {
    'display': 'inline-block',
    'width': '33%',
    'height': '50%',
    'textAlign': 'center',
    'verticalAlign': 'top', 
    'padding': '3rem 0rem 0rem 0rem'
}



layout = html.Div(id="main", children=[
    
    html.Section(id='current_ride', children=[
        html.H1(style = {'textAlign': 'left', 'verticalAlign': 'middle', 'marginBottom': '2rem'}, children="Current Ride"),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="current_rider_name", children=""),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="current_rider_gender", children="", style={'color': 'blue'}),
        ]),

         html.Div(style=DIV_STYLE, children=[
            html.H2(id="current_rider_age", children=""),
        ]),

        html.Hr(style={'border': '1px solid black', 'width': '80%'}),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="current_ride_duration", children=""),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="current_heart_rate", children=""),
        ]),

         html.Div(style=DIV_STYLE, children=[
            html.H2(id="heart_safety", children="", style={'color': 'green'}),
        ]),
    ]),

    html.Section(id='current_rides_graph', children=[
        html.Div(style=GRAPH_STYLE, children=[
            dcc.Graph(id='heart_rate_graph', config={'displayModeBar': False}),
        ]),
        html.Div(style=GRAPH_STYLE, children=[
            dcc.Graph(id='resistance_graph', config={'displayModeBar': False}),
        ]),
        html.Div(style=GRAPH_STYLE, children=[
            dcc.Graph(id='power_graph', config={'displayModeBar': False}),
        ])
    ]),

    dcc.Interval(
            id='interval-component',
            interval=2*1000, # in milliseconds
            n_intervals=0
        )
]
)



@callback(Output('current_rider_name', 'children'),
          Output('current_rider_gender', 'children'),
          Output('current_rider_age', 'children'),
          Output('current_ride_duration', 'children'),
          Output('current_heart_rate', 'children'),
          Output('heart_safety', 'children'),
          Output("heart_safety", "style"),
          Input('interval-component', 'n_intervals'))
def update_metrics(n):
    data = get_current_rider_data(engine)
    return f"{data['name']}", f"{data['gender']}",\
          f"{data['age']} Yrs", f"{data['duration']} Secs",\
          f"{data['heart_rate']} BPM", f"{data['heart_safety']}", {"color": heart_rate_status_colour(data['heart_safety'])}


@callback(Output('heart_rate_graph', 'figure'),
          Output('resistance_graph', 'figure'),
          Output('power_graph', 'figure'),
          Input('interval-component', 'n_intervals'))
def update_graphs(n):
    return heart_rate_graph(engine), resistance_graph(engine), power_graph(engine)
