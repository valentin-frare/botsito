parameters = {
    "community-link": "http://aminoapps.com/c/a-r-m-ys-forever"
}

from tinydb import TinyDB, Query

db = TinyDB('db.json')

from datetime import datetime
import os
import sys
import time
import json
from hmac import new
import base64
import random
import components
from threading import Thread
import websocket
import traceback

try:
    import requests
    from flask import Flask
    from json_minify import json_minify
    import pytz
except:
    os.system("pip3 install requests flask json_minify pytz")
finally:
    import requests
    from flask import Flask
    from json_minify import json_minify
    import pytz

from hashlib import sha1

style = "<style>body{background-color:#1A374D;margin:0;padding:0;font-family:Arial}.row_container{background-color: #1A374D;color: white;display: flex;align-items: center;}.email{width: 225px;background-color: #406882;box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);padding: 5px;color: white;z-index: 5;}.last_time{text-align: center;width: 180px;background-color: #B1D0E0;color: black;box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);padding: 5px;z-index: 2;}.errors{background-color: #1A374D;color: red;padding: 5px;box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);z-index: 4;}.generations{background-color: #6998AB;color: white;padding: 5px;box-shadow: 11px -1px 21px -10px rgba(0,0,0,1);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,1);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,1);z-index: 4;}.big_error{text-align: center;background-color: #9b0000;border: solid 5px #d50000;border-width: 0px 0px 5px 0px;color: #ffffff;padding: 15px;box-shadow: 0px 11px 47px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 0px 11px 47px -10px rgba(0,0,0,0.75);-moz-box-shadow: 0px 11px 47px -10px rgba(0,0,0,0.75);z-index: 7;}</style>"

def total_coins(array_ret: list) -> int:
    ret = [str(i) for i in array_ret]
    coinsTotal = 0
    for i in range(len(ret)):
        json_content = json.loads(ret[i].replace("'", '"').split("ObservedDict(value=")[1].split("}")[0] + "}")

        coins = 0
        if ret[i].__contains__('coins'):
            try: coins = int(json_content['coins'])
            except: coins = ""

        coinsTotal += coins
    return int(coinsTotal)

def formateo(array_ret: list):
    ret = [str(i) for i in array_ret]
    for i in range(len(ret)):
        email = ""
        if ret[i].split("('"):
            try:
                email = ret[i].split("('")[1].split("', ")[0]
            except:
                email = ""
        generations = ""
        errors = ""
        last_time = ""
        coins = 0

        json_content = json.loads(ret[i].replace("'", '"').split("ObservedDict(value=")[1].split("}")[0] + "}")

        if ret[i].__contains__('generations'):
            try: generations = json_content['generations']
            except: generations = ""
        if ret[i].__contains__('errors'):
            try: errors = json_content['errors']
            except: errors = ""
        if ret[i].__contains__('last-time'):
            try: last_time = json_content['last-time']
            except: last_time = ""
        if ret[i].__contains__('coins'):
            try: coins = json_content['coins']
            except: coins = ""
        ret[i] = f'{components.generations(str(i))}{components.email(email)}'
        if generations: ret[i] += components.generations(generations)
        if errors: ret[i] += components.errors(errors)
        if last_time: ret[i] += components.last_time(last_time)
        if coins: ret[i] += components.generations(str(coins))

    return map(lambda r: components.row_container(r), ret)

flask_app = Flask('')

@flask_app.route('/')
def home():
    if not [i for i in list(db.all()['page_out'].items())]: return 'fzh10vusfl@1secmail.com'
    try:
      return style + components.big_error(f"{db.all()['last_error']} | {db.all()['index']} | TotalCoins: {total_coins(list(db.all()['page_out'].items()))}") + ''.join(formateo(list(db.all()['page_out'].items())))
    except Exception as e:
      return 'fzh10vusfl@1secmail.com' + str(e)

def run(): flask_app.run()

