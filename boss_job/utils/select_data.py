import pymongo


def parse():
    client = pymongo.MongoClient(host='120.79.162.44', port=10086)
    client.admin.authenticate("Leo", "fwwb123456")
    db = client.fwwb
    city_num = db.boss_city_code
    data = city_num.find()
    return data