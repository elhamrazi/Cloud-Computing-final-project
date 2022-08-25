from flask import Flask
from mongoengine import *
from flask_mongoengine import MongoEngine
from datetime import datetime

from flask import Blueprint
from flask_restful import Api

from flask_restful import Resource
from flask import jsonify, request
from flask_api import status
import sys
import hashlib
import datetime
from flask import jsonify, request, redirect

import json


with open('config.json', 'r') as f:
    configs = json.load(f)

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'test',
    'host': configs["db_host"],
    'port': configs["db_port"]
}

db = MongoEngine(app)

api = Api(app)


class URLRep(db.Document):
    shorturl = StringField(max_length=20, null=False, required=True)
    creation_date = DateTimeField(default=datetime.datetime.now(), null=False)
    longurl = StringField(max_length=200, null=False)
    expirationTime = IntField(configs["expiration_time"])
    userId = LongField(default=100000)

    meta = {'collection': 'URLGen',
            'indexes': [
                'shorturl',
                'longurl'
                ]
            }

    def __init__(self, shorturl, longurl,*args, **kwargs):
        super(db.Document, self).__init__(*args, **kwargs)
        self.shorturl = shorturl
        self.longurl = longurl


class URLGen(Resource):

    def get(self):
        shorturl_user = request.args.get('shorturl')
        if shorturl_user is None:
            return "ShortURL input parameter missing", status.HTTP_400_BAD_REQUEST

        desired_documents = URLRep.objects(shorturl=shorturl_user)
        if desired_documents.count() == 0:
            return "No long URL found for input shorturl", status.HTTP_404_NOT_FOUND
        
        responseURLDoc = desired_documents[0]
        print(responseURLDoc['creation_date'])
        now = datetime.datetime.now()
        dur = now - responseURLDoc['creation_date']
        dur_s = dur.total_seconds()
        if dur_s > configs["expiration_time"]:
            return "link expired", status.HTTP_404_NOT_FOUND

        return jsonify(
            {
                "shorturl": responseURLDoc['shorturl'],
                "longurl": responseURLDoc["longurl"],
                "creation_date": responseURLDoc["creation_date"],
                "userId": responseURLDoc["userId"]
            }
        )

    def get_md5_bytes_as_base62(self, urlstring):
        digestStr = hashlib.md5(urlstring.encode('utf-8')).hexdigest()

        # Above is 32 char (2 char per byte so 128 bit hash)

        # Lets take only first 10 digits for shortness
        digestStr = digestStr[:10]

        md5int = int(digestStr, 16)
        # Add current micro seconds to bring uniqueness
        md5int += datetime.datetime.now().microsecond
        return self.base62_encode_i(md5int)

    def base62_encode_i(self, dec):
        s = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ret = ''
        while dec > 0:
            ret = s[dec % 62] + ret
            dec = int(dec/62)
        return ret

    def post(self):
        longurl = request.form['longurl']
        print(longurl)

        # json_data = request.get_json(force=True)
        # longurl = json_data["longurl"]
        shorturl = "http://" + self.get_md5_bytes_as_base62(longurl)

        try:
            #data= paste_schema.loads(request.data)
            urlrep = URLRep(shorturl, longurl)
            urlrep.save()
        except Exception as e:
            return str(e), 422

        return jsonify({"shorturl": shorturl, "longurl": longurl})


class URLRedirect(Resource):
    def get(self):
        shorturlUser = request.args.get('shorturl')
        if shorturlUser is None:
            return "ShortURL input parameter missing", status.HTTP_400_BAD_REQUEST

        desired_documents = URLRep.objects(shorturl=shorturlUser)

        if desired_documents.count() == 0:
            return "No long URL found for input shorturl", status.HTTP_404_NOT_FOUND

        responseURLDoc = desired_documents[0]

        longurl = responseURLDoc["longurl"]
        return redirect(longurl, code=302)


# Route
api.add_resource(URLGen, '/URLGen')
api.add_resource(URLRedirect, '/URLRedirect')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=configs["port"], debug=True)