class Client:
    def __init__(self, deviceId=None):
        self.api = "https://service.narvii.com/api/v1"
        self.socket_url = "wss://ws1.narvii.com"
        self.device_Id = self.generate_device_Id() if not deviceId else deviceId
        self.headers = {
    "NDCDEVICEID": self.device_Id,
    "SMDEVICEID":
        "b89d9a00-f78e-46a3-bd54-6507d68b343c",
    "Accept-Language": "en-EN",
    "Content-Type":
        "application/json; charset=utf-8",
    "User-Agent":
        "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)",
    "Host": "service.narvii.com",
    "Accept-Encoding": "gzip",
    "Connection": "Keep-Alive"}
        self.socket_thread, self.sid = None, None
        self.socket, self.auid = None, None

    def ws_send(self, data):
        if self.sid is None: return
        final = f"{self.device_Id}|{int(time.time() * 1000)}"
        ndc_msg_sig = self.generate_signature_message(final)
        headers = {"NDCDEVICEID": self.device_Id, "NDCAUTH": f"sid={self.sid}", "NDC-MSG-SIG": ndc_msg_sig}
        self.socket = websocket.WebSocketApp(f"{self.socket_url}/?signbody={final.replace('|', '%7C')}", header=headers)
        self.socket_thread = Thread(target=self.socket.run_forever)
        self.socket_thread.start()
        time.sleep(4)
        self.socket.send(data)

    def generate_device_Id(self):
        identifier = os.urandom(20)
        mac = new(bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F"), bytes.fromhex("42") + identifier, sha1)
        return f"42{identifier.hex()}{mac.hexdigest()}".upper()

    def generate_signature_message(self, data):
        signature_message = base64.b64encode(bytes.fromhex("42") + new(bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93"),data.encode("utf-8"), sha1).digest()).decode("utf-8")
        self.headers["NDC-MSG-SIG"]=signature_message
        return signature_message

    def login(self, email: str, password: str):
        data = json.dumps({
             "email": email,
             "secret": f"0 {password}",
             "deviceID": self.device_Id,
             "clientType": 100,
             "action": "normal",
             "timestamp": (int(time.time() * 1000))})
        self.generate_signature_message(data = data)
        request = requests.post(f"{self.api}/g/s/auth/login", data=data, headers=self.headers).json()
        try:
            self.sid = request["sid"]
            self.auid = request["auid"]
        except: pass
        return request

    def send_active_object(self, comId: int, start_time: int = None, end_time: int = None, timers: list = None, tz: int = -time.timezone // 1000):
        data = {"userActiveTimeChunkList": [{"start": start_time, "end": end_time}], "timestamp": int(time.time() * 1000), "optInAdsFlags": 2147483647, "timezone": tz}
        if timers: data["userActiveTimeChunkList"] = timers
        data = json_minify(json.dumps(data))
        self.generate_signature_message(data = data)
        request = requests.post(f"{self.api}/x{comId}/s/community/stats/user-active-time?sid={self.sid}", data = data, headers = self.headers)
        return request.json()

    def watch_ad(self): return requests.post(f"{self.api}/g/s/wallet/ads/video/start?sid={self.sid}", headers = self.headers).json()

    def get_from_link(self, link: str): return requests.get(f"{self.api}/g/s/link-resolution?q={link}", headers = self.headers).json()

    def lottery(self, comId, time_zone: str = -int(time.timezone) // 1000):
        data = json.dumps({"timezone": time_zone, "timestamp": int(time.time() * 1000)})
        self.generate_signature_message(data = data)
        request = requests.post(f"{self.api}/x{comId}/s/check-in/lottery?sid={self.sid}", data = data, headers = self.headers)
        return request.json()

    def join_community(self, comId: int, inviteId: str = None):
        data = {"timestamp": int(time.time() * 1000)}
        if inviteId: data["invitationId"] = inviteId
        data = json.dumps(data)
        self.generate_signature_message(data=data)
        request = requests.post(f"{self.api}/x{comId}/s/community/join?sid={self.sid}", data = data, headers = self.headers)
        return request.json()

    def get_coins_count(self):
        custom_headers = self.headers.copy()
        custom_headers.update({'NDCAUTH': f'sid={self.sid}'})
        custom_headers.update({'AUID': f'{self.auid}'})
        response = requests.get(f"{self.api}/g/s/wallet?timezone=-300", headers = custom_headers)
        if response.status_code != 200: raise Exception('torticolis') 
        else: return int(json.loads(response.text)["wallet"]["totalCoins"])

    def show_online(self, comId):
        data = {"o": {
            "actions": ["Browsing"],
            "target": f"ndc://x{comId}/",
            "ndcId": int(comId),
            "id": "82333"}, "t":304}
        data = json.dumps(data)
        time.sleep(1)
        self.ws_send(data)

class App:
    def __init__(self):
        self.client = Client()
        extensions = self.client.get_from_link(parameters["community-link"])["linkInfoV2"]["extensions"]
        self.comId = extensions["community"]["ndcId"]
        try: self.invitationId = extensions["invitationId"]
        except: self.invitationId = None
    def tzc(self):
        zones = ['Etc/GMT-11','Etc/GMT-10','Etc/GMT-9','Etc/GMT-8','Etc/GMT-7','Etc/GMT-6','Etc/GMT-5','Etc/GMT-4','Etc/GMT-3','Etc/GMT-2','Etc/GMT-1','Etc/GMT0','Etc/GMT+1','Etc/GMT+2','Etc/GMT+3','Etc/GMT+4','Etc/GMT+5','Etc/GMT+6','Etc/GMT+7','Etc/GMT+8','Etc/GMT+9','Etc/GMT+10','Etc/GMT+11','Etc/GMT+12']
        for _ in zones:
            H = datetime.datetime.now(pytz.timezone(_)).strftime("%H")
            Z = datetime.datetime.now(pytz.timezone(_)).strftime("%Z")
            if H=="23": break
        return (int(Z) *60)
    def generation(self, email: str, password: str):
        try:
            print(self.client.login(email = email, password = password))
            if not f'{email}' in db.all()["page_out"]: db.update({'coins': 0}, Query().page_out == email)
            #print(f"[\033[1;31mcoins-generator\033[0m][\033[1;36mjoin-community\033[0m]: {self.client.join_community(comId = self.comId, inviteId = self.invitationId)['api:message']}.")
            self.client.lottery(comId = self.comId, time_zone = self.tzc())
            self.client.watch_ad()

            try: db.update({'coins': self.client.get_coins_count()}, Query().page_out == email)
            except: db.update({'coins': 0}, Query().page_out == email)

            for i2 in range(25):
                self.client.send_active_object(comId = self.comId, timers = [{'start': int(time.time()), 'end': int(time.time()) + 300} for _ in range(50)], tz = self.tzc())
                time.sleep(1 + random.uniform(.8, 1.4))
            #print(f"[\033[1;31mcoins-generator\033[0m][\033[1;25;32mend\033[0m][{email}]: Finished.")
            tz = pytz.timezone('America/Buenos_Aires')
            now = datetime.now(tz=tz)
            try:
              db.update({'generations': int(db.all()["page_out"][f'{email}']['generations']) + 1}, Query().page_out == email)
            except:
              db.update({'generations': 1}, Query().page_out == email)
            db.update({'last-time': f'{now.strftime("%d/%m/%Y, %H:%M:%S")}'}, Query().page_out == email)
        except Exception as error:
            tz = pytz.timezone('America/Buenos_Aires')
            now = datetime.now(tz=tz)
            db.update(str(error) + " / " + str(now), Query().page_out == email)
            try:
                db.update({'errors': int(db.all()["page_out"][f'{email}']['errors']) + 1}, Query().page_out == email)
            except:
                db.update({'errors': 1}, Query().page_out == email)
            pass

    def run(self):
        if not 'index' in db.all(): db.update({'index': 0})
        with open("accounts.json", "r") as emails:
            emails = json.load(emails)
            while True:
                try:
                    if db.all()['index'] == len(emails): db.update({'index': 0})
                    for i in range(db.all()['index'], len(emails)):
                        db.update({'index': db.all()['index'] + 1})
                        account = emails[i]
                        self.client.device_Id = account["device"]
                        self.client.headers["NDCDEVICEID"] = self.client.device_Id
                        self.generation(email = account["email"], password = account["password"])
                except Exception as e:
                    os.system('clear')
                    os.execv(sys.executable, ['python'] + sys.argv)


if __name__ == "__main__":
    Thread(target=run).start()
    App().run()
