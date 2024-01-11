import time
import logging
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, url, urlWithTag, tags=[]):
        self.articles = []
        self.articlesDetails = []
        self.driver = None
        self.url = url
        self.urlWithTag = urlWithTag
        self.tags = tags

    def setup_driver(self):
        options = webdriver.ChromeOptions()
         # Continue Selenium processes immediately after initial page content is received.
        options.page_load_strategy = 'none'
        # Prevent browser interface from displaying
        options.add_argument('--headless')
        # Prevent extensions from loading
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(options=options)
    
    def get_article_to_scrape(self):
        """
        Retrieves a list of articles with their name and urls to be scraped.
        """
        driver = self.driver
        driver.get(self.url)

        # Wait for articles to load
        wait_load = WebDriverWait(driver, 20).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".focus-story, .more-story, .in-sec-story"))
        )
        time.sleep(3)

        # Get article name and article url and set tag as unknown
        self.articles = [[article.text, article.get_attribute('href'), ""]
                         for article in driver.find_elements(By.XPATH, "//div[contains(@class, 'in-sec-story')]//descendant::a")]
        
        # Filter out links not starting with 'https://www.thestar.com.my' and links that are fully uppercased
        self.articles = list(filter(
            lambda x: x[1].startswith('https://www.thestar.com.my') and
                        (x[0].upper() != x[0]),
                        self.articles
        ))

    
    def get_articles_to_scrape_by_tag(self):
        """
        Retrieves a list of articles to be scraped according to tags specified by user.
        """

        for tag in self.tags:
            driver = self.driver
            target = self.urlWithTag + tag
            driver.get(target)

            # Wait for articlees to load
            wait_load = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//ul[contains(@class, 'timeline')]//descendant::li"))
            )

            time.sleep(3) # Modifying to below 3 might cause scraping to fail

            # Get article name, article url and article tags
            self.articles.extend(
                [[article.text, article.get_attribute('href'), tag]
                 for article in driver.find_elements(By.XPATH, "//div[contains(@class, 'timeline-content')]//h2//a")]
            )
    
    def get_articles_details(self, article):
        """
        Handles the request of each articles.
        """
        try: 
            req = requests.get(article[1])
            soup = BeautifulSoup(req.text, 'lxml')
            result = self.scrape_details(soup, article[0], article[1], article[2])
            self.articlesDetails.append(result)
        except requests.exceptions as error:
            logger.error(f"Error encountered while requesting for article", error)

    def scrape_details(self, soup, name, url, tag):
        """
        Extracts data from BeautifulSoup object
        """
        data = {}
        data['name'] = name
        data['url'] = url
        data['category'] = soup.find('a', class_='kicker').text 
        data['published_date'] = str(soup.find(class_='date').text).strip() or "Unknown"
        data['content'] = ' '.join([p.text
                                    for p in soup.find(id='story-body') \
                                    .find_all("p", recursive=False)])
        # TODO: Filter content
        data['tag'] = tag if tag != "" else ""
        return data
        

    def thread_scrape_details(self):
        """
        Utilizes multiple threads to speed up scraping process of each article.
        """
        # Currently set max_workers to 2 to avoid overusing memory of Render
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.map(self.get_articles_details, self.articles)

    def tear_down(self):
        if self.driver:
            self.driver.close()





