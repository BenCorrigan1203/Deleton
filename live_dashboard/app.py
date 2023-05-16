import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "0rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Pages", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(page['name'], href=page['relative_path'], active="exact")
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[dash.page_container], style=CONTENT_STYLE)


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        content
    ],

)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)