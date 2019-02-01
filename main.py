from mcrcon import MCRcon

class Minecraft:
    def start(self):
        return 0
    def stop(self):
        with MCRcon("localhost", "password", 25575) as mcr:
            resp = mcr.command("/stop")
            print(resp)

def main():
    mc = Minecraft()
    mc.stop()

main()
