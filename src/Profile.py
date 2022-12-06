from googlesearch import search
from bs4 import BeautifulSoup as bs
import plotly.express as px
import pandas as pd


import requests
import json


class Profile:

    def __init__(self, github_profile_name):
        # Initialize properties
        self.github_profile_name = None
        self.github_url = None
        self.full_name = None
        self.company = None
        self.location = None
        self.email = None
        self.link = None
        self.followers = None
        self.following = None
        self.linkedin_url = None
        self.repos = None
        self.language_graph = None
        self.stars = None
        if github_profile_name:
            self.github_profile_name = github_profile_name
            self.github_url = "https://github.com/{0}".format(self.github_profile_name)
            self.repos = self.scrape_repos()
            self.language_graph = self.build_language_graph(self.repos)

            # Fetch available properties from GitHub
            self.get_github_information_v2()
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

    def get_github_information_v2(self):
        query = 'https://github.com/{0}'.format(self.github_profile_name)

        page = requests.get(query)
        soup = bs(page.text, "html.parser")
        print("Scraping profile {0}".format(self.github_profile_name))
        try:
            self.full_name = soup.find("span", {"itemprop": "name"}).text.strip()
        except Exception:
            pass
        try:
            self.location = soup.find("li", {"itemprop": "homeLocation"}).find("span").text
        except:
            pass
        try:
            self.company = soup.find("li", {"itemprop": "worksFor"}).find("span").text
        except:
            pass
        try:
            self.email = soup.find("li", {"itemprop": "email"}).find("a").text
        except:
            pass
        try:
            self.link = soup.find("li", {"itemprop": "url"}).find("a").text
        except:
            pass
        try:
            elems = soup.find_all("span", {"class": "text-bold color-fg-default"})
            self.followers = convert_number_string(elems[0].text)
            self.following = convert_number_string(elems[1].text)
        except:
            pass
        try:
            self.stars = int(soup.find("a", {"data-tab-item": "stars"}).find("span", {"class", "Counter"}).text)
        except:
            self.stars = 0
            pass


        print("\tFull Name: {0}\n\tLocation: {1}\n\tCompany: {2}\n\tEmail: {3}\n\tLink: {4}\n\tFollowers: {5}\n\tFollowing: {6}\n\tStars: {7}"
              .format(self.full_name,
                      self.location,
                      self.company,
                      self.email,
                      self.link,
                      self.followers,
                      self.following,
                      self.stars))



    def scrape_repos(self):
        query = 'https://github.com/{0}?tab=repositories'.format(self.github_profile_name)
        page = requests.get(query)

        soup = bs(page.text, "html.parser")

        repos = soup.find_all("li", {"itemprop": "owns"})
        repo_names = [repo.find("a", {"itemprop": "name codeRepository"}).text.strip() for repo in repos]
        repo_languages = []
        for repo in repos:
            try:
                repo_language = repo.find("span", {"itemprop": "programmingLanguage"}).text
                repo_languages.append(repo_language)
            except:
                pass

        repo_dict = {repo_name: repo_language for (repo_name, repo_language) in zip(repo_names, repo_languages)}
        return repo_dict

    def build_language_graph(self, repo_dict):
        names = list(set(self.repos.values()))
        values = [list(self.repos.values()).count(name) for name in names]
        chart = px.pie(values=values, names=names)
        chart.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        },
        margin=dict(t=0, b=0, l=0, r=0))
        return chart

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

    def to_dict(self):
        return {
            "github_profile_name": self.github_profile_name,
            "github_url": self.github_url,
            "full_name": self.full_name,
            "company": self.company,
            "location": self.location,
            "email": self.email,
            "link": self.link,
            "followers": self.followers,
            "following": self.following,
            "linkedin_url": self.linkedin_url,
            "repos": self.repos,
            "language_graph": self.language_graph,
            "stars": self.stars
        }


def convert_number_string(number_string):
    number = None
    if 'k' in number_string:
        number_string = number_string.replace('k', '')
        number = int(float(number_string) * 1000)
    else:
        number = int(number_string)
    return number