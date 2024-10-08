from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Configure MongoDB
mongo_client = MongoClient("mongodb://host.docker.internal:27017/")  # Adjust if needed
DB_NAME = "mydb"
COLLECTION_NAME = "mycoll"
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# Create a document
@app.route('/mongo', methods=['POST'])
def create_mongo():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"id": str(result.inserted_id)}), 201

# Read a document
@app.route('/mongo/<id>', methods=['GET'])
def read_mongo(id):
    document = collection.find_one({"_id": ObjectId(id)})
    if document:
        # Convert ObjectId to string
        document['_id'] = str(document['_id'])
        return jsonify(document), 200
    return jsonify({"error": "Document not found"}), 404

# Update a document
@app.route('/mongo/<id>', methods=['PUT'])
def update_mongo(id):
    data = request.json
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.modified_count > 0:
        return jsonify({"modified_count": result.modified_count}), 200
    return jsonify({"error": "Document not found or no changes made"}), 404

# Delete a document
@app.route('/mongo/<id>', methods=['DELETE'])
def delete_mongo(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"deleted_count": result.deleted_count}), 200
    return jsonify({"error": "Document not found"}), 404

@app.route('/')
def index():
    return "Welcome to Flask MongoDB CRUD API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
