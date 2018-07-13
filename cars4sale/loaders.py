import functools
from scrapy.loader.processors import MapCompose, Join, Compose, TakeFirst

from cars4sale import utils, items

class DeAutosCarAdLoader(items.CarAdLoader):
    pass

class DeMotoresCarAdLoader(items.CarAdLoader):
    title_in = MapCompose(functools.partial(utils.split_and_get, at=slice(1,None)), items.CarAdLoader.title_in)
    title_out = Join()
    year_in = MapCompose(utils.split_and_get, items.CarAdLoader.year_in)
    price_in = MapCompose(functools.partial(utils.split_and_get, at=-1), items.CarAdLoader.price_in)
    currency_in = MapCompose(functools.partial(utils.split_and_get, at=slice(0,-1)))
    currency_out = Compose(Join(), lambda k: utils.currency_mappings[k])

class MercadoLibreCarAdLoader(items.CarAdLoader):
    currency_out = Compose(TakeFirst(), lambda k: utils.currency_mappings[k])

class OlxCarAdLoader(items.CarAdLoader):
    year_in = MapCompose(utils.split_and_get, items.CarAdLoader.year_in)
    price_in = MapCompose(str.strip, lambda v: v[1:] if v.startswith('$') else v[3:], items.CarAdLoader.price_in)
    currency_in = MapCompose(str.strip, lambda v: v[0] if v.startswith('$') else v[:3])
    currency_out = Compose(Join(), lambda k: utils.currency_mappings[k])
    km_in = MapCompose(utils.to_int)
