import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "./assets/pills.css"], use_pages=True)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#333333",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "0rem",
    "padding": "2rem 1rem"
}

sidebar = html.Div(
    [
        html.H2("Pages", className="display-4", style={"color": "#7fc37e"}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(page['name'], href=page['relative_path'], active="exact", style={"color": "#7fc37e"})
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True
        ),
        html.Img(src=app.get_asset_url('deloton.png'), style={"width": "100%", "height": "auto", "position": "absolute", "bottom": "0", "left": "0"})
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[dash.page_container], style=CONTENT_STYLE)


app.layout = html.Div(children=
    [
        dcc.Location(id="url"),
        sidebar,
        content
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)