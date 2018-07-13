# -*- coding: utf-8 -*-
import functools
import scrapy
from datetime import datetime

from cars4sale import loaders, items

class OlxSpider(scrapy.Spider):
    name = "olx"
    start_urls = [
        'http://www.olx.com.ar/autos-cat-378/'
    ]

    def parse(self, response):
        for brand in response.xpath("//div[@id='listing-filters']/div[contains(@class,'carbrand')]//label/input"):
            brand_name = brand.xpath("./@value").extract_first()
            filter_name = brand.xpath("./@data-filter-name").extract_first()
            if brand_name not in ['other','otro']:
                href = "{0}/-{1}_{2}".format(response.url, filter_name, brand_name)
                yield scrapy.Request(href, callback=functools.partial(self.parse_models, brand_name.replace('+',' ')))

    def parse_models(self, brand, response):
        for model in response.xpath("//div[@id='listing-filters']/div[contains(@class,'carmodel')]//label/input"):
            model_name = model.xpath("./@value").extract_first()
            filter_name = model.xpath("./@data-filter-name").extract_first()
            if model_name not in ['other','otro']:
                href = "{0}-{1}_{2}".format(response.url, filter_name, model_name)
                yield scrapy.Request(href, callback=functools.partial(self.parse_ads, brand, model_name.replace('+',' ')))

    def parse_ads(self, brand, model, response):
        for ad in response.xpath("//main[@id='items-list-view']/ul/li/div"):
            price = ad.xpath("./p[@class='items-price']/a/text()").extract_first().strip()
            if price.startswith("$") or price.startswith("USD"):
                cb = functools.partial(self.parse_ad, brand, model)
                href = "https:" + ad.xpath("./a[1]/@href").extract_first()
                yield scrapy.Request(href, callback=cb)

        next_page = response.xpath("//div[@id='items-pagination']//a[contains(@class,'next')]/@href").extract_first()
        if next_page is not None:
            yield scrapy.Request('http:' + next_page, callback=functools.partial(self.parse_ads, brand, model))

    def parse_ad(self, brand, model, response):
        loader = loaders.OlxCarAdLoader(item=items.CarAd(), response=response)

        loader.add_xpath("title", "//article//div[@class='title']/h1/text()")
        loader.add_value("brand", [brand])
        loader.add_value("model", [model])
        loader.add_xpath("year", "//article/div/section/ul/li[1]/span/text()")
        loader.add_xpath("price", "//article/div/section/header//strong[@class='price']/text()")
        loader.add_xpath("currency", "//article/div/section/header//strong[@class='price']/text()")
        loader.add_xpath("km", "//article/div/section/ul/li[4]/span/text()")
        loader.add_value("href", [response.url])
        loader.add_xpath("img", "//article/div/section/section/figure/a[1]/img/@src")
        loader.add_value("source", [self.name])
        loader.add_value("date", [datetime.today()])

        return loader.load_item()
