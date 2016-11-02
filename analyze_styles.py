from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json




analyzation_script = None
with open("analyze-style.js") as ANALYZE:
    analyzation_script = ANALYZE.read()


def analyze(browser, url):
    browser.get(url)
    return browser.execute_script(analyzation_script)


def get_browser():
    return webdriver.Chrome()



if __name__ == "__main__":
    sites = []
    with open("sites") as SITES:
        sites = [s for s in SITES.read().split("\n") if s != ""]
    browser = get_browser()

    style_data = []
    for site in sites:
        style_data.append(analyze(browser, site))
    print style_data
    
    browser.quit()