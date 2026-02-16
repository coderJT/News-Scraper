import time
import logging
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, url, urlWithTag, tags=[]):
        self.articles = []
        self.articlesDetails = []
        self.url = url
        self.urlWithTag = urlWithTag
        self.tags = tags

    def setup_driver(self):
        # No-op now as we don't use Selenium, but kept for compatibility with existing server calls
        pass
    
    def get_article_to_scrape(self):
        """
        Retrieves a list of articles with their name and urls to be scraped.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Select articles based on the classes used in original scraper
            # Standard CSS selectors for these classes
            found_articles = soup.select('div.in-sec-story a, div.focus-story a, div.more-story a')
            
            # Format: [[text, href, tag]]
            self.articles = []
            for a in found_articles:
                text = a.get_text(strip=True)
                href = a.get('href')
                if href and not href.startswith('http'):
                    href = 'https://www.thestar.com.my' + href
                
                # Filter as per original logic: must start with domain and not be all uppercase
                if href and href.startswith('https://www.thestar.com.my') and text.upper() != text:
                    self.articles.append([text, href, ""])
                    
        except Exception as e:
            logger.error(f"Error getting articles to scrape: {e}")

    def get_articles_to_scrape_by_tag(self):
        """
        Retrieves a list of articles to be scraped according to tags specified by user.
        """
        for tag in self.tags:
            target_url = self.urlWithTag + tag
            try:
                response = requests.get(target_url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Original XPath: //div[contains(@class, 'timeline-content')]//h2//a
                found_articles = soup.select('div.timeline-content h2 a')
                
                for a in found_articles:
                    text = a.get_text(strip=True)
                    href = a.get('href')
                    if href and not href.startswith('http'):
                        href = 'https://www.thestar.com.my' + href
                    self.articles.append([text, href, tag])
                    
            except Exception as e:
                logger.error(f"Error getting articles by tag '{tag}': {e}")

    def get_articles_details(self, article):
        """
        Handles the request of each articles.
        """
        try: 
            req = requests.get(article[1], timeout=10)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, 'lxml')
            result = self.scrape_details(soup, article[0], article[1], article[2])
            self.articlesDetails.append(result)
        except Exception as error:
            logger.error(f"Error encountered while requesting for article {article[1]}: {error}")

    def scrape_details(self, soup, name, url, tag):
        """
        Extracts data from BeautifulSoup object
        """
        data = {}
        data['name'] = name
        data['url'] = url
        
        kicker = soup.find('a', class_='kicker')
        data['category'] = kicker.text if kicker else "Unknown"
        
        date_elem = soup.find(class_='date')
        data['published_date'] = str(date_elem.text).strip() if date_elem else "Unknown"
        
        story_body = soup.find(id='story-body')
        if story_body:
            data['content'] = ' '.join([p.text for p in story_body.find_all("p", recursive=False)])
        else:
            data['content'] = ""
            
        data['tag'] = tag
        return data

    def thread_scrape_details(self):
        """
        Utilizes multiple threads to speed up scraping process of each article.
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.get_articles_details, self.articles)

    def tear_down(self):
        # No-op now as we don't use Selenium
        pass
