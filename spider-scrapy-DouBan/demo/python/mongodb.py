import pymongo

import datetime

myclient = pymongo.MongoClient("mongodb://192.168.110.130:27017/")

db = myclient["tuduweb"]
collection = db["loginDB"]

post = {"author": "Kid",
        "text": "My first blog post!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow(),
        'error': 1}

post_id = collection.insert_one(post).inserted_id

print(post_id)