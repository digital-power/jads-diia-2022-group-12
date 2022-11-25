import warnings

warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

import requests
import json

from dash import Dash, dcc, html, Input, Output

app = dash.Dash(
    __name__,
)
resumes = []
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


def get_user_information(profile_name):
    query = 'https://api.github.com/users/{0}'.format(profile_name)
    response = requests.get(query)
    response_dict = json.loads(response.text)
    return response_dict


def get_user_information_first_ten_results(search_results):
    information_dict = dict()
    for i in range(10):
        search_result = search_results[i]
        user_information_dict = dict()

        user_information = get_user_information(search_result['login'])
        user_information_dict['name'] = user_information['name']
        user_information_dict['location'] = user_information['location']
        information_dict[search_result['login']] = user_information_dict
    print(information_dict)


@app.callback(
    Output('my-list', 'children'),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"), prevent_initial_call=True
)
def update_search(selected_location, selected_language):
    query = query_builder(selected_location, selected_language)
    response = requests.get(query)
    response_dict = json.loads(response.text)
    results = response_dict['items']
    info_list = [html.Li([dcc.Markdown(result['login']), html.Ul(html.Li(dcc.Markdown(result['html_url'])))]) for result in results]
    get_user_information_first_ten_results(results)
    return info_list

    # resumes.append(html.Li(
    #     [dcc.Markdown(profile_link), html.Ul(
    #         html.Li(
    #                 dcc.Markdown('[Resume]({0})'.format(resume_link))))]))


if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True, threaded=True)
