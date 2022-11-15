from bs4 import BeautifulSoup
import requests

from threading import Thread
import time

try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")


def github_webscrape_v1():

    username = 'manuelarte'

    github_html = requests.get(f'https://github.com/{username}').text
    soup = BeautifulSoup(github_html, "html.parser")
    out = str(soup)
    split = out.split('\n')

    for i, line in enumerate(split):
        if 'octicon-location' in line:
            print(split[i + 1])

    return soup

def github_webscrape_v2():

    username = 'manuelarte'

    github_html = requests.get(f'https://github.com/{username}').text
    soup = BeautifulSoup(github_html, "html.parser")

    location_li = soup.body.find("li",{"itemprop":"homeLocation"})
    location_span = location_li.findChildren(["span", "a"], recursive=True)
    location = location_span[0].text
    print(location)

    return soup

def find_location(profile_url):
    github_html = requests.get(profile_url).text
    soup = BeautifulSoup(github_html, "html.parser")
    if soup.body:
        location_li = soup.body.find("li", {"itemprop": "homeLocation"})
        if location_li:
            location_span = location_li.findChildren(["span", "a"], recursive=True)
            location = location_span[0].text
            print(location)
        else:
            print('Not found for:', profile_url)
    else:
        print('No body found')

def find_profile(gist_url):
    github_html = requests.get(gist_url).text
    soup = BeautifulSoup(github_html, "html.parser")
    if soup.body:
        user_a = soup.body.find("span", {"class": "author"})
        if user_a:
            profile_name = user_a.findChildren("a")[0].text
            return profile_name
        else:
            print('Not found for:', gist_url)
    else:
        print('No body found')
    return 0


def github_webscrape_v3():
    start_v3 = time.time()
    query = "site:github.com software AND (developer OR engineer) AND language:java AND ~resume -job -jobs -hire -hiring -topics"
    result_stop = 30
    for j in search(query, tld="co.in", num=result_stop, stop=result_stop, pause=2):
        link_parts = j.split('/')
        profile_url = '/'.join(link_parts[:4])

        find_location(profile_url)
    end_v3 = time.time()
    print("V3", end_v3-start_v3)

def github_webscrape_v4():
    start_v4 = time.time()
    threads = []
    number = 5
    start = 0
    stop = 3
    pause = 2
    query = "site:github.com software AND (developer OR engineer) AND language:python AND ~cv -job -jobs -hire -hiring -topics"

    results = search(query, tld="com", num=number, start=start, stop=stop, pause=pause)

    for j in results:
        link_parts = j.split('/')
        profile_name = link_parts[3]
        profile_url = "https://github.com/{0}".format(profile_name)
        print(j, profile_url)
        scrape_thread = Thread(target=find_location(profile_url))
        scrape_thread.run()
        threads.append(scrape_thread)

    end_v4 = time.time()
    print("V4", end_v4-start_v4)

def get_longlist():
    start_v4 = time.time()
    threads = []
    number = 5
    start = 0
    stop = 5
    pause = 2
    query = "site:github.com software AND (developer OR engineer) AND language:python AND ~cv -job -jobs -hire -hiring -topics"

    results = search(query, tld="com", num=number, start=start, stop=stop, pause=pause)

    print([find_location(link) for link in results])

get_longlist()