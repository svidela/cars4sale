# -*- coding: utf-8 -*-
import os
import functools
import scrapy
from datetime import datetime

from cars4sale import loaders, items

class DemotoresSpider(scrapy.Spider):
    name = "demotores"
    start_urls = [
        'http://demotores.com.ar/autos/'
    ]

    def _brands_sel(self, response):
        nav = response.xpath("//ul[contains(@class,'listing-navigation')]")
        return nav.xpath("./li[contains(@class,'cs-inav__filter--marca')]//div[contains(@class,'form-group facet')]")

    def _models_sel(self, response):
        brands_sel = self._brands_sel(response)
        return brands_sel.xpath("./div[contains(@class,'checked')]/div[2]/div[@class='filter-group']")

    def _versions_sel(self, response):
        models_sel = self._models_sel(response)
        return models_sel.xpath(".//div[contains(@class,'checked')]/div[2]/div[@class='filter-group']")

    def parse(self, response):
        for brand in self._brands_sel(response).xpath(".//a"):
            if brand.xpath("./label/text()").extract_first() != 'Otra Marca':
                href = response.urljoin(brand.xpath("@href").extract_first())
                yield scrapy.Request(href, callback=self.parse_models)

    def parse_models(self, response):
        for model in self._models_sel(response).xpath(".//a"):
            if model.xpath("./label/text()").extract_first() != "Otro Modelo":
                href = response.urljoin(model.xpath("@href").extract_first())
                yield scrapy.Request(href, callback=self.parse_versions)

    def parse_versions(self, response):
        for version in self._versions_sel(response).xpath(".//a"):
            if version.xpath("./label/text()").extract_first() != 'Otra Versión':
                href = response.urljoin(version.xpath("@href").extract_first())
                yield scrapy.Request(href, callback=self.parse_ads)

    def parse_ads(self, response):
        brand, model, version = self._brands_sel(response).xpath("./div[contains(@class,'checked')]/div/a/label/text()").extract()
        ads = response.xpath("//div[@id='listing-items']/div[contains(@class,'listing-item')]/div/div[1]//h4/a/@href")
        for ad in ads:
            cb = functools.partial(self.parse_ad, brand, model, version)
            yield scrapy.Request(response.urljoin(ad.extract()), callback=cb)

        next_page = response.xpath("//div[contains(@class,'pagination-container')]//ul/li[@class='pagination__btn-next']/a/@href").extract_first()
        if next_page is not None:
            cars_page = response.urljoin(next_page)
            yield scrapy.Request(cars_page, callback=self.parse_ads)

    def parse_ad(self, brand, model, version, response):
        loader = loaders.DeMotoresCarAdLoader(item=items.CarAd(), response=response)

        loader.add_xpath("title", "//h2[@class='content-details__title']/text()")
        loader.add_value("brand", [brand])
        loader.add_value("model", [model])
        loader.add_value("version", [version])
        loader.add_xpath("year", "//h2[@class='content-details__title']/text()")
        loader.add_xpath("price", "//h3[@class='price']/text()")
        loader.add_xpath("currency", "//h3[@class='price']/text()")
        loader.add_xpath("km", "//ul[@class='key-features-list']/li[2]/text()")
        loader.add_value("href", [response.url])
        loader.add_xpath("img", "//div[@id='vehicle-gallery-slider']//a/img/@src")
        loader.add_value("source", [self.name])
        loader.add_value("date", [datetime.today()])

        return loader.load_item()
