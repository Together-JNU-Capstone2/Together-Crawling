import scrapy

class ContestItem(scrapy.Item):
    # 각 필드는 데이터베이스의 컬럼과 일치하게 설정합니다.
    item_id = scrapy.Field()  # 일반적으로 이 값은 크롤링 중 자동으로 설정되거나 데이터베이스에 의해 할당됩니다.
    title = scrapy.Field()
    content = scrapy.Field()
    sponsor = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    deadline = scrapy.Field()
    views = scrapy.Field()
    # 추가하신 description 필드
    description = scrapy.Field()
