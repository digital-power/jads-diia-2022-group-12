from googlesearch import search

import requests
import json


class Profile:

    def __init__(self, github_profile_name):
        self.github_profile_name = github_profile_name
        # Initialize properties
        self.full_name = None
        self.company = None
        self.location = None
        self.email = None
        self.github_url = None
        self.linkedin_url = None

        # Fetch available properties from GitHub
        self.get_github_information()

    def get_github_information(self):
        query = 'https://api.github.com/users/{0}'.format(self.github_profile_name)
        response = requests.get(query)
        response_dict = json.loads(response.text)
        self.full_name = response_dict['name']
        self.company = response_dict['company']
        self.location = response_dict['location']
        self.github_url = response_dict['html_url']
        self.email = response_dict['email']

    # def get_linkedin_url(self):
    #     if not self.full_name:
    #
    #     query = '"{0}" site:linkedin.com/in OR site:linkedin.com/pub -intitle:profiles -inurl:"/dir"'.format(self.full_name)
    #     for j in search(query, tld="co.in", num=1, stop=1, pause=1):
    #         return