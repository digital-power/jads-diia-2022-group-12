import warnings

warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

from dash import Dash, dcc, html, Input, Output

app = dash.Dash(
    __name__,
)
resumes = []
professions = {'Software Engineer': 'software engineer',
               'Software Developer': 'software developer'}
locations = {'Amsterdam': 'amsterdam',
             'London': 'london'}
languages = {'Python': 'python',
             'CSS': 'css',
             'Ruby': 'ruby'}
colors = {"background": "#011833", "text": "#7FDBFF"}

app.layout = html.Div(className='body', children=
    [
        html.H1(
            "Skills lookup",
        ),
        html.Div(
            [

                # Dropdown to filter profession
                html.Div(className='dropdown-container', children=
                    [
                        html.Label("Profession"),
                        dcc.Dropdown(
                            id="profession-dropdown",
                            options=[{"label": k, "value": v}
                                     for k, v in professions.items()
                                     ],
                            className="dropdown"
                        ),
                    ]
                ),
                # Dropdown to filter countries with average schooling years.

                html.Div(className='dropdown-container', children=
                    [
                        html.Label("Location"),
                        dcc.Dropdown(
                            id="location-dropdown",
                            options=[{"label": k, "value": v}
                                     for k, v in locations.items()
                                     ],
                            className="dropdown"
                        ),
                    ],
                ),

                html.Div(className='dropdown-container', children=
                    [
                        html.Label("Language"),
                        dcc.Dropdown(
                            id="language-dropdown",
                            options=[{"label": k, "value": v}
                                     for k, v in languages.items()
                                     ],
                            className="dropdown"
                        ),
                    ],
                ),

            ],
            className="row",
        ),
        html.Br(),
        html.Div(id='query-container', className='query-container'),
        html.Div(className='list-container', children=[html.Ul(id='my-list')])
    ],
)


def build_query(selected_profession, selected_location, selected_language):
    query = "site:github.com"
    if selected_profession:
        query += " " + str(selected_profession)
    if selected_location:
        query += " AND " + str(selected_location)
    if selected_language:
        query += " AND language:" + str(selected_language)
    query += " AND ~resume -job -jobs -hire -hiring"
    return query


@app.callback(
    Output('query-container', 'children'),
    Input("profession-dropdown", "value"),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"), prevent_initial_call=True
)
def update_query(selected_profession, selected_location, selected_language):
    query = build_query(selected_profession, selected_location, selected_language)
    return query


@app.callback(
    Output('my-list', 'children'),
    Input("profession-dropdown", "value"),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"), prevent_initial_call=True
)
def update_search(selected_profession, selected_location, selected_language):
    try:
        from googlesearch import search
    except ImportError:
        print("No module named 'google' found")

    query = "site:github.com"
    if selected_profession:
        query += " " + str(selected_profession)
    if selected_location:
        query += " AND " + str(selected_location)
    if selected_language:
        query += " AND language:" + str(selected_language)
    query += " AND ~resume -job -jobs -hire -hiring"
    resumes = []
    for j in search(query, tld="co.in", num=5, stop=5, pause=2):
        link_parts = j.split('/')
        profile_link = '/'.join(link_parts[:4])
        resume_link = j
        resumes.append(html.Li(
            [dcc.Markdown(profile_link), html.Ul(
                html.Li(
                    dcc.Markdown('[Resume]({0})'.format(resume_link))))]))
    return resumes


if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True, threaded=True)
