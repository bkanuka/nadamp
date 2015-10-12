import sys
from flask import Flask, request
from flask_restful import reqparse, Resource, Api, abort

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('vol', type=int)

if len(sys.argv) > 1 and sys.argv[1] == '--debug':
    import logging
    logging.getLogger().setLevel(logging.DEBUG)


from nadamp import Amp
amp = Amp('HarmonyHub', 5222, 'bkanuka@gmail.com', 'password')

class Main(Resource):
    def get(self):
        args = parser.parse_args()

        if args.get('vol', False):
            amp.set_vol(args['temp'])

        r = amp.get_vol()
        return r

api.add_resource(Main, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8052, debug=True, use_reloader=False)
