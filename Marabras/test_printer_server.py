# initialization
import json, requests
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/": {"origins": "*"}})

app.config['CORS_HEADERS'] = ["Content-Type", "Access-Control-Allow-Origin"]

@app.route('/', methods=['POST','OPTIONS', 'GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def foo():
    print('POST recebido')
    response_json = request.json
    with open('visita_en_visita.json', 'w') as f:
        json.dump(response_json, f, indent=2)

    #response_json["visit"]["lang"] = 'pt-BR'
    print(json.dumps(response_json, indent=2, sort_keys=True))
    print(response_json["visit"]["countryCode"], response_json["visit"]["lang"])
    
    # print_post = requests.post('http://172.16.17.191:7677/api/reports', json=response_json)
    # print(f'{print_post.status_code} - {print_post.reason}')

    #response = jsonify(response_json)
    
    return response_json

if __name__ == '__main__':
    app.debug = True
    app.run(host="172.16.17.191")