import requests
import json
from googlesearch import search



def search_loc(location_list, language_list):
    query = 'https://api.github.com/search/users?q='
    location_query = '+'.join(['location:"{0}"'.format(location) for location in location_list])
    language_query = '+'.join(['language:"{0}"'.format(language) for language in language_list])
    query += location_query
    query += language_query
    query += "per_page=10page=1"
    print(query)
    response = requests.get(query)
    response_dict = json.loads(response.text)
    return response_dict


def dig_user_search_result(search_result):
    user_url = search_result['url']
    response = requests.get(user_url)
    response_dict = json.loads(response.text)
    return response_dict


def dig_user_url(url):
    response = requests.get(url)
    response_dict = json.loads(response.text)
    return response_dict

def get_linkedin_profile_from_name(full_name):
    query = '"{0}" site:linkedin.com/in OR site:linkedin.com/pub -intitle:profiles -inurl:"/dir"'.format(full_name)
    for j in search(query, tld="co.in", num=1, stop=1, pause=2):
        return j

def get_user_information(profile_name):
    query = 'https://api.github.com/users/{0}'.format(profile_name)
    response = requests.get(query)
    response_dict = json.loads(response.text)
    response_dict['linkedin'] = get_linkedin_profile_from_name(response_dict['name'])
    return response_dict


# location_list = ['The Hague']
# language_list = ['Python', 'Ruby']
#
# results = search(location_list, language_list)
# print(results)
# # print(dig_user_search_result(results['items'][0])['name'])

print(get_user_information("tkipf"))