import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import concurrent.futures

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def scrape_article(self, url):
        """
        Extracts main text content from a news article URL.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=12)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove noise
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
                
            title = ""
            if soup.title:
                title = soup.title.get_text().strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()

            # Attempt to find the main article body
            # Common tags for news sites
            article_body = soup.find('article') or soup.find('div', class_=re.compile(r'article|content|story|main', re.I))
            
            if article_body:
                paragraphs = article_body.find_all('p')
            else:
                paragraphs = soup.find_all('p')

            text_content = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
            
            # Clean up whitespace
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            if not text_content:
                return {'title': title, 'text': '', 'error': 'No significant text content found.'}
                
            return {
                'title': title,
                'text': text_content[:8000],  # Limit text size for Gemini
                'url': url,
                'error': None
            }
            
        except Exception as e:
            return {'title': '', 'text': '', 'url': url, 'error': str(e)}

    def scrape_multiple(self, urls):
        """
        Scrapes multiple URLs in parallel to save time.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.scrape_article, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                results.append(future.result())
        return results

# Singleton instance
scraper_instance = NewsScraper()

def get_scraper():
    return scraper_instance
