from dash import html
import dash


dash.register_page(__name__, path="/")



layout = html.Div(children=[
    html.H1(children="Home Page! Come see some bike action."),

]
)