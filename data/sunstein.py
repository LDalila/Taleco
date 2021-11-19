import json
import re
import requests
import time
import urllib.request

from bs4 import BeautifulSoup

from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from scihub.scihub.scihub import SciHub # 🏴‍☠️🏴‍☠️🏴‍☠️

"""
To get the initial list of links:
Go to https://www.jstor.org/action/doBasicSearch?Query=au%3A%28%22cass+sunstein%22%29&so=rel&sd=MINDATE&ed=MAXDATE, replacing MINDATE and MAXDATE by the starting and end year (1987 - 2005)
Run the following Javascript code in the console:

============

output = []

// Loop every 5 seconds to not get rate-limited
itv = setInterval(function () {
  // Get all article links
  all_links = $('pharos-heading[data-qa="search-result-title"]')
  for (link of all_links) {
    // Check that they are from Sunstein and not reviews of his works
    if (!$(link).find('span').length) {
      a = $(link).find('a')
      url = 'https://www.jstor.org' + a.attr('href').match(/^[^\d]*\d+/)
      // Add to our list of data
  	  output.push([url, a.text()])
  	}
  }
  console.log('Total article links parsed so far:', output.length)
  // Look for a "next page" button
  next = $($('pharos-pagination.right')[0].shadowRoot).find('pharos-link.next')
  if (next.length) {
    // If it exists, click it
    $(next[0].shadowRoot).find('a')[0].click()
  } else {
    // If not, we're done
    clearInterval(itv)
    console.log('Parsing done, please copy the output below to "sunstein_links.json"')
    console.log(output)
  }
}, 5000)

============

At the end, right-click the outputted Array and click 'Copy object' (make sure you right-click the left part, on the 'Array' word itself, then paste it into sunstein_links.json.
Then run this script. Whenever a captcha appears, fill it in and press Enter in the console. The program will exit when it's done.
"""

# Help Selenium not get detected and stuck in a captcha loop
# https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec/53040904#53040904
options = webdriver.ChromeOptions() 
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Start Selenium headless browser for Chrome
driver = webdriver.Chrome(options=options)

# More options to not be detected
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'})
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


def get_all_article_info():
    in_file = 'data/sunstein_links.json'
    out_file = 'data/sunstein_articles.json'


    # Read list of links
    with open(in_file, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    all_articles = []
    for link, title in tqdm(data):
        article = {'link': link, 'title': title}
        print(link, title)
        # Access the page
        driver.get(link)
        while True:
            try:
                # Get all metadata about the article
                js_data = driver.execute_script("return gaData.content")
                break
            except:
                # In case of captcha, wait until the user has filled it in
                input('Fill in the captcha, then press Enter in this window')
        # Add to existing article data
        all_articles.append({**article, **js_data})
        print({**article, **js_data})

    # Write all article data to output file
    with open(out_file, 'w') as f:
        json.dump(all_articles, f, indent=4)


def download_all_article_pdfs():
    # Download all links and save them to pdf files
    in_file = 'data/sunstein_articles.json'
    year_regex = re.compile(r'\d{4}')
    
    with open(in_file, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
    
    sh = SciHub()
    for article_dict in tqdm(data):
        date = year_regex.search(article_dict['contentIssue']).group(0)
        title = article_dict['itemTitle'].replace(' ', '_')
        title = ''.join(x for x in title if (x.isalnum() or x in '_-')).lower()
        result = sh.download(article_dict['link'], path=f'data/sunstein_articles/{date}_{title}.pdf')


def get_all_chicago_info():
    out_file = 'data/sunstein_articles2.json'
    
    # Load jQuery for easier parsing
    with open('data/jquery.min.js', 'r') as jquery_js:
        jquery = jquery_js.read()
    
    # Load the first page
    site = 'https://chicagounbound.uchicago.edu/do/search/advanced/?q=author%3A(%20Cass%20R.%20Sunstein%20)&start={}&start_date=01%2F01%2F1987&end_date=12%2F31%2F2005&context=3858785&sort=date_desc&facet='
    all_articles = []
    driver.get(site.format(0))
    
    # Load jQuery
    driver.execute_script(jquery)
    time.sleep(3)
    
    # Read the number of results
    max_i = int(driver.execute_script("return $('strong')[1].textContent"))
    
    for i in tqdm(range(0, max_i + 25, 25)):
        js_data = driver.execute_script("""
links = []
for (article of document.getElementsByClassName('result')) {
    // Parse data for each article
    title = ''
    pub = ''
    link = ''
    date = ''
    title = article.children[0].children[0].textContent
    pub = article.children[0].children[4].children[1].textContent
    link = article.children[0].children[6].children[0].href
    date = article.children[1].children[0].children[1].textContent
    links.push([title, pub, link, date])
}
return links
        """)
        # Remove articles that have no download link
        js_data = [x for x in js_data if 'end_date' not in x[2]]
        all_articles += js_data
        # Go to next page
        if i <= max_i:
            driver.execute_script("$('#next-page')[0].click()")
            time.sleep(1)
    
    # Convert the list of article information to a JSON dictionary
    all_articles = [dict(zip(['title', 'publication', 'link', 'date'], x)) for x in all_articles]
    
    with open(out_file, 'w') as f:
        json.dump(all_articles, f, indent=4)


def download_all_chicago_pdfs():
    # Download all links and save them to pdf files
    in_file = 'data/sunstein_articles2.json'
    
    with open(in_file, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
    
    for article_dict in tqdm(data):
        date = article_dict['date'][-4:]
        title = article_dict['title'].replace(' ', '_')
        title = ''.join(x for x in title if (x.isalnum() or x in '_-')).lower()
        urllib.request.urlretrieve(article_dict['link'], f'data/sunstein_raw/chicago/{date}_{title}.pdf')

# All parts are independent and can be run differently
# get_all_article_info()
# download_all_article_pdfs()
# get_all_chicago_info()
# download_all_chicago_pdfs()

driver.close()