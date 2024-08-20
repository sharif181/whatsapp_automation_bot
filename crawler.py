import time

from helper.scaper import Scraper


class Crawler:
    def __init__(self, url: str):
        self.url = url
        self.crawler = None

    def initialize_whatsapp(self):
        self.crawler = Scraper(self.url)
    
    def send_message(self, number: str, message: str):
        self.crawler.driver.get(f'https://web.whatsapp.com/send?phone={number}')
        time.sleep(10)

if __name__ == "__main__":
    crawler = Crawler("https://web.whatsapp.com/")
    crawler.initialize_whatsapp()

    if crawler.crawler.setup_done:
        time.sleep(20)
        crawler.send_message("", "")