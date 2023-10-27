# main.py
# -*- coding: utf-8 -*-

from Exhibition import OpengalleryCrawler, ExhibitScraper
from Festival import UrlCrawler, FestivalScraper
from Musical import MusicalCrawler, MusicalScraper
import pandas as pd

def main():
    # Opengallery 크롤링
    url_crawler = OpengalleryCrawler()
    opengallery_urls = url_crawler.main()
    
    exhibit_scraper = ExhibitScraper()
    exhibit_df = exhibit_scraper.scrape_page(opengallery_urls)
    exhibit_scraper.close_driver()
    exhibit_df.to_csv('exhibit_data.csv', index=False)
    
    # Festival 크롤링
    url_crawler = UrlCrawler()
    festival_urls = url_crawler.main()
    
    festival_scraper = FestivalScraper()
    festival_df = festival_scraper.scrape_data(festival_urls)
    festival_scraper.close_driver()
    festival_df.to_csv('festival_data.csv', index=False)
    
    # Musical 크롤링
    musical_crawler = MusicalCrawler()
    musical_urls = musical_crawler.main()
    
    musical_scraper = MusicalScraper()
    musical_df = musical_scraper.scrape_musicals(musical_urls)
    musical_scraper.close_driver()
    musical_df.to_csv('musical_data.csv', index=False)

if __name__ == "__main__":
    main()
