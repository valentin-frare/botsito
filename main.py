parameters = {
    "community-link": "http://aminoapps.com/c/a-r-m-ys-forever"
}
from datetime import datetime
import os
import sys
import time
import json
from hmac import new
import base64
import random
from threading import Thread
import websocket

try:
    import requests
    from json_minify import json_minify
    import pytz
except:
    os.system("pip3 install requests flask json_minify pytz")
finally:
    import requests
    from json_minify import json_minify
    import pytz

from hashlib import sha1

import databaseClass

db = databaseClass.SqlDatabase()

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
        localhour=time.strftime("%H", time.gmtime()); localminute=time.strftime("%M", time.gmtime()); 
        UTC={"GMT0":'+0', "GMT1":'+60', "GMT2":'+120', "GMT3":'+180', "GMT4":'+240', "GMT5":'+300', "GMT6":'+360', "GMT7":'+420', "GMT8":'+480', "GMT9":'+540', "GMT10":'+600', "GMT11":'+660', "GMT12":'+720', "GMT13":'+780', "GMT-1":'-60', "GMT-2":'-120', "GMT-3":'-180',"GMT-4":'-240', "GMT-5":'-300', "GMT-6":'-360', "GMT-7":'-420', "GMT-8":'-480', "GMT-9":'-540', "GMT-10":'-600', "GMT-11":'-660'}; hour = [localhour, localminute]
        if hour[0]=="00":tz=UTC["GMT-1"];return int(tz)
        if hour[0]=="01":tz=UTC["GMT-2"];return int(tz)
        if hour[0]=="02":tz=UTC["GMT-3"];return int(tz)
        if hour[0]=="03":tz=UTC["GMT-4"];return int(tz)
        if hour[0]=="04":tz=UTC["GMT-5"];return int(tz)
        if hour[0]=="05":tz=UTC["GMT-6"];return int(tz)
        if hour[0]=="06":tz=UTC["GMT-7"];return int(tz)
        if hour[0]=="07":tz=UTC["GMT-8"];return int(tz)
        if hour[0]=="08":tz=UTC["GMT-9"];return int(tz)
        if hour[0]=="09":tz=UTC["GMT-10"];return int(tz)
        if hour[0]=="10":tz=UTC["GMT13"];return int(tz)
        if hour[0]=="11":tz=UTC["GMT12"];return int(tz)
        if hour[0]=="12":tz=UTC["GMT11"];return int(tz)
        if hour[0]=="13":tz=UTC["GMT10"];return int(tz)
        if hour[0]=="14":tz=UTC["GMT9"];return int(tz)
        if hour[0]=="15":tz=UTC["GMT8"];return int(tz)
        if hour[0]=="16":tz=UTC["GMT7"];return int(tz)
        if hour[0]=="17":tz=UTC["GMT6"];return int(tz)
        if hour[0]=="18":tz=UTC["GMT5"];return int(tz)
        if hour[0]=="19":tz=UTC["GMT4"];return int(tz)
        if hour[0]=="20":tz=UTC["GMT3"];return int(tz)
        if hour[0]=="21":tz=UTC["GMT2"];return int(tz)
        if hour[0]=="22":tz=UTC["GMT1"];return int(tz)
        if hour[0]=="23":tz=UTC["GMT0"];return int(tz)
    def generation(self, email: str, password: str):
        try:
            self.client.login(email = email, password = password)
            #print(f"[\033[1;31mcoins-generator\033[0m][\033[1;36mjoin-community\033[0m]: {self.client.join_community(comId = self.comId, inviteId = self.invitationId)['api:message']}.")
            self.client.lottery(comId = self.comId, time_zone = self.tzc())
            self.client.watch_ad()

            db.UpdateDataOfEmail(email, {'coins': self.client.get_coins_count()})

            for i2 in range(25):
                print(self.client.send_active_object(comId = self.comId, timers = [{'start': int(time.time()), 'end': int(time.time()) + 300} for _ in range(50)], tz = self.tzc()))
                time.sleep(1 + random.uniform(.8, 1.4))
            #print(f"[\033[1;31mcoins-generator\033[0m][\033[1;25;32mend\033[0m][{email}]: Finished.")
            tz = pytz.timezone('America/Buenos_Aires')
            now = datetime.now(tz=tz)
            db.UpdateDataOfEmail(email, {'generations': "generations + 1"})
            db.UpdateDataOfEmail(email, {'last-time': f'\'{now.strftime("%d/%m/%Y, %H:%M:%S")}\''})
        except Exception as error:
            print(error)
            tz = pytz.timezone('America/Buenos_Aires')
            now = datetime.now(tz=tz)
            db.SetLastError(str(error) + " / " + str(now))
            db.AddErrorToEmail(email)

    def run(self):
        with open("accounts.json", "r") as emails:
            emails = json.load(emails)
            while True:
                try:
                    if db.GetIndex() == len(emails): db.ResetIndex()
                    for i in range(db.GetIndex(), len(emails)):
                        db.AddIndex()
                        account = emails[i]
                        self.client.device_Id = account["device"]
                        self.client.headers["NDCDEVICEID"] = self.client.device_Id
                        self.generation(email = account["email"], password = account["password"])
                except Exception as e:
                    os.system('clear')
                    os.execv(sys.executable, ['python'] + sys.argv)


if __name__ == "__main__":
    App().run()
