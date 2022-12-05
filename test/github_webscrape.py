import requests
from bs4 import BeautifulSoup as bs
from src.Profile import Profile

number_string = "12.4k"
if 'k' in number_string:
    number_string = number_string.replace('k', '')
    number = float(number_string)
    print(int(number*1000))