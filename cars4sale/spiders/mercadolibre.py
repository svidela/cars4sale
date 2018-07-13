# -*- coding: utf-8 -*-
import scrapy
import functools
from datetime import datetime

from cars4sale import loaders, items

class MercadolibreSpider(scrapy.Spider):
    name = "mercadolibre"
    start_urls = [
        'http://autos.mercadolibre.com.ar/'
    ]

    def parse(self, response):
        for brand in response.xpath("//dl[contains(@class,'filters__brand')]//div[@class='modal-content']//a"):
            brand_name = brand.xpath("@title").extract_first()
            if brand_name != 'Otras Marcas':
                href = response.urljoin(brand.xpath("@href").extract_first())
                yield scrapy.Request(href, callback=functools.partial(self.parse_models, brand_name))

    def parse_models(self, brand, response):
        models = response.xpath("//dl[contains(@class,'filters__model')]//div[@class='modal-content']//a")
        if not models:
            models = response.xpath("//dl[contains(@class,'filters__model')]//a")

        for model in models:
            model_name = model.xpath("@title").extract_first()
            if model_name != 'Otros Modelos':
                href = response.urljoin(model.xpath("@href").extract_first())
                yield scrapy.Request(href, callback=functools.partial(self.parse_versions, brand, model_name))

    def parse_versions(self, brand, model, response):
        versions = response.xpath("//dl[@id='id_SHORT_VERSION']//div[contains(@class,'modal-content')]//a")
        if not versions:
            versions = response.xpath("//dl[@id='id_SHORT_VERSION']//a")

        for version in versions:
            version_name = version.xpath("@title").extract_first()
            if version_name != 'Otras Versiones':
                href = response.urljoin(version.xpath("@href").extract_first())
                yield scrapy.Request(href, callback=functools.partial(self.parse_ads, brand, model, version_name))

    def parse_ads(self, brand, model, version, response):
        for ad in response.xpath("//ol[@id='searchResults']/li/div/div/div/@item-url"):
            cb = functools.partial(self.parse_ad, brand, model, version)
            yield scrapy.Request(response.urljoin(ad.extract()), callback=cb)

        next_page = response.xpath("//section[@id='results-section']/div[@class='pagination__container']/ul/li[@class='pagination__next']/a/@href").extract_first()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=functools.partial(self.parse_ads, brand, model, version))

    def parse_ad(self, brand, model, version, response):
        loader = loaders.MercadoLibreCarAdLoader(item=items.CarAd(), response=response)

        loader.add_xpath("title", "//section[@id='short-desc']//header/h1/text()")
        loader.add_value("brand", [brand])
        loader.add_value("model", [model])
        loader.add_value("version", [version])
        loader.add_xpath("year", "//section[@id='short-desc']//article[@class='vip-classified-info']/dl/dd[1]/text()")
        loader.add_xpath("price", "//section[@id='short-desc']//span[@class='price-tag-fraction']/text()")
        loader.add_xpath("currency", "//section[@id='short-desc']//span[@class='price-tag-symbol']/text()")
        loader.add_xpath("km", "//section[@id='short-desc']//article[@class='vip-classified-info']/dl/dd[2]/text()")
        loader.add_value("href", [response.url])
        loader.add_xpath("img", "//div[@id='gallery_dflt']//figure[1]//img/@src")
        loader.add_value("source", [self.name])
        loader.add_value("date", [datetime.today()])

        return loader.load_item()
