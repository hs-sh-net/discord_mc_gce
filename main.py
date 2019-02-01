import configparser
import subprocess
from mcrcon import MCRcon

class Config:
    file = "config.ini"

    def __init__(self):
        config = configparser.ConfigParser()
        if not config.read(self.file):
            config["Minecraft"] = {
                "host": "localhost",
                "port": 25575,
                "password": "password",
            }
            with open(self.file, 'w') as configfile:
                config.write(configfile)

    def load(self, section, key):
        config = configparser.ConfigParser()
        config.read(self.file)

        if not section in config:
            config[section] = {}

        if not key in config[section]:
            config[section][key] = ""
            with open(self.file, 'w') as configfile:
                config.write(configfile)

        return config[section][key]


class Server:
    def __init__(self):
        conf = Config()
        self.host = conf.load("Minecraft", "host")
        self.password = conf.load("Minecraft", "password")
        self.port = int(conf.load("Minecraft", "port"))
        self.gce_zone = conf.load("GCE", "gce_zone")
        self.gce_name = conf.load("GCE", "gce_name")
        self.gcloud = conf.load("GCE", "gcloud")

    def start(self):
        subprocess.run([self.gcloud, "compute", "instances", "start", "--zone", self.gce_zone, self.gce_name])

    def stop(self):
        with MCRcon(self.host, self.password, self.port) as mcr:
            print(mcr.command("/stop"))

def main():
    server = Server()
    server.stop()

main()
