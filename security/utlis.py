from flask_pymongo import MongoClient
import os
db = MongoClient(os.environ["MONGO_URI"])
def is_user_valid(username:str):
    user = db["users"]["user-data"].find_one({"username":username})
    if user is None:
        return False
    else:
        return True
    
if __name__ =="__main__":
    print(is_user_valid("Lakme"))