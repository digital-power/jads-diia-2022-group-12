from googlesearch import search

import requests
import json


class Profile:

    def __init__(self, github_profile_name):
        # Initialize properties
        self.github_profile_name = github_profile_name
        self.full_name = None
        self.company = None
        self.location = None
        self.email = None
        self.github_url = None
        self.linkedin_url = None

        # Fetch available properties from GitHub
        self.get_github_information()

        # Fetch LinkedIn URL
        self.get_linkedin_url()

    def get_github_information(self):
        # Build query based on profile name
        query = 'https://api.github.com/users/{0}'.format(self.github_profile_name)

        # Get query results
        response = requests.get(query)
        response_dict = json.loads(response.text)

        # Add info to class
        self.full_name = response_dict['name']
        self.company = response_dict['company']
        self.location = response_dict['location']
        self.github_url = response_dict['html_url']
        self.email = response_dict['email']

    def get_linkedin_url(self):
        # TODO: Google search API is horribly slow, find alternative
        formatted_location = self.location.split(", ")[0]
        query = '"{0}" AND "{1}" site:linkedin.com/in OR site:linkedin.com/pub -intitle:profiles -inurl:"/dir"'\
            .format(self.full_name, formatted_location)
        results = search(query, tld="co.in", num=1, stop=1, pause=2)
        for result in results:
            # TODO: Fix this if statement
            self.linkedin_url = result if result else "Not found."
            break

