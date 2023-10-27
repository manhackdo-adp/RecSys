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

class UrlCrawler:
    '''
    페스티벌 URL 크롤러
    '''
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_url = "https://korean.visitkorea.or.kr/kfes/list/wntyFstvlList.do"

    def extract_urls(self, soup):
        '''
        주어진 HTML에서 축제 URL 추출
        '''
        urls = []
        for element in soup:
            a_tags = element.find_all('a')
            for a_tag in a_tags:
                href = a_tag.get('href')
                if "/kfes/detail/fstvlDetail.do" in href:
                    urls.append("https://korean.visitkorea.or.kr/" + href)
        return urls

    def extract_clean_html(self):
        '''
        현재 웹 페이지의 HTML을 추출하고 BeautifulSoup 객체로 파싱
        '''
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        extract_elements = ['footer', 'header', 'head']
        
        for element in extract_elements:
            extract = soup.find(element)
            if extract:
                extract.extract()
        
        return soup

    def scroll_to_bottom(self):
        while True:
            prev_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == prev_height:
                break

    def crawl_festivals(self):
        self.driver.get(self.base_url)
        self.scroll_to_bottom()
        soup = self.extract_clean_html()
        urls = self.extract_urls(soup)
        
        self.driver.close()
        
        return urls

    def main(self):
        urls = self.crawl_festivals()
        urls = urls[3:]  # 첫 3개의 URL 제외
        return urls

class FestivalScraper:
    '''
    축제 스크래퍼
    '''
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)  # 암묵적 대기시간 설정
        self.driver.set_page_load_timeout(60)
        self.columns = ['축제명', '날짜', '장소', '가격', '주최', '문의', '내용1', '내용2', '메인이미지', '백그라운드']
        self.all_data = []
        self.festival_df = pd.DataFrame(columns=self.columns)

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
    
    def extract_background_image_url(self, style):
        '''
        스타일 속성에서 배경 이미지 URL 추출
        '''
        if style and "background:url(" in style:
            img_url = style.split("background:url(")[1].split(")")[0]
            return img_url
        return None
    
    def scrape_data(self, urls):
        for url in urls:
            self.driver.get(url)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            name = self.extract_text(soup, '#festival_head').replace(" ", "")
            date = self.extract_text(soup, 'body > main > div > div > section.poster_title > div > div > div.schedule > span:nth-child(2)')
            location = self.extract_text(soup, 'body > main > div > div > section.poster_detail > div > div.poster_detail_wrap > div > div.img_info_box > ul > li:nth-child(2) > p')
            preview = self.extract_text(soup, 'body > main > div > div > section.poster_detail > div > div.poster_info_content > div.m_img_fst > div:not(.more_pc_btn)').replace('더보기', '')
            full_ct = self.extract_text(soup, 'body > main > div > div > section.poster_detail > div > div.poster_info_content > div.m_more > p')
            price = self.extract_text(soup, 'body > main > div > div > section.poster_detail > div > div.poster_detail_wrap > div > div.img_info_box > ul > li:nth-child(3) > p')
            organize = self.extract_text(soup, 'body > main > div > div > section.poster_detail > div > div.poster_detail_wrap > div > div.img_info_box > ul > li:nth-child(4) > p')
            phone_element = soup.select_one('a[href^="tel:"] > p.info_content')
            phone_number = phone_element.get_text(strip=True) if phone_element else None

            main_img_element = soup.select_one("img[alt*='포스터']")
            main_img_url = self.extract_image_url(main_img_element)
            
            bg_img_url = self.extract_background_image_url(soup.select_one("div.visula_bg").get('style'))
            
            data = {'축제명': name,
                    '날짜': date,
                    '장소': location,
                    '가격': price,
                    '주최': organize,
                    '문의': phone_number,
                    '내용1': preview,
                    '내용2': full_ct,
                    '메인이미지': main_img_url,
                    '백그라운드': bg_img_url}

            self.all_data.append(data)
        self.festival_df = pd.DataFrame(self.all_data)
        return self.festival_df  # 데이터프레임을 리턴

    def close_driver(self):
        self.driver.quit()

if __name__ == "__main__":
    url_crawler = UrlCrawler()
    urls = url_crawler.main()
    
    scraper = FestivalScraper()
    festival_df = scraper.scrape_data(urls)  
    
    scraper.close_driver()

# 추출한 데이터를 CSV 파일로 저장
festival_df.to_csv('/Users/seodaeseong/Desktop/Programming/Python_Notebook/redSys/DATA_Files/festival_data.csv', index=False)
