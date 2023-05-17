from dash import html
import dash

from dash_utils import get_db_connection, get_current_rider_name
from dotenv import load_dotenv


dash.register_page(__name__, path="/")
load_dotenv()
engine = get_db_connection()

initial_load_rider = get_current_rider_name(engine)
print(initial_load_rider)

DIV_STYLE = {
    'display': 'inline-block',
    "padding": "2rem 1rem"
}

layout = html.Div(id="main", children=[
    
    html.Section(id='current_ride', children=[
        html.H1("Current Ride"),

        html.Div(style=DIV_STYLE, children=[
            html.H2(children=f"{initial_load_rider['name']}"),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H1(children=f"{initial_load_rider['gender']}"),
        ]),

         html.Div(style=DIV_STYLE, children=[
            html.H1(children=f"{initial_load_rider['age']}"),
        ]),

        html.Hr(style={'border': '1px solid black'}),

        html.Div(style=DIV_STYLE, children=[
            html.H1('Duration'),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H1('BPM'),
        ]),

         html.Div(style=DIV_STYLE, children=[
            html.H1('Danger?'),
        ]),
    ]),

    html.Section(id='recent_rides', children=[
        html.H1("Recent Rides")
    ]),
]
)

