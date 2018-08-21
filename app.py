from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat
import logging
import requests
import random
import datetime

app = Flask(__name__)
api = Api(app)

def ranSrc():
    src = [{"MonitorPhase":"Createitem","IsDelay":"True","DelayCount":"1"},{"MonitorPhase":"Inventory","IsDelay":"False","DelayCount":"0"}]
    x0 = random.randint(0,1)
    x1 = random.randint(0,1)
    y0 = "True" if x0 else "False"
    y1 = "True" if x1 else "False"
    src[0]["IsDelay"] = y0
    src[1]["IsDelay"] = y1
    src[0]["DelayCount"] = str(x0)
    src[1]["DelayCount"] = str(x1)
    return src

def sendMessage(mes,cha="integration_test"):
    rocket = RocketChat('aw5p', '@lexis1437', server_url='https://chat.newegg.org')
    pprint(rocket.me().json())
    pprint(rocket.channels_list().json())
    pprint(rocket.chat_post_message(mes, channel=cha, alias='AlertBot').json())

class AlertAPI(Resource):
    def post(self):
        # hardcode source
        src = [{"MonitorPhase":"Createitem","IsDelay":"True","DelayCount":"1"},{"MonitorPhase":"Inventory","IsDelay":"False","DelayCount":"0"}]
        if (int(src[0]["DelayCount"])+int(src[1]["DelayCount"])):
            title = "CI: "+src[0]["DelayCount"]+" ,I: "+src[1]["DelayCount"]
            text = src[0]["MonitorPhase"]+"__IsDelay: "+src[0]["IsDelay"]+", DelayCount = "+src[0]["DelayCount"]+"\n"+src[1]["MonitorPhase"]+"__IsDelay: "+src[1]["IsDelay"]+", DelayCount = "+src[1]["DelayCount"]
            sendMessage(text)
            return "success"
        return "fail"

parser = reqparse.RequestParser()
parser.add_argument('n', type=int)

class Test(Resource):
    lastRecord = {}

    def post(self):
        src = ranSrc()
        totalDelay = 0
        text = ""
        
        """
        now = datetime.datetime.now()
        if now.minute == 0:
            text += "Top of the hour Alert\n"
            for phase in src:
                text += phase["MonitorPhase"]+"-Delay Count = "+phase["DelayCount"]+"\n"
                self.lastRecord[phase["MonitorPhase"]] = phase["DelayCount"]
                totalDelay += int(phase["DelayCount"])
            sendMessage(text)
            return
        """

        for phase in src:
            try:
                if self.lastRecord[phase["MonitorPhase"]] !="0" or phase["IsDelay"] == "True":
                    text += phase["MonitorPhase"]+"-Delay Count = "+phase["DelayCount"]+"\n"
                self.lastRecord[phase["MonitorPhase"]] = phase["DelayCount"]
                totalDelay += int(phase["DelayCount"])
            except:
                if phase["IsDelay"] == "True":
                    text += phase["MonitorPhase"]+"-Delay Count = "+phase["DelayCount"]+"\n"
                self.lastRecord[phase["MonitorPhase"]] = phase["DelayCount"]
                totalDelay += int(phase["DelayCount"])
        return if totalDelay == 0 else sendMessage(text)
        return self.lastRecord

api.add_resource(Test, '/api/Alert')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5200)
