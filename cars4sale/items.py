import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose

from cars4sale import utils

class CarAdLoader(ItemLoader):
    default_output_processor = TakeFirst()

    title_in = MapCompose(str.strip, str.upper)
    brand_in = MapCompose(str.upper)
    model_in = MapCompose(str.upper)
    version_in = MapCompose(str.upper)

    year_in = MapCompose(int)
    price_in = MapCompose(utils.drop_dot, int)
    km_in = MapCompose(utils.split_and_get, utils.drop_dot, int)
    img_in = MapCompose(utils.drop_url_query)

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
