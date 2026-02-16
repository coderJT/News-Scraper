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
            
            # Select articles based on clearer news-specific classes
            # Only picking from sections likely to contain main news
            found_articles = soup.select('div.in-sec-story a, div.focus-story a')
            
            # Format: [[text, href, tag]]
            self.articles = []
            seen_hrefs = set()
            
            # Categories to exclude
            exclude_list = ['/lifestyle/', '/food/', '/tech/', '/travel/', '/business/', '/entertainment/', '/culture/']
            
            for a in found_articles:
                text = a.get_text(strip=True)
                href = a.get('href')
                
                # Basic validation
                if not href or not text or len(text) < 15: # Longer titles usually mean news
                    continue
                    
                if not href.startswith('http'):
                    href = 'https://www.thestar.com.my' + href
                
                # Clean up URL (remove fragments/queries)
                href = href.split('#')[0].split('?')[0]
                
                # Avoid duplicates and check for valid news structure
                if href in seen_hrefs:
                    continue
                
                # Filter: must start with domain, contain /news/ followed by a subcategory
                # and NOT contain excluded categories
                if (href.startswith('https://www.thestar.com.my/news/') and 
                    text.upper() != text and
                    not any(x in href.lower() for x in exclude_list)):
                    
                    # Further check: news articles usually have a date-like structure in URL or certain depth
                    # e.g., /news/nation/2026/02/16/...
                    self.articles.append([text, href, ""])
                    seen_hrefs.add(href)
                    
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
            # More robust paragraph extraction, filtering out ads and navigational text
            paragraphs = []
            for p in story_body.find_all("p"):
                text = p.get_text(strip=True)
                # Skip short sentences or common ad/navigation strings
                if text and len(text) > 10:
                    lower_text = text.lower()
                    if not any(x in lower_text for x in ["advertisement", "subscribe", "read also", "related story", "watching:"]):
                        paragraphs.append(text)
            data['content'] = ' '.join(paragraphs)
        else:
            data['content'] = ""
            
        data['tag'] = tag
        return data

    def thread_scrape_details(self):
        """
        Utilizes multiple threads to speed up scraping process of each article.
        """
        # Filter out empty articles or invalid entries
        valid_articles = [a for a in self.articles if a[1]]
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.get_articles_details, valid_articles)

    def tear_down(self):
        # No-op now as we don't use Selenium
        pass
