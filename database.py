from pymongo import MongoClient
from threading import Lock


class Database:
    db = None
    instance = None
    lock = Lock()

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.voicebot

    @staticmethod
    def get_instance():
        Database.lock.acquire()
        if Database.instance is None:
            Database.instance = Database()
        Database.lock.release()
        return Database.instance


db = Database.get_instance().db