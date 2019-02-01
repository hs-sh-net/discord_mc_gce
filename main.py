import configparser
import subprocess
import re
from mcrcon import MCRcon

class Config:
    file = "config.ini"

    def load(self, section, key, *, default=""):
        config = configparser.ConfigParser()

        config.read(self.file)

        if not section in config:
            config[section] = {}
            print("Config: [", section, "]")

        if not key in config[section]:
            config[section][key] = default
            print("Config: [", section, "][", key, "] : ", default)
            with open(self.file, 'w') as configfile:
                config.write(configfile)

        return config[section][key]


class Server:
    def __init__(self):
        conf = Config()
        self.host = conf.load("Minecraft", "host", default="localhost")
        self.password = conf.load("Minecraft", "password", default="password")
        self.port = conf.load("Minecraft", "port", default="25575")
        self.gce_zone = conf.load("GCE", "gce_zone", default="asia-northeast1-b")
        self.gce_name = conf.load("GCE", "gce_name", default="minecraft")
        self.gcloud = conf.load("GCE", "gcloud", default="/snap/bin/gcloud")

        self.port = int(self.port)

    def start(self):
        subprocess.run([self.gcloud, "compute", "instances", "start", "--zone", self.gce_zone, self.gce_name])

    def stop(self):
        with MCRcon(self.host, self.password, self.port) as mcr:
            print(mcr.command("/stop"))

    def count(self):
        with MCRcon(self.host, self.password, self.port) as mcr:
            res = mcr.command("/list")
            count = int(re.search("([0-9]+)", res).group(0))
            return(count)

def main():
    server = Server()
    print(server.count(), "人います")

main()
