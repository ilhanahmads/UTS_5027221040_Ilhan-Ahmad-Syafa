import grpc
import concurrent.futures
import random
import time
import data_pb2
import data_pb2_grpc
from pymongo import MongoClient
import random

client = MongoClient('mongodb://localhost:27017/')
db = client['randompicker']
collection = db['use']

class DataService(data_pb2_grpc.DataServiceServicer):

    def AddData(self, request, context):
        data = {'name': request.name}
        collection.insert_one(data)
        return data_pb2.DataResponse(message="Data added successfully.")

    def GetData(self, request, context):
        if collection.count_documents({}) == 0:
            return data_pb2.DataResponse(message="No data available.")
        else:
            data = list(collection.find())
            selected_data = random.choice(data)['name']
            return data_pb2.DataResponse(message=selected_data)

    def UpdateData(self, request, context):
        query = {'name': request.name}
        new_values = {"$set": {'name': request.new_name}}
        result = collection.update_one(query, new_values)
        if result.modified_count > 0:
            return data_pb2.DataResponse(message="Data updated successfully.")
        else:
            return data_pb2.DataResponse(message="Data not found.")

    def DeleteData(self, request, context):
        query = {'name': request.name}
        result = collection.delete_one(query)
        if result.deleted_count > 0:
            return data_pb2.DataResponse(message="Data deleted successfully.")
        else:
            return data_pb2.DataResponse(message="Data not found.")

    def GetDataList(self, request, context):
        data = list(collection.find())
        data_names = [item['name'] for item in data]
        return data_pb2.DataResponse(message=", ".join(data_names))

def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    data_pb2_grpc.add_DataServiceServicer_to_server(DataService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
