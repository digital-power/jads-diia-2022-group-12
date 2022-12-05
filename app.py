import warnings

warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import requests
import json
from dash import callback_context as ctx

from src.Profile import Profile
from googlesearch import search
from dash import Dash, dcc, html, Input, Output

profile_list = []

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

functions = {'Software Developer': 'software developer',
             'Software Engineer': 'software engineer'}
locations = {'Amsterdam': 'amsterdam',
             'The Hague': 'the hague'}
languages = {'Python': 'python',
             'CSS': 'css',
             'Ruby': 'ruby'}
order_options = {'Followers': 'followers',
                 'Stars': 'stars'}
colors = {"background": "#011833", "text": "#7FDBFF"}

app.layout = html.Div(className='body', children=
    [
        dcc.Store(id='profile-list'),
        html.H1(
            "Skills lookup",
        ),
        html.Div(
            [
                html.Div(className='selector-container', children=
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

                html.Div(className='selector-container', children=
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

                html.Div(className='selector-container', children=
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
        # html.Div(className='slider-container', children=[
        #     html.Label("Forks"),
        #     dcc.RangeSlider(min=0, max=10000, step=50, id='fork-range-slider',
        #                     tooltip={"placement": "bottom", "always_visible": True},
        #                     marks={i: str(i) for i in range(0, 10000, 1000)})]),
        html.Br(),
        html.Div(id='query-container', className='query-container'),
        html.Div(className='order-by-container', children=[html.Label("Order By"),
                                                           dcc.Dropdown(id='order-by-dropdown',
                                                                        options=[{"label": k, "value": v}
                                                                                 for k, v in
                                                                                 order_options.items()
                                                                                 ],
                                                                        )]),
        html.Div(className='list-container', children=[html.Ul(id='my-list')])
    ],
)


@app.callback(
    Output('query-container', 'children'),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"),
    # Input("fork-range-slider", "value"),
    prevent_initial_call=True
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
    # if fork_range:
    #     query += 'followers:>{0}'.format(fork_range[0])
    return query

@app.callback(
    Output('profile-list', 'data'),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"),
    # Input("fork-range-slider", "value"),
    prevent_initial_call=True
)
def get_profiles(selected_location, selected_language):
    max_results = 15
    query = query_builder(selected_location, selected_language)
    response = requests.get(query)
    response_dict = json.loads(response.text)
    results = response_dict['items'][0:max_results]
    print(response_dict)
    usernames = [result['login'] for result in results]
    profiles = [Profile(username) for username in usernames]


@app.callback(
    Output('my-list', 'children'),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"),
    # Input("fork-range-slider", "value"),
    prevent_initial_call=True
)
def update_search(selected_location, selected_language):
    max_results = 5
    if ctx.triggered_id in ["location-dropdown", "language-dropdown"]:
        query = query_builder(selected_location, selected_language)
        response = requests.get(query)
        response_dict = json.loads(response.text)
        results = response_dict['items'][0:max_results]
        print(response_dict)
        usernames = [result['login'] for result in results]
        profiles = [Profile(username) for username in usernames]
        info_list = [html.Details(className='profile-collapse', children=[
                        html.Summary(profile.github_profile_name),
                            html.Div(className='profile-container', children=[
                                html.Div(className='language-plot-container', children=dcc.Graph(figure=profile.language_graph)),
                                html.Li(className='info-list', children=[dcc.Markdown(profile.github_profile_name),
                                    html.Ul([html.Li(dcc.Markdown("Name: {0}".format(profile.full_name))),
                                    html.Li(dcc.Markdown("GitHub: {0}".format(profile.github_url))),
                                    html.Li(dcc.Markdown("Location: {0}".format(profile.location))),
                                    html.Li(dcc.Markdown("LinkedIn: {0}".format(profile.linkedin_url))),
                                    html.Li(dcc.Markdown("Website: {0}".format(profile.link))),
                                    html.Li(dcc.Markdown("GitHub followers: {0}".format(profile.followers))),
                                    html.Li(dcc.Markdown("Total GitHub repositories: {0}".format(len(profile.repos))))])])])]) for profile in profiles]
        profile_list = profiles
        return info_list

# @app.callback(
#     Output('my-list', 'children'),
#     Input("order-by-dropdown", "value"),
#     prevent_initial_call=True
# )
# def update_list_order(order_by):
#     if order_by == "followers":
#         print(profile_list)



if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True, threaded=True)
