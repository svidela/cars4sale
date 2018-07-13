import scrapy

class CarAd(scrapy.Item):
    title = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    version = scrapy.Field()
    year = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    km = scrapy.Field()
    href = scrapy.Field()
    img = scrapy.Field()
    source = scrapy.Field()
    date = scrapy.Field()
