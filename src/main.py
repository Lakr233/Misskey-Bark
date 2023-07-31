#
# main.py
# misskey-bark
#
# Created by @Lakr233 on 2023/01/15
#

import os
import re
import sys
import json
import signal

import socketserver
import http.server

from bark import Bark
def terminate(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, terminate)

print("[*] misskey-bark v0.0.1")
print("[*] by @Lakr233")


script_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_path, "../config/config.json")

config = {}
print("[*] load config at %s" % config_path)
with open(config_path, "r") as f:
    str = f.read()
    config = json.loads(str)

config_bark = config['bark']

bark = Bark(config_bark)

key = config['misskey']['key']
port = int(config['server']['port'])
path = config['server']['path']
print("[*] start server on port %d" % port)
print("[*] path: %s" % path)

posted_events = {}

class MisskeyBarkHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")

    def do_POST(self):
        if self.path != path:
            self.send_error(404)
            return
        if self.headers['x-misskey-hook-secret'] != key:
            self.send_error(403)
            return

        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        data_object = json.loads(data)

        # print("[*] ========== receive data ==========")
        # print(json.dumps(data_object, indent=4, sort_keys=True))
        # print("[*] ==================================")

        self.resolve(data_object)
        self.send_response(200)
        self.end_headers()

    def trim_to_plain_text(self, text: str) -> str:
        regex_to_delete = [
            r':[A-Za-z0-9._]+:',
        ]
        for regex in regex_to_delete:
            text = re.sub(regex, "", text)
        return text

    def get_user_name(self, user: dict) -> str:
        try:
            ans = ""
            if user['name'] != None and len(user['name']) > 0:
                ans = user['name']
            else:
                ans = user['username']
            return self.trim_to_plain_text(ans)
        except:
            return ""

    def get_user_avatar(self, user: dict) -> str:
        try:
            return user['avatarUrl']
        except:
            return ""

    def get_note_description(self, note: dict) -> str:
        try:
            if note['cw'] != None and len(note['cw']) > 0:
                return self.trim_to_plain_text(note['cw'])
            text = note['text']
            if text == None:
                text = ""
            text = self.trim_to_plain_text(text)
            if len(note['files']) > 0:
                text += " 📎x%d" % len(note['files'])
            return text.strip()
        except:
            return ""

    def resolve(self, data: dict):
        if posted_events.get(data['eventId']) != None:
            return
        posted_events[data['eventId']] = True
        print("[*] resolve event %s" % data['eventId'])

        title = ""
        message = ""
        icon = ""

        if data['type'] == 'followed':
            title = self.get_user_name(data['body']['user']) + " 关注了你"
            icon = self.get_user_avatar(data['body']['user'])

        if data['type'] == 'renote':
            title = self.get_user_name(
                data['body']['note']['user']) + " 转发了你的嘟文"
            newpost = self.get_note_description(data['body']['note'])
            oldpost = self.get_note_description(data['body']['note']['renote'])
            if len(newpost) > 0:
                message += newpost
            else:
                message = oldpost
            icon = self.get_user_avatar(data['body']['note']['user'])

        if data['type'] == 'mention':
            title = self.get_user_name(data['body']['note']['user']) + " 提到了你"
            message = self.get_note_description(data['body']['note'])
            icon = self.get_user_avatar(data['body']['note']['user'])

        # if data['type'] == 'reply':
        #     title = self.get_user_name(data['body']['note']['user']) + " 回复了你"
        #     message = self.get_note_description(data['body']['note'])
        #     icon = self.get_user_avatar(data['body']['note']['user'])

        if data['type'] == 'reaction':
            title = self.get_user_name(data['body']['note']['user']) + " 回应了你"
            icon = self.get_user_avatar(data['body']['note']['user'])
            try:
                message = self.get_note_description(data['body']['note'])
            except:
                message = ""

        if len(title) <= 0 and len(message) <= 0:
            return

        bark.send(title, message, icon=icon)


httpd = socketserver.TCPServer(("", port), MisskeyBarkHandler)
httpd.serve_forever()
