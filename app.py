__author__ = 'reisuke'

from flask import Flask
from flask_restful import Resource, Api, reqparse
import base64
import numpy as np
import cv2
from sys import argv

app = Flask(__name__)
api = Api(app)


class ImageConvert(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('data', type=str, required=True)
        self.parser.add_argument('format', type=str, required=True)
        self.container = {}
        super(ImageConvert, self).__init__()

    def post(self):
        args = self.parser.parse_args()
        for key, value in args.items():
            self.container[key] = value

        self.container['data'] = base64.b64decode(self.container['data'])
        grayscaled = self.to_grayscale(self.container['data'], self.container['format'])

        return {'result': grayscaled}

    def to_grayscale(self, bytes_string, file_format):
        """to_grayscale(string, string) => string

        Description:
        Convert RGB image bytes string to grayscale image bytes string.
        To use this function, argument must be an image bytes string
        and file format in string.

        Returns a base64-encoded converted image bytes string.
        """
        numpy_array = np.fromstring(bytes_string, np.uint8)
        image_numpy = cv2.imdecode(numpy_array, cv2.CV_LOAD_IMAGE_COLOR)
        convert = cv2.cvtColor(image_numpy, cv2.COLOR_BGR2GRAY)

        result = cv2.imencode(file_format, convert)[1].tostring()
        return base64.b64encode(result)

api.add_resource(ImageConvert, '/api/imageconverter/v0.1/', endpoint='v0.1')


if __name__ == '__main__':
    argument = argv[1:]
    if len(argument) != 1:
        print "Usage: python app.py [hostname]:[port]"
        print "Example: python app.py localhost:9000"
        exit(2)

    hostname, port = argument[0].split(':')
    app.run(host=hostname, port=int(port), debug=True)