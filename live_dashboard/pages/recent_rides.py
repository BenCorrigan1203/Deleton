from dash import html, callback, Output, Input, dcc
import dash
from dash_utils import get_db_connection, age_graph, gender_graph, metrics
from dotenv import load_dotenv


dash.register_page(__name__, path="/recent_rides")
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
    'width': '50%',
    'height': '50%',
    'textAlign': 'center',
    'verticalAlign': 'top', 
    'padding': '3rem 0rem 0rem 0rem'
}



layout = html.Div(id="main", children=[
    
    html.Section(id='recent_ride_metrics', children=[
        html.H1(style = {'textAlign': 'left', 'verticalAlign': 'middle', 'marginBottom': '2rem'}, children="Recent Rides"),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="total_power_title", children="Cumulative Power"),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="avg_power_title", children="Average Power"),
        ]),

         html.Div(style=DIV_STYLE, children=[
            html.H2(id="avg_resistance_title", children="Average Resistance"),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="total_power", children="", style={"font-size": "25px"}),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H2(id="avg_power", children="", style={"font-size": "25px"}),
        ]),

         html.Div(style=DIV_STYLE, children=[
            html.H2(id="avg_resistance", children="", style={"font-size": "25px"}),
        ]),
    ]),

    html.Section(id='recent_rides_graph', children=[
        html.Div(style=GRAPH_STYLE, children=[
            dcc.Graph(id='gender_graph', config={'displayModeBar': False}),
        ]),
        html.Div(style=GRAPH_STYLE, children=[
            dcc.Graph(id='age_graph', config={'displayModeBar': False}),
        ])
    ]),

    dcc.Interval(
            id='interval-component',
            interval=300*1000, # in milliseconds
            n_intervals=0
        )
]
)



@callback(Output('total_power', 'children'),
          Output('avg_power', 'children'),
          Output('avg_resistance', 'children'),
          Input('interval-component', 'n_intervals'))
def update_metrics(n):
    metrics_dict = metrics(engine)
    return f'{metrics_dict["total_power"]} Watts', f'{metrics_dict["avg_power"]} W/s', f'{metrics_dict["avg_resistance"]} N'


@callback(Output('gender_graph', 'figure'),
          Output('age_graph', 'figure'),
          Input('interval-component', 'n_intervals'))
def update_graphs(n):
    return gender_graph(engine), age_graph(engine)