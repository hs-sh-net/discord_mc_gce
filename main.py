import configparser
import subprocess
import re
import discord
import datetime
import schedule
from mcrcon import MCRcon


class Config:
    file = "config.ini"

    def load(self, section, key, *, default=""):
        config = configparser.ConfigParser()

        config.read(self.file)

        if section not in config:
            config[section] = {}
            print("Config: [", section, "]")

        if key not in config[section]:
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
        self.interval = conf.load("Minecraft", "interval", default="5")
        self.inactive_count = conf.load("Minecraft", "count", default="2")
        self.gce_zone = conf.load("GCE", "gce_zone", default="asia-northeast1-b")
        self.gce_name = conf.load("GCE", "gce_name", default="minecraft")
        self.gcloud = conf.load("GCE", "gcloud", default="/snap/bin/gcloud")
        self.inactive = 0
        self.is_polling = 0

        self.port = int(self.port)
        self.interval = int(self.interval)
        self.inactive_count = int(self.inactive_count)

    def start(self):
        subprocess.run([self.gcloud, "compute", "instances", "start", "--zone", self.gce_zone, self.gce_name])

    def stop(self):
        self.rcon("/stop")

    def count(self):
        res = self.rcon("/list")
        res = re.search("([0-9]+)", res)
        if res is None:
            return -1
        count = int(res.group(0))
        return count

    def poll(self):
        count = self.count()
        print(datetime.datetime.now(), "Player:", count)
        if count == 0:
            self.inactive = self.inactive + 1
            if self.inactive > self.inactive_count:
                self.stop()
                print(datetime.datetime.now(), "Stopped")
        else:
            self.inactive = 0

    def rcon(self, command):
        try:
            with MCRcon(self.host, self.password, self.port) as mcr:
                return mcr.command(command)
        except ConnectionRefusedError:
            print("Minecraft: ConnectionRefusedError")
            return ""

class Discord:
    def __init__(self):
        conf = Config()
        self.token = conf.load("Discord", "Token")
        self.interval = conf.load("Discord", "Interval", default="5")

        self.interval = int(self.interval)
        self.last = datetime.datetime.fromtimestamp(0)
        self.client = discord.Client()

    def start(self):
        @self.client.event
        async def on_ready():
            print('We have logged in as {0.user}'.format(self.client))

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            now = datetime.datetime.now()
            if message.content.startswith('/mc'):
                print(now, now - self.last, message.author, message.content)

                if now - self.last < datetime.timedelta(minutes=self.interval):
                    return

                self.last = now

            if message.content.startswith('/mc start'):
                server = Server()
                if server.count() == -1:
                    server.start()
                    msg = "サーバーを起動します"
                else:
                    msg = "サーバーは起動しています"
                await self.client.send_message(message.channel, msg)

            elif message.content.startswith('/mc stop'):
                server = Server()
                cnt = server.count()

                if cnt == 0:
                    server.stop()
                    msg = "サーバーを停止します"
                elif cnt == -1:
                    msg = "サーバーは停止しています"
                else:
                    msg = "まだ人がいます"

                await self.client.send_message(message.channel, msg)

            elif message.content.startswith('/mc count'):
                server = Server()
                msg = server.count()
                await self.client.send_message(message.channel, msg)

        self.client.run(self.token)


def main():
    server = Server()
    server.poll()
    schedule.every(server.interval).minutes.do(server.poll)

    ds = Discord()
    ds.start()


main()
