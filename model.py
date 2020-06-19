import pymysql
import datetime
import flask
import operator
from mysql import connector
from sqlite3 import OperationalError

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'LoginPass@@12',
    'database': 'DogsTinder'
}

class DBManager():
    connection: pymysql.Connection = None

    @classmethod
    def getConnection(cls):
        return cls.connection
    
    @classmethod
    def getCursor(cls):
        try:
            if not cls.connection or not cls.connection.open:
                cls.connection = pymysql.connect(**db_config)
        except OperationalError:
            cls.connection.close        
        return cls.connection.cursor()


    @classmethod
    def closeConnection(cls):
        if cls.connection and cls.connection.open:
            cls.connection.close()
   
class Message:
    def __init__(self, sender, receiver, content, date:datetime, meeting_proposal):
        self.id = None
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.date = date
        self.meeting_proposal = meeting_proposal

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'content': self.content,
            'date': self.date
        }