from flask import Blueprint, Response, jsonify, g, request
from bson import json_util, son
from flask_pymongo import pymongo

import pandas as pd

from .utils import build_query, outliers_modified_z_score, outliers_iqr

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/brands', methods=['GET'])
def get_brands():
    return jsonify({'brands': g.db.ads.distinct("brand")})

@bp.route('/brands/<brand>/models', methods=['GET'])
def get_models(**kwargs):
    return jsonify({'models': g.db.ads.distinct("model", build_query(**kwargs))})

@bp.route('/brands/<brand>/models/<model>/versions', methods=['GET'])
def get_versions(**kwargs):
    return jsonify({'versions': g.db.ads.distinct("version", build_query(**kwargs))})

@bp.route('/brands/<brand>/ads', methods=['GET'])
@bp.route('/brands/<brand>/models/<model>/ads', methods=['GET'])
@bp.route('/brands/<brand>/models/<model>/versions/<version>/ads', methods=['GET'])
def get_ads(**kwargs):
    limit = request.args.get('limit', default=0, type=int)
    offset = max(0, request.args.get('offset', default=0, type=int))
    sort_by = request.args.get('sort_by', default='_id')
    sort_dir = request.args.get('sort_dir', default='ASC')

    ads = g.db.ads.find(build_query(**kwargs), projection={"_id": 0, "date": 0})\
                  .sort(sort_by, pymongo.ASCENDING if sort_dir == 'ASC' else pymongo.DESCENDING)\
                  .limit(limit)\
                  .skip(offset)

    return Response(json_util.dumps({'ads': ads}),
                    status=200,
                    mimetype='application/json')

@bp.route('/brands/<brand>/grouped_ads', methods=['GET'])
@bp.route('/brands/<brand>/models/<model>/grouped_ads', methods=['GET'])
@bp.route('/brands/<brand>/models/<model>/versions/<version>/grouped_ads', methods=['GET'])
def get_grouped_ads(**kwargs):
    agg = g.db.ads.aggregate([{
        '$match': build_query(**kwargs)
    }, {
        '$group': {
            '_id': {
                'brand': '$brand',
                'model': '$model',
                'year' : '$year'
            },
            'ads': {
                '$push': {
                    'version' : '$version',
                    'title'   : '$title',
                    'price'   : '$price',
                    'currency': '$currency',
                    'km'      : '$km',
                    'href'    : '$href',
                    'img'     : '$img',
                    'source'  : '$source'
                }
            }
        }
    }, {
        '$sort': son.SON([('_id.year', -1), ('_id.brand', 1), ('_id.model', 1)])
    }])

    filter_outliers = request.args.get('filter_outliers', 1, type=int)
    if filter_outliers:
        output = []
        for group in agg:
            ads = pd.DataFrame(group['ads'])
            ads = ads.loc[~outliers_modified_z_score(ads.price)]
            ads = ads.loc[~outliers_iqr(ads.price)]
            ads = ads[(ads.price >= ads.price.quantile(0.05)) & (ads.price <= ads.price.quantile(0.95))]

            output.append({'_id': group['_id'], 'ads': ads.to_dict('records')})

        return jsonify({'groups': output})

    return Response(json_util.dumps({'groups': agg}),
                    status=200,
                    mimetype='application/json')
