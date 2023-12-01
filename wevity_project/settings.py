# Scrapy settings for wevity_project project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "wevity_project"
SPIDER_MODULES = ["wevity_project.spiders"]
NEWSPIDER_MODULE = "wevity_project.spiders"
ROBOTSTXT_OBEY = True
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 기존 설정에 추가
ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'wevity_project.pipelines.S3Pipeline': 300,  # 파이프라인 경로를 적절히 조정하세요.
}

IMAGES_STORE = 's3://jh-capstone2-bucket/img/'

