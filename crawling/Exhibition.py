# -*- coding: utf-8 -*-

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import time

# 웹 드라이버 관련 옵션 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--headless")  # 브라우저를 표시하지 않고 실행 (백그라운드에서 실행)

class OpengalleryCrawler:
    '''
    Opengallery 전시회 URL 크롤러
    '''
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_urls = ['https://www.opengallery.co.kr/exhibition/?p={}'.format(i) for i in range(85)]

    def extract_urls(self, soup):
        '''
        주어진 HTML에서 전시회 URL 추출
        '''
        urls = []
        for element in soup:
            a_tags = element.find_all('a')
            for a_tag in a_tags:
                href = a_tag.get('href')
                if "/exhibition/4" in href:
                    urls.append("https://www.opengallery.co.kr/" + href)
        return urls
    
    def extract_clean_html(self):
        '''
        현재 웹 페이지의 HTML을 추출하고 BeautifulSoup 객체로 파싱
        '''
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    
    def crawl_festivals(self):
        '''
        모든 전시회 URL 수집
        '''
        all_urls = []
        for base_url in self.base_urls:
            self.driver.get(base_url)
            soup = self.extract_clean_html()
            urls = self.extract_urls(soup)
            all_urls.extend(urls)
        self.driver.close()
        return all_urls
    
    def main(self):
        urls = self.crawl_festivals()
        return urls

class ExhibitScraper:
    '''
    전시회 스크래퍼
    '''
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)  # 암묵적 대기시간 설정
        self.driver.set_page_load_timeout(60)
        self.columns = ['전시회명', '날짜', '장소', '가격', '주최', '문의', '설명', '입장시간', '메인이미지']
        self.all_data = []
        self.exhibit_df = pd.DataFrame(columns=self.columns)

    def extract_text(self, element, selector):
        '''
        HTML 엘리먼트에서 텍스트 추출
        '''
        selected_element = element.select_one(selector)
        if selected_element:
            return selected_element.get_text(strip=True).replace('\n', ' ').replace('\t', '')
        return None
    
    def extract_image_url(self, element, attr='src'):
        '''
        HTML 엘리먼트에서 이미지 URL 추출
        '''
        if element and element.has_attr(attr):
            img_url = element[attr]
            return img_url
        return None
    
    def scrape_page(self, urls):
        '''
        각 전시회 페이지를 스크랩하고 데이터 수집
        '''
        for url in urls:
            self.driver.get(url)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            name = self.extract_text(soup, "#contents > div > section.exhibitionDetail-head > h2")
            date = self.extract_text(soup, "#contents > div > section:nth-child(4) > div.exhibitionDetail-infoTable > table > tbody > tr:nth-child(3) > td")
            location = self.extract_text(soup, "#contents > div > section:nth-child(4) > div.exhibitionDetail-infoTable > table > tbody > tr:nth-child(2) > td")
            price = self.extract_text(soup, "#contents > div > section:nth-child(4) > div.exhibitionDetail-infoTable > table > tbody > tr:nth-child(5) > td")
            organize = self.extract_text(soup, "#contents > div > section:nth-child(4) > div.exhibitionDetail-infoTable > table > tbody > tr:nth-child(2) > td")
            phone_number = self.extract_text(soup, "#contents > div > section:nth-child(4) > div.exhibitionDetail-infoTable > table > tbody > tr:nth-child(7) > td")
            description = self.extract_text(soup, "#contents > div > section:nth-child(3) > div")
            main_img_element = soup.select_one("#contents > div > section.exhibitionDetail-carousel.owl-carousel.owl-loaded.owl-drag > div.owl-stage-outer > div > div > div > div > img")
            main_img_url = self.extract_image_url(main_img_element)
            hours = self.extract_text(soup, "#contents > div > section:nth-child(4) > div.exhibitionDetail-infoTable > table > tbody > tr:nth-child(4) > td")

            data = {'전시회명': name,
                    '날짜': date,
                    '장소': location,
                    '가격': price,
                    '주최': organize,
                    '문의': phone_number,
                    '설명': description,
                    '입장시간': hours,
                    '메인이미지': main_img_url}
        
            self.all_data.append(data)
        self.exhibit_df = pd.DataFrame(self.all_data)
        return self.exhibit_df  # 데이터프레임을 리턴
        
    def close_driver(self):
        self.driver.quit()

if __name__ == "__main__":
    url_crawler = OpengalleryCrawler()
    urls = url_crawler.main()
    
    scraper = ExhibitScraper()
    exhibit_df = scraper.scrape_page(urls)  
    
    scraper.close_driver()
    
# 추출한 데이터를 CSV 파일로 저장
exhibit_df.to_csv('/Users/seodaeseong/Desktop/Programming/Python_Notebook/redSys/DATA_Files/exhibit_df.csv', index=False)
