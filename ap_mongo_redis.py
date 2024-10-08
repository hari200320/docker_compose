from flask import Flask, request, jsonify
import redis
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Configure Redis
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
redis_client = redis.StrictRedis(host='host.docker.internal', port=6379, db=0)
# Configure MongoDB
mongo_client = MongoClient("mongodb://host.docker.internal:27017/")
# mongo_client = MongoClient("mongodb://localhost:27017/")

DB_NAME = "mydb"
COLLECTION_NAME = "mycoll"
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# CRUD operations for both Redis and MongoDB

@app.route('/data', methods=['POST'])
def create_data():
    data = request.json
    key = data.get('key')
    value = data.get('value')

    # Save to Redis
    redis_client.set(key, value)

    # Save to MongoDB
    mongo_data = {"key": key, "value": value}
    result = collection.insert_one(mongo_data)

    return jsonify({
        "message": "Data saved in both Redis and MongoDB",
        "redis": {"key": key, "value": value},
        "mongo_id": str(result.inserted_id)
    }), 201

@app.route('/data/<key>', methods=['GET'])
def read_data(key):
    # First try to get the value from Redis
    value = redis_client.get(key)
    if value:
        return jsonify({
            "key": key,
            "value": value.decode('utf-8'),
            "source": "Redis"
        }), 200
    
    # If not found in Redis, try to get it from MongoDB
    document = collection.find_one({"key": key})
    if document:
        document['_id'] = str(document['_id'])  # Convert ObjectId to string
        # Optionally, you can cache the MongoDB result in Redis
        redis_client.set(key, document['value'])
        return jsonify({
            "key": document['key'],
            "value": document['value'],
            "source": "MongoDB"
        }), 200
    
    return jsonify({"error": "Key not found in both Redis and MongoDB"}), 404

@app.route('/data/<key>', methods=['PUT'])
def update_data(key):
    data = request.json
    value = data.get('value')
    
    # Update in Redis
    redis_client.set(key, value)

    # Update in MongoDB
    result = collection.update_one({"key": key}, {"$set": {"value": value}})
    if result.modified_count > 0:
        return jsonify({"key": key, "value": value}), 200
    return jsonify({"error": "Key not found or no changes made"}), 404

@app.route('/data/<key>', methods=['DELETE'])
def delete_data(key):
    # Delete from Redis
    redis_result = redis_client.delete(key)
    
    # Delete from MongoDB
    mongo_result = collection.delete_one({"key": key})

    if redis_result or mongo_result.deleted_count > 0:
        return jsonify({"deleted": key}), 200
    return jsonify({"error": "Key not found in both Redis and MongoDB"}), 404

@app.route('/')
def index():
    return "Welcome to Flask Redis and MongoDB CRUD API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
