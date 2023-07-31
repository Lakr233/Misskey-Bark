#
# bark.py
# misskey-bark
#
# Created by @Lakr233 on 2023/01/15
#

import urllib.parse
import requests


class Bark:
    config = {}

    def __init__(self, config: dict):
        self.config = config

    def read_conf(self, key: str):
        try:
            return self.config[key]
        except KeyError:
            return None

    def get_endpoint(self): return self.config["endpoint"]
    def get_endpoints(self): 
        try:
            ans = list(self.config["endpoints"])
            if len(ans) < 1: return None
            return ans
        except:
            return None

    def get_group(self): return self.config["group"]
    def get_icon(self): return self.config["icon"]
    def get_sound(self): return self.config["sound"]
    def get_cat(self) -> bool: return self.config["cat"]

    def url_str_join(self, list: list):
        build = ""
        for comp in list:
            if len(comp) == 0: continue
            if comp[-1] == "/": comp = comp[:-1]
            if comp[0] == "/": comp = comp[1:]
            build += comp + "/"

        if build[-1] == "/": build = build[:-1]
        return build

    def send(self, user: str, message: str, icon: str = ""):
        if self.get_cat() == True: message += " 喵～"
        parms = {
            "group": self.get_group(),
            "icon":  icon if len(icon) > 0 else self.get_icon(),
            "sound": self.get_sound(),
        }
        parms = {k: v for k, v in parms.items() if v is not None}
        title = urllib.parse.quote(user.strip())
        message = urllib.parse.quote(message.strip())

        if self.get_endpoints() != None:
            for endpoint in self.get_endpoints():
                url = self.url_str_join([endpoint, title, message])
                r = requests.get(url, params=parms)
                print("[*] response: %s" % r.text)
            return

        url = self.url_str_join([self.get_endpoint(), title, message])
        r = requests.get(url, params=parms)
        print("[*] response: %s" % r.text)
        
