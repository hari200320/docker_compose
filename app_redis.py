from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

# Configure Redis
redis_client = redis.StrictRedis(host='host.docker.internal', port=6379, db=0)  
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


# Create a key-value pair
@app.route('/redis', methods=['POST'])
def create_redis():
    data = request.json
    key = data.get('key')
    value = data.get('value')
    redis_client.set(key, value)
    return jsonify({"key": key, "value": value}), 201

# Read a value by key
@app.route('/redis/<key>', methods=['GET'])
def read_redis(key):
    value = redis_client.get(key)
    if value:
        return jsonify({"key": key, "value": value.decode('utf-8')}), 200
    return jsonify({"error": "Key not found"}), 404

# Update a value by key
@app.route('/redis/<key>', methods=['PUT'])
def update_redis(key):
    data = request.json
    value = data.get('value')
    redis_client.set(key, value)
    return jsonify({"key": key, "value": value}), 200

# Delete a key-value pair
@app.route('/redis/<key>', methods=['DELETE'])
def delete_redis(key):
    result = redis_client.delete(key)
    if result:
        return jsonify({"deleted": key}), 200
    return jsonify({"error": "Key not found"}), 404

@app.route('/')
def index():
    return "Welcome to Flask Redis CRUD API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
