import functools
import unidecode

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, Compose, TakeFirst

from cars4sale import utils, items

class CarAdLoader(ItemLoader):
    default_output_processor = TakeFirst()

    title_in = MapCompose(str.strip, str.upper, unidecode.unidecode)
    brand_in = MapCompose(str.upper, unidecode.unidecode)
    model_in = MapCompose(str.upper, unidecode.unidecode)
    version_in = MapCompose(str.upper, unidecode.unidecode)

    year_in = MapCompose(int)
    price_in = MapCompose(utils.drop_dot, int)
    km_in = MapCompose(utils.split_and_get, utils.drop_dot, int)
    img_in = MapCompose(utils.drop_url_query, utils.add_url_scheme)

class DeAutosCarAdLoader(CarAdLoader):
    pass

class DeMotoresCarAdLoader(CarAdLoader):
    title_in = MapCompose(functools.partial(utils.split_and_get, at=slice(1,None)), CarAdLoader.title_in)
    title_out = Join()
    year_in = MapCompose(utils.split_and_get, CarAdLoader.year_in)
    price_in = MapCompose(functools.partial(utils.split_and_get, at=-1), CarAdLoader.price_in)
    currency_in = MapCompose(functools.partial(utils.split_and_get, at=slice(0,-1)))
    currency_out = Compose(Join(), lambda k: utils.currency_mappings[k])

class MercadoLibreCarAdLoader(CarAdLoader):
    currency_out = Compose(TakeFirst(), lambda k: utils.currency_mappings[k])

class OlxCarAdLoader(CarAdLoader):
    year_in = MapCompose(utils.split_and_get, CarAdLoader.year_in)
    price_in = MapCompose(str.strip, lambda v: v[1:] if v.startswith('$') else v[3:], CarAdLoader.price_in)
    currency_in = MapCompose(str.strip, lambda v: v[0] if v.startswith('$') else v[:3])
    currency_out = Compose(Join(), lambda k: utils.currency_mappings[k])
    km_in = MapCompose(utils.to_int)
