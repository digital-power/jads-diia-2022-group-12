from src.Profile import Profile
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


URL = 'https://nl.linkedin.com/in/thomaskipf'

# s = Service(ChromeDriverManager().install())

# options = Options()
# options.add_argument("--window-size=1920,1200")

driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

# driver = webdriver.Chrome(options=options, service=s)
driver.get(URL)

try:
    elem = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'experience__list')) #This is a dummy element
    )
finally:
    driver.quit()

print(elem.text)

# test = elem.find_element(By.CLASS_NAME, 'experience-item__duration experience-item__meta-item')
# print(test)
