from flask import Flask,request, jsonify
from data_sotre import data

app = Flask(__name__)


@app.route('/data', methods=['GET'])
def get_data():
    name = request.args.get('name','')
    for client in data["clients"]:
        if client["Name"]==name:
            id=client["Account"]
    return jsonify([id]), 200


app.run()