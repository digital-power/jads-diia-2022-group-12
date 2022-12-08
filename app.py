import warnings

warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import requests
import json
from dash import callback_context as ctx
import pandas as pd

from src.Profile import Profile
from dash import Dash, dcc, html, Input, Output, State

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

functions = {'Software Developer': 'software developer',
             'Software Engineer': 'software engineer'}
locations = {'Amsterdam': 'amsterdam',
             'The Hague': 'the hague',
             'Rotterdam': 'rotterdam',
             'Utrecht': 'utrecht',
             'Eindhoven': 'eindhoven',
             'Groningen': 'groningen'}
languages = {'Python': 'python',
             'C': 'c',
             'C++': 'c++',
             'CSS': 'css',
             'Ruby': 'ruby'}
order_options = {'Followers': 'followers',
                 'Stars': 'stars'}
order_type = {'Ascending': False,
              'Descending': True}
colors = {"background": "#011833", "text": "#7FDBFF"}

app.layout = html.Div(className='body', children=
    [
        dcc.Download(id="download"),
        dcc.Store(id='profile-list'),
        dcc.ConfirmDialog(
            id='confirm-',
            message='Danger danger! Are you sure you want to continue?',
        ),
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
        html.Div(className='search-button-container', children=[html.Button('Search', id='search-button', n_clicks=0)]),
        html.Br(),
        html.Div(id='query-container', className='query-container'),
        html.Div(className='order-by-container', children=[html.Label("Order By"),
                                                           dcc.Dropdown(id='order-by-dropdown',
                                                                        options=[{"label": k, "value": v}
                                                                                 for k, v in
                                                                                 order_options.items()
                                                                                 ],
                                                                        )]),
        html.Div(className='order-type-container', children=[html.Label("Order Type"),
                                                           dcc.Dropdown(id='order-type-dropdown',
                                                                        options=[{"label": k, "value": v}
                                                                                 for k, v in
                                                                                 order_type.items()
                                                                                 ],
                                                                        )]),
        html.Div(className='list-container', children=[html.Ul(id='my-list')]),
        html.Div(className='export-button-container', children=[html.Button('Export to Excel', id='export-button', n_clicks=0)])
    ],
)


@app.callback(
    Output('query-container', 'children'),
    Input("location-dropdown", "value"),
    Input("language-dropdown", "value"),
    prevent_initial_call=True
)
def update_query(selected_location, selected_language):
    query = query_builder(selected_location, selected_language)
    return query


def query_builder(location_list, language_list):
    # Build query based on location and language
    query = 'https://api.github.com/search/users?q='
    if location_list:
        location_query = '+'.join(['location:"{0}"'.format(location) for location in location_list])
        query += location_query
    if language_list:
        language_query = '+'.join(['language:"{0}"'.format(language) for language in language_list])
        query += language_query
    return query


@app.callback(
    Output('profile-list', 'data'),
    Input("search-button", "n_clicks"),
    State("location-dropdown", "value"),
    State("language-dropdown", "value"),
    prevent_initial_call=True
)
def get_profiles(n_clicks, selected_location, selected_language):
    # Limit results
    max_results = 50
    query = query_builder(selected_location, selected_language)
    response = requests.get(query)
    response_dict = json.loads(response.text)
    if len(response_dict['items']) > max_results:
        results = response_dict['items'][0:max_results]
    else:
        results = response_dict['items']
    usernames = [result['login'] for result in results]
    profiles = []
    # Google and GitHub dont like a lot of requests, find status code 429 to indicate whether we're locked out
    access_to_github = True
    access_to_google = True
    for username in usernames:
        cur_profile = Profile(username)
        if access_to_github:
            access_to_github = cur_profile.get_github_information_v2()
        if access_to_google:
            access_to_google = cur_profile.get_linkedin_url()
    # If we can't find full name skip adding the profile
        if cur_profile.full_name:
            profiles.append(cur_profile)
    # Convert profiles to dict to allow saving
    return [profile.to_dict() for profile in profiles]


@app.callback(
    Output('my-list', 'children'),
    Input('profile-list', 'data'),
    Input("order-by-dropdown", "value"),
    Input("order-type-dropdown", "value"),
    prevent_initial_call=True
)
def update_list(profile_list, order_by, order_type):
    # If profile list exists
    if profile_list:
        # Convert dicts to profile class instances
        profiles = [profile_from_dict(profile) for profile in profile_list]
        # Check the order dropdowns
        if ctx.triggered_id in ['order-by-dropdown', 'order-type-dropdown']:
            # If order dropdowns are assigned
            if order_by and order_type is not None:
                # Order by followers
                if order_by == 'followers':
                    profiles = sorted(profiles, key=lambda x: x.followers, reverse=order_type)
                # Order by stars
                elif order_by == 'stars':
                    profiles = sorted(profiles, key=lambda x: x.stars, reverse=order_type)
        # Build list components and add to list on page
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
                                    html.Li(dcc.Markdown("Stars: {0}".format(profile.stars))),
                                    html.Li(dcc.Markdown("Total GitHub repositories: {0}".format(len(profile.repos))))])])])]) for profile in profiles]
        return info_list


@app.callback(
    Output("download", "data"),
    Input("export-button", "n_clicks"),
    State('profile-list', 'data'),
    prevent_initial_call=True
)
def export_to_excel(n_clicks, profiles):
    # Export to excel if there are profiles in list
    if len(profiles) > 0:
        profiles_df = pd.DataFrame(profiles)
        profiles_df = profiles_df.drop(['language_graph'], axis=1)
        profiles_df = profiles_df.reset_index(drop=True)
        profiles_df_csv = profiles_df.to_csv(sep=';')
        return dict(content=profiles_df_csv, filename="profile_export.csv")


def profile_from_dict(data_dict):
    # Build profile from dict
    profile = Profile(None)
    profile.github_profile_name = data_dict['github_profile_name']
    profile.github_url = data_dict['github_url']
    profile.full_name = data_dict['full_name']
    profile.company = data_dict['company']
    profile.location = data_dict['location']
    profile.email = data_dict['email']
    profile.link = data_dict['link']
    profile.followers = data_dict['followers']
    profile.following = data_dict['following']
    profile.linkedin_url = data_dict['linkedin_url']
    profile.repos = data_dict['repos']
    profile.language_graph = data_dict['language_graph']
    profile.stars = data_dict['stars']
    return profile


if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True, threaded=True)
