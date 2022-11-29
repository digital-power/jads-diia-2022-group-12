import warnings

warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import requests
import json

from src.Profile import Profile
from googlesearch import search
from dash import Dash, dcc, html, Input, Output

app = dash.Dash(
    __name__,
)
resumes = []
functions = {'Software Developer': 'software developer',
             'Software Engineer': 'software engineer'}
locations = {'Amsterdam': 'amsterdam',
             'The Hague': 'the hague'}
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
                html.Div(className='dropdown-container', children=
                [
                    html.Label("Function"),
                    dcc.Dropdown(
                        id="function-dropdown",
                        multi=True,
                        options=[{"label": k, "value": v}
                                 for k, v in functions.items()
                                 ],
                        className="dropdown"
                    ),
                ],
                         ),

                html.Div(className='dropdown-container', children=
                    [
                        html.Label("Location"),
                        dcc.Dropdown(
                            id="location-dropdown",
                            multi=True,
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
                            multi=True,
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


@app.callback(
    Output('query-container', 'children'),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"), prevent_initial_call=True
)
def update_query(selected_location, selected_language):
    query = query_builder(selected_location, selected_language)
    return query

def query_builder(location_list, language_list):
    query = 'https://api.github.com/search/users?q='
    if location_list:
        location_query = '+'.join(['location:"{0}"'.format(location) for location in location_list])
        query += location_query
    if language_list:
        language_query = '+'.join(['language:"{0}"'.format(language) for language in language_list])
        query += language_query
    return query


def get_linkedin_profile_from_name(full_name):
    query = '"{0}" site:linkedin.com/in OR site:linkedin.com/pub -intitle:profiles -inurl:"/dir"'.format(full_name)
    for j in search(query, tld="co.in", num=1, stop=1, pause=1):
        return

@app.callback(
    Output('my-list', 'children'),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"), prevent_initial_call=True
)
def update_search(selected_location, selected_language):
    max_results = 3
    query = query_builder(selected_location, selected_language)
    response = requests.get(query)
    response_dict = json.loads(response.text)
    results = response_dict['items'][0:max_results]
    usernames = [result['login'] for result in results]
    profiles = [Profile(username) for username in usernames]
    info_list = [html.Li([dcc.Markdown(profile.github_profile_name),
                          html.Ul([html.Li(dcc.Markdown("Name: {0}".format(profile.full_name))),
                                   html.Li(dcc.Markdown("GitHub: {0}".format(profile.github_url))),
                                   html.Li(dcc.Markdown("Location: {0}".format(profile.location))),
                                   html.Li(dcc.Markdown("LinkedIn: {0}".format(profile.linkedin_url)))])]) for profile in profiles]
    return info_list


if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True, threaded=True)
