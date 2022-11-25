import requests
import json


def search(location_list, language_list):
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


location_list = ['The Hague']
language_list = ['Python', 'Ruby']

results = search(location_list, language_list)
print(results)
# print(dig_user_search_result(results['items'][0])['name'])
