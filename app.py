from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from pprint import pprint
import logging
import requests

app = Flask(__name__)
api = Api(app)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

class RocketException(Exception):
    pass


class RocketConnectionException(Exception):
    pass


class RocketAuthenticationException(Exception):
    pass


class RocketMissingParamException(Exception):
    pass



class RocketChat:
    headers = {}
    API_path = '/api/v1/'

    def __init__(self, user=None, password=None, server_url='http://127.0.0.1:3000', ssl_verify=True, proxies=None,
                 timeout=30):
        """Creates a RocketChat object and does login on the specified server"""
        self.server_url = server_url
        self.proxies = proxies
        self.ssl_verify = ssl_verify
        self.timeout = timeout
        if user and password:
            self.login(user, password)

    @staticmethod
    def __reduce_kwargs(kwargs):
        if 'kwargs' in kwargs:
            for arg in kwargs['kwargs'].keys():
                kwargs[arg] = kwargs['kwargs'][arg]

            del kwargs['kwargs']
        return kwargs

    def __call_api_get(self, method, **kwargs):
        args = self.__reduce_kwargs(kwargs)
        return requests.get(self.server_url + self.API_path + method + '?' +
                            '&'.join([i + '=' + str(args[i])
                                      for i in args.keys()]),
                            headers=self.headers,
                            verify=self.ssl_verify,
                            proxies=self.proxies,
                            timeout=self.timeout
                            )

    def __call_api_post(self, method, files=None, use_json=True, **kwargs):
        reduced_args = self.__reduce_kwargs(kwargs)
        # Since pass is a reserved word in Python it has to be injected on the request dict
        # Some methods use pass (users.register) and others password (users.create)
        if 'password' in reduced_args and method != 'users.create':
            reduced_args['pass'] = reduced_args['password']
        if use_json:
            return requests.post(self.server_url + self.API_path + method,
                                 json=reduced_args,
                                 files=files,
                                 headers=self.headers,
                                 verify=self.ssl_verify,
                                 proxies=self.proxies,
                                 timeout=self.timeout
                                 )
        else:
            return requests.post(self.server_url + self.API_path + method,
                                 data=reduced_args,
                                 files=files,
                                 headers=self.headers,
                                 verify=self.ssl_verify,
                                 proxies=self.proxies,
                                 timeout=self.timeout
                                 )

    def login(self, user, password):
        login_request = requests.post(self.server_url + self.API_path + 'login',
                                      data={'username': user,
                                            'password': password},
                                      verify=self.ssl_verify,
                                      proxies=self.proxies)
        if login_request.status_code == 401:
            raise RocketAuthenticationException()

        if login_request.status_code == 200:
            if login_request.json().get('status') == "success":
                self.headers['X-Auth-Token'] = login_request.json().get('data').get('authToken')
                self.headers['X-User-Id'] = login_request.json().get('data').get('userId')
                return login_request
            else:
                raise RocketAuthenticationException()
        else:
            raise RocketConnectionException()

    def me(self, **kwargs):
        """	Displays information about the authenticated user."""
        return self.__call_api_get('me', kwargs=kwargs)

    def chat_post_message(self, text, room_id=None, channel=None, attachments=None, **kwargs):
        """Posts a new chat message."""
        if room_id:
            return self.__call_api_post('chat.postMessage', roomId=room_id, text=text, attachments=attachments, kwargs=kwargs)
        elif channel:
            return self.__call_api_post('chat.postMessage', channel=channel, text=text, attachments=attachments, kwargs=kwargs)
        else:
            raise RocketMissingParamException('roomId or channel required')
    def channels_list(self, **kwargs):
        """Retrieves all of the channels from the server."""
        return self.__call_api_get('channels.list', kwargs=kwargs)



def sendMessage(mes,attachments,cha="integration_test"):
    rocket = RocketChat('aw5p', '@lexis1437', server_url='https://chat.newegg.org')
    pprint(rocket.me().json())
    pprint(rocket.channels_list().json())
    pprint(rocket.chat_post_message(mes, channel=cha, alias='AlertBot', attachments=attachments).json())

class AlertAPI(Resource):
    def post(self):
        # hardcode source
        src = [{"MonitorPhase":"Createitem","IsDelay":"True","DelayCount":"1"},{"MonitorPhase":"Inventory","IsDelay":"False","DelayCount":"0"}]
        if (int(src[0]["DelayCount"])+int(src[1]["DelayCount"])):
            title = "CI: "+src[0]["DelayCount"]+" ,I: "+src[1]["DelayCount"]
            text = src[0]["MonitorPhase"]+"__IsDelay: "+src[0]["IsDelay"]+", DelayCount = "+src[0]["DelayCount"]+"\n"+src[1]["MonitorPhase"]+"__IsDelay: "+src[1]["IsDelay"]+", DelayCount = "+src[1]["DelayCount"]
            att = {}
            att["title"] = title
            att["text"] = text
            att["color"] = "#FF8800"
            att = [att]
            sendMessage("Alert", att)
            return "success"
        return "fail"

api.add_resource(AlertAPI, '/api/alert')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5200)
