from flask import Flask, render_template, request, jsonify
import grpc
import data_pb2_grpc
import data_pb2
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_data():
    data = request.form['data']
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = data_pb2_grpc.DataServiceStub(channel)
            response = stub.AddData(data_pb2.DataRequest(name=data))
            return jsonify({"message": response.message, "success": True})
    except Exception as e:
        return jsonify({"message": str(e), "success": False})

@app.route('/get-data-list')  # Reuse this route for both listing and random fetching
def get_data_list():
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = data_pb2_grpc.DataServiceStub(channel)
            response = stub.GetDataList(data_pb2.DataRequest())  
            data_list = response.message.split(",")
            if not data_list or data_list[0] == "":
                return jsonify({"message": "No data available.", "success": True}) 
            # If 'random' is in the query parameters, return a random item
            if 'random' in request.args:
                random_data = random.choice(data_list)
                return jsonify({"message": random_data, "success": True})
            else:  # Otherwise, return the full list as before
                return jsonify({"message": data_list, "success": True})
    except Exception as e:
        return jsonify({"message": str(e), "success": False})


@app.route('/update', methods=['POST'])
def update_data():
    data = request.json['data']
    new_data = request.json['new_data']
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = data_pb2_grpc.DataServiceStub(channel)
            response = stub.UpdateData(data_pb2.DataRequest(name=data, new_name=new_data))
            return jsonify({"message": response.message, "success": True})
    except Exception as e:
        return jsonify({"message": str(e), "success": False})

@app.route('/delete', methods=['POST'])
def delete_data():
    data = request.json['data']
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = data_pb2_grpc.DataServiceStub(channel)
            response = stub.DeleteData(data_pb2.DataRequest(name=data))
            return jsonify({"message": response.message, "success": True})
    except Exception as e:
        return jsonify({"message": str(e), "success": False})

if __name__ == '__main__':
    app.run(debug=True)
