import os
import scrapy
from datetime import datetime

from cars4sale import loaders, items

class DeAutosSpider(scrapy.Spider):
    name = "deautos"
    start_urls = [
        'http://listado.deautos.com/autos/'
    ]

    def parse(self, response):
        for brand in response.xpath("//div[contains(@class,'marca')]/ul/li/a/@href"):
            yield scrapy.Request(response.urljoin(brand.extract()), callback=self.parse_models)

    def parse_models(self, response):
        for model in response.xpath("//div[contains(@class,'modelo')]/ul/li/a/@href"):
            yield scrapy.Request(response.urljoin(model.extract()), callback=self.parse_versions)

    def parse_versions(self, response):
        for version in response.xpath("//div[contains(@class,'version')]/ul/li/a"):
            if version.xpath("@title").extract_first() != 'No Especifica':
                href = version.xpath("@href").extract_first()
                yield scrapy.Request(response.urljoin(href), callback=self.parse_ads)

    def parse_ads(self, response):
        for ad in response.xpath("//ul[@class='publication-list']/li/div[@class='data-container']"):
            if ad.xpath("./div[@class='price']/span/text()").extract_first() != 'A consultar':
                href = ad.xpath("./div[@class='model-brand']/a/@href").extract_first()
                yield scrapy.Request(response.urljoin(href), callback=self.parse_ad)

        next_page = response.xpath("//ul/li/a[contains(.//text(), 'Siguiente')]/@href").extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_ads)

    def parse_ad(self, response):
        loader = loaders.DeAutosCarAdLoader(item=items.CarAd(), response=response)
        base_xpath = "//div[@class='first-info']/div[contains(@class,'car-info')]"

        loader.add_xpath("title", base_xpath + "//meta[@itemprop='name']/@content")
        loader.add_xpath("brand", base_xpath + "//div[contains(@class,'car-model')]/span/span/text()")
        loader.add_xpath("model", base_xpath + "//div[contains(@class,'car-model')]/span[2]/text()")
        loader.add_xpath("version", base_xpath + "//div[contains(@class,'car-version')]/span/text()")
        loader.add_xpath("year", base_xpath + "//div[contains(@class,'data')]/span[2]/text()")
        loader.add_xpath("price", base_xpath + "//div[contains(@class,'price')]/meta[@itemprop='price']/@content")
        loader.add_xpath("currency", base_xpath + "//div[contains(@class,'price')]/meta[@itemprop='priceCurrency']/@content")
        loader.add_xpath("km", base_xpath + "//div[contains(@class,'data')]/span[3]/text()")
        loader.add_value("href", [response.url])
        loader.add_xpath("img", "//div[@id='main-carousel-vip']//img/@data-src")
        loader.add_xpath("img", "//div[@id='main-carousel-vip']//img/@src")
        loader.add_value("source", [self.name])
        loader.add_value("date", [datetime.today()])

        return loader.load_item()
