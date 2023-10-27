# -*- coding: utf-8 -*-

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# 웹 드라이버 관련 옵션 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--headless")  # 브라우저를 표시하지 않고 실행 (백그라운드에서 실행)

class MusicalCrawler:
    '''
    뮤지컬 URL 크롤러
    '''
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_urls = []

        categories = ["000001", "000002", "000003", "000004", "000005", "000006"]
        page_ranges = [(1, 7), (1, 10), (1, 11), (1, 5), (1, 11), (1, 2)]

        for category, (start_page, end_page) in zip(categories, page_ranges):
            for i in range(start_page, end_page):
                url = f"http://www.playdb.co.kr/playdb/playdblist.asp?Page={i}&sReqMainCategory={category}&sReqSubCategory=&sReqDistrict=&sReqTab=2&sPlayType=2&sStartYear=&sSelectType="
                self.base_urls.append(url)

    def extract_urls(self, soup):
        '''
        주어진 HTML에서 뮤지컬 URL 추출
        '''
        urls = []
        a_tags = soup.find_all("a", href=True, onclick=True)
        for a_tag in a_tags:
            href = a_tag['href']
            click = a_tag['onclick']
            if "http://www.playdb.co.kr/playdb/PlaydbDetail.asp?sReqPlayNo=" in href:
                urls.append(href)
            elif "goDetail" in click:
                play_no = click.replace('goDetail(\'', '').replace('\')', '')
                url = "http://www.playdb.co.kr/playdb/PlaydbDetail.asp?sReqPlayNo=" + play_no
                urls.append(url)
        return urls

    def extract_clean_html(self, url):
        '''
        현재 웹 페이지의 HTML을 추출하고 BeautifulSoup 객체로 파싱
        '''
        self.driver.get(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def crawl_musicals(self):
        all_urls = []

        for base_url in self.base_urls:
            soup = self.extract_clean_html(base_url)
            urls = self.extract_urls(soup)
            all_urls.extend(urls)

        return all_urls

    def main(self):
        urls = self.crawl_musicals()
        self.driver.close()
        return urls

class MusicalScraper:
    '''
    뮤지컬 스크래퍼
    '''
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)  # 암묵적 대기시간 설정
        self.driver.set_page_load_timeout(60)
        self.columns = ['뮤지컬명', '날짜', '장소', '내용1', '관람등급', '메인이미지']
        self.all_data = []
        self.musical_df = pd.DataFrame(columns=self.columns)

    def extract_text(self, soup, selector):
        '''
        HTML 엘리먼트에서 텍스트 추출
        '''
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True).replace('\n', ' ').replace('\t', '')
        return None
    
    def extract_image_url(self, element, attr='src'):
        '''
        HTML 엘리먼트에서 이미지 URL 추출
        '''
        if element and element.has_attr(attr):
            img_url = element[attr]
            return img_url
        return None
    
    def scrape_musicals(self, urls):
        for url in urls:
            self.driver.get(url)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            name = self.extract_text(soup, "#wrap > div.pddetail > div.pddetail_info > div.pddetail_subject > table > tbody > tr:nth-child(1) > td > span.title")
            date = self.extract_text(soup, "#wrap > div.pddetail > div.pddetail_info > div.detaillist > table > tbody > tr:nth-child(2) > td:nth-child(2)")
            location = self.extract_text(soup, "#wrap > div.pddetail > div.pddetail_info > div.detaillist > table > tbody > tr:nth-child(3) > td:nth-child(2) > a")
            preview = self.extract_text(soup, "#DivBasic > div > div:nth-child(1) > p")
            main_img_element = soup.select_one("#wrap > div.pddetail > h2 > img")
            main_img_url = self.extract_image_url(main_img_element)
            age = self.extract_text(soup, "#wrap > div.pddetail > div.pddetail_info > div.detaillist > table > tbody > tr:nth-child(5) > td:nth-child(2)")
            
            data = {'뮤지컬명': name,
                    '날짜': date,
                    '장소': location,
                    '내용1': preview,
                    '관람등급': age,
                    '메인이미지': main_img_url
            }
        
            self.all_data.append(data)
        self.musical_df = pd.DataFrame(self.all_data)
        return self.musical_df  # 데이터프레임을 리턴
        
    def close_driver(self):
        self.driver.quit()

if __name__ == "__main__":
    url_crawler = MusicalCrawler()
    urls = url_crawler.main()

    scraper = MusicalScraper()
    musical_df = scraper.scrape_musicals(urls)  
    
    scraper.close_driver()

# 추출한 데이터를 CSV 파일로 저장
musical_df.to_csv('/Users/seodaeseong/Desktop/Programming/Python_Notebook/redSys/DATA_Files/musical_all_df.csv', index=False)
