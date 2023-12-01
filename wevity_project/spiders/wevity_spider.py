
import scrapy
from wevity_project.items import ContestItem
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags, replace_escape_chars
import boto3
from scrapy.spiders import Spider

def clean_html(raw_html):
    # HTML 태그를 제거하고 깨끗한 텍스트로 변환하는 함수입니다.
    clean_text = remove_tags(raw_html)
    clean_text = replace_escape_chars(clean_text, which_ones=('\n', '\t', '\r'))
    return clean_text.strip()

class WevitySpider(scrapy.Spider):
    name = 'wevity_spider'
    allowed_domains = ['wevity.com']
    start_urls = ['https://www.wevity.com/?c=find&s=1&gub=2&cidx=5']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # S3 클라이언트 초기화
        self.s3_client = boto3.client('s3')
        # 이미 저장된 데이터 목록을 불러옵니다.
        self.existing_items = self.load_existing_items()

    def load_existing_items(self):
        # S3 버킷에서 데이터 목록을 불러옵니다.
        # 예시로 'mybucket/myfolder/' 경로의 객체 목록을 가져옵니다.
        response = self.s3_client.list_objects_v2(Bucket='jh-capstone2-bucket', Prefix='myfolder/')
        return [item['Key'] for item in response.get('Contents', [])]


    def parse(self, response):
        count = 0 
        # 목록 페이지에서 각 상세 페이지로의 링크를 추출합니다.
        contests = response.css('.list > li:not(.top)')
        for contest in contests:
            contest_url = contest.css('.tit a::attr(href)').get()
            # 마감된 공모전을 건너뜁니다.
            # 이미 처리된 항목인지 확인
            if contest_url in self.existing_items:
                # 이 경우 크롤링 중단 또는 건너뛰기
                break
            deadline_info = contest.css('.day .dday.end::text').get()
            # 마감 텍스트가 '마감'인지 확인합니다.
            if deadline_info and "마감" in deadline_info:
                count += 1
                if count >= 20:
                    # 마감된 공모전이 20개 이상이면 크롤링을 종료합니다.
                    return
                continue

            link = contest.css('.tit a::attr(href)').get()
            if link:
                # 상세 페이지로의 요청을 생성합니다.
                yield response.follow(link, self.parse_detail)
        next_page = response.css('.list-navi a::attr(href)').re(r'&gp=(\d+)')
        current_page = response.css('.list-navi a.on::attr(href)').re_first(r'&gp=(\d+)')

        if next_page:
            next_page = max(map(int, next_page))  # 최대 페이지 번호를 찾습니다.
            current_page = int(current_page) if current_page else 1  # 현재 페이지 번호를 가져옵니다.
            
            if next_page > current_page:  # 다음 페이지가 현재 페이지보다 클 경우에만 요청을 생성합니다.
                next_page_url = f"?c=find&s=1&gub=2&cidx=5&gp={next_page}"
                yield response.follow(next_page_url, self.parse)

    def parse_detail(self, response):
        # 상세 페이지에서 필요한 정보를 추출합니다.
        loader = ItemLoader(item=ContestItem(), response=response)
        title_html = response.css('.tit-area h6.tit').get()
        loader.add_value('title', clean_html(title_html))
        
        # 주최/주관 정보를 추출하고 HTML 태그를 제거합니다.
        sponsor_html = response.xpath('//li[span[contains(text(), "주최/주관")]]').get()
        loader.add_value('sponsor', clean_html(sponsor_html))
        
        # 접수기간을 추출하고 HTML 태그를 제거합니다.
        deadline_html = response.css('.dday-area').get()
        loader.add_value('deadline', clean_html(deadline_html))
        
        # 공모전 이미지 URL을 추출합니다.
        image_url = response.css('.thumb img::attr(src)').get()
        if image_url:
            loader.add_value('image_urls', [response.urljoin(image_url)])  # 상대 URL을 절대 URL로 변환

        # 상세 내용을 추출합니다.
        detailed_content_html = response.css('div#viewContents').get()
        loader.add_value('description', detailed_content_html)
        
        yield loader.load_item()
    