from flask_pymongo import MongoClient
import os
db = MongoClient(os.environ["MONGO_URI"])
def is_user_valid(username:str):
    user = db["users"]["user-data"].find_one({"username":username.lower()})
    if user is None:
        return False
    else:
        return True

def find_user(username:str):
    return db["users"]["user-data"].find_one({"username":username.lower()})
def find_company(company_id:str):
    data = db["users"]["user-data"].find_one({"company_id":company_id})
    data.pop("_id", None)
    data.pop("username", None)
    data.pop("password", None)

    return data

if __name__ =="__main__":
    print(is_user_valid("Lakme"))