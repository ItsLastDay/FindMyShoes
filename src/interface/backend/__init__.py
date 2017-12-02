from flask import Flask
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS
from collections import defaultdict

# https://stackoverflow.com/a/6098238/5338270
import sys, os, inspect, os.path
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
indexing_folder = os.path.abspath(os.path.join(cmd_folder, os.pardir, os.pardir, 'indexing'))
sys.path.append(indexing_folder)
from searcher import QueryProcessor
from index_reader import IndexReader
from index_builder import IndexBuilder
data_folder = os.path.abspath(os.path.join(cmd_folder, os.pardir, os.pardir, os.pardir, 'data', 'index'))


app = Flask(__name__)
CORS(app)
api = Api(app)

api_base_url = '/api/v1'

# TODO move into run_backend.py or another separate file.
class Search(Resource):
    def __init__(self):
        index_reader = IndexReader(os.path.join(data_folder, 'inverted.bin'), 
                os.path.join(data_folder, 'weight.bin'),
                os.path.join(data_folder, 'dictionary.txt'))
        # Dirty!
        index_reader.__enter__()
        self._query_processor = QueryProcessor(index_reader, os.path.join(data_folder, os.pardir, 'json'))
        super(Search, self).__init__()

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q')
        parser.add_argument('page')
        query_string = parser.parse_args()

        print(query_string)
        total_num, best_results, best_results_coincidence = self._query_processor.get_ranked_docs(
            query_string['q'],
            page=int(query_string['page'])
        )

        # TODO Retrieve document info from mongo.
        best_results = list(map(lambda x, c: {
            'url': x[0].url,
            'name': x[0].name,
            'price': x[0].price,
            'sizes': x[0].sizes,
            'image': x[0].image,
            'confidence': x[1],
            'coincidence': c,
            }, best_results, best_results_coincidence))
        # print(best_results)

        return [total_num, best_results]
        

api.add_resource(Search, api_base_url + '/search')
