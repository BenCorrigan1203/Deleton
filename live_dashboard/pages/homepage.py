from dash import html
import dash

from dash_utils import get_db_connection


dash.register_page(__name__, path="/")


DIV_STYLE = {
    'display': 'inline-block',
    "padding": "2rem 1rem"
}

layout = html.Div(id="main", children=[
    
    html.Section(id='current_ride', children=[
        html.H1("Current Ride"),

        html.Div(style=DIV_STYLE, children=[
            html.H2('Rider Name'),
        ]),

        html.Div(style=DIV_STYLE, children=[
            html.H1('Rider Gender'),
        ]),

         html.Div(style=DIV_STYLE, children=[
            html.H1('Rider Age'),
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

