import components
from flask import Flask
import databaseClass

style = "<style>body{background-color:#1A374D;margin:0;padding:0;font-family:Arial}.row_container{background-color: #1A374D;color: white;display: flex;align-items: center;}.email{width: 225px;background-color: #406882;box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);padding: 5px;color: white;z-index: 5;}.last_time{text-align: center;width: 180px;background-color: #B1D0E0;color: black;box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);padding: 5px;z-index: 2;}.errors{background-color: #1A374D;color: red;padding: 5px;box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,0.75);z-index: 4;}.generations{background-color: #6998AB;color: white;padding: 5px;box-shadow: 11px -1px 21px -10px rgba(0,0,0,1);-webkit-box-shadow: 11px -1px 21px -10px rgba(0,0,0,1);-moz-box-shadow: 11px -1px 21px -10px rgba(0,0,0,1);z-index: 4;}.big_error{text-align: center;background-color: #9b0000;border: solid 5px #d50000;border-width: 0px 0px 5px 0px;color: #ffffff;padding: 15px;box-shadow: 0px 11px 47px -10px rgba(0,0,0,0.75);-webkit-box-shadow: 0px 11px 47px -10px rgba(0,0,0,0.75);-moz-box-shadow: 0px 11px 47px -10px rgba(0,0,0,0.75);z-index: 7;}</style>"

def total_coins(array_ret: list) -> int:
    ret = array_ret
    coinsTotal = 0
    for i in range(len(ret)):
        json_content = ret[i][1]
        coins = int(json_content['coins'])
        coinsTotal += coins
    return int(coinsTotal)

def formateo(array_ret: list):
    ret = array_ret
    for i in range(len(ret)):
        email = ret[i][1]
        generations = ret[i][2]
        last_time = ret[i][2]
        coins = ret[i][3]
        errors = ret[i][4]
        
        ret[i] = f'{components.generations(str(i))}{components.email(email)}'
        ret[i] += components.generations(generations)
        ret[i] += components.errors(errors)
        ret[i] += components.last_time(last_time)
        ret[i] += components.generations(str(coins))

    return map(lambda r: components.row_container(r), ret)

flask_app = Flask('')

@flask_app.route('/')
def home():
    try:
        db = databaseClass.SqlDatabase()
        return style + components.big_error(f"{db.GetLastError()} | {db.GetIndex()} | TotalCoins: {db.GetAllCoins()}") + ''.join(formateo(list(db.GetAllBotsitos())))
    except Exception as e:
        return 'fzh10vusfl@1secmail.com' + str(e)

def run(): flask_app.run()

if __name__ == "__main__":
    run()
