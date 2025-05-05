from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Koneksi MongoDB (ganti sesuai koneksi Anda)
client = MongoClient("mongodb+srv://SIC6:jmCISIocH7HxL6xg@cluster0.qvi1yfs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Pureindivisum']
collection = db['Byunum']

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.json
    data["timestamp"] = datetime.utcnow()
    collection.insert_one(data)
    return jsonify({"status": "success", "data": data}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
