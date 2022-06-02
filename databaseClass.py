from datetime import datetime
import json
import time
import pytz
import components
from tinydb import TinyDB, Query
import psycopg2

class SqlDatabase:
    def __init__(self, 
                 dbname="dfclo7hjnqt1ah", 
                 user="jafyfpjgcghbvp", 
                 password="ef666820db80ba29d38880df18b26731280d3e0dd3a68c6d06eb5519265625be", 
                 host="ec2-54-204-56-171.compute-1.amazonaws.com", 
                 port="5432") -> None:
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor()
    
    def GetDataFromEmail(self, email: str) -> tuple:
        self.cursor.execute(f"SELECT * FROM Botsitos WHERE email = '{email}';")
        return self.cursor.fetchone()
    
    def UpdateDataOfEmail(self, email: str, data: dict):
        sqlCommand = "UPDATE Botsitos "
        for key in data.keys():
            sqlCommand += f"SET {key} = {data[key]} "
        sqlCommand += f"WHERE email = '{email}'"
        self.cursor.execute(sqlCommand)
        self.connection.commit()
        return True
    
    def AddErrorToEmail(self, email: str):
        sqlCommand = "UPDATE Botsitos "
        sqlCommand += "SET errors = errors + 1 "
        sqlCommand += f"WHERE email = '{email}'"
        self.cursor.execute(sqlCommand)
        self.connection.commit()
        return True
        
    def GetIndex(self) -> int:
        self.cursor.execute("SELECT * FROM Index WHERE id = 4")
        return self.cursor.fetchone()[1]
    
    def AddIndex(self) -> bool:
        self.cursor.execute("SELECT * FROM Index WHERE id = 4")
        index = self.cursor.fetchone()[1]
        self.cursor.execute(f"UPDATE Botsitos SET index = {index + 1} WHERE id = 4")
        self.connection.commit()
        return True
    
    def ResetIndex(self) -> bool:
        self.cursor.execute("UPDATE Botsitos SET index = 0 WHERE id = 4")
        self.connection.commit()
        return True
    
    def GetLastError(self) -> str:
        self.cursor.execute("SELECT * FROM LastError WHERE id = 4")
        return self.cursor.fetchone()[1]
    
    def SetLastError(self, error: str) -> bool:
        self.cursor.execute(f"UPDATE LastError SET lastError = '{error}' WHERE id = 4")
        self.connection.commit()
        return True
    
    def GetAllBotsitos(self) -> list:
        self.cursor.execute("SELECT * FROM Botsitos")
        return self.cursor.fetchall()
    
    def GetAllCoins(self) -> int:
        self.cursor.execute("SELECT (coins) FROM Botsitos")
        wallets = self.cursor.fetchall()
        totalCoins = 0
        for wallet in wallets:
            totalCoins += wallet[0]
        return int(totalCoins)
    
db = SqlDatabase()
print(db.GetAllBotsitos())