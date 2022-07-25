from __future__ import print_function

import sys
from time import sleep, localtime
#from weakref import WeakKeyDictionary
from collections import OrderedDict

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from battleships import Logging
import os

class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)
    
    def Close(self):
        self._server.DelPlayer(self)
    
    ##################################
    ### Network specific callbacks ###
    ##################################
    
    def Network_message(self, data):
        Logging.logger.debug(f"{os.path.basename(__file__)} {self.nickname} Network_message: data={data}")
        self._server.SendToAll({"action": "message", "message": data['message'], "who": self.nickname})
    
    def Network_nickname(self, data):
        Logging.logger.debug(f"{os.path.basename(__file__)} {self.nickname} Network_nickname: data={data}")
        self.nickname = data['nickname']
        self._server.SendPlayers()
    
    def Network_fire(self, data):
        Logging.logger.debug(f"{os.path.basename(__file__)} {self.nickname} Network_fire: data={data}")
        opp_id = data['opp_id']
        pos = data['pos']
        self._server.SendFire(opp_id, pos)

    def Network_incomingupdate(self, data):
        # result of incoming
        Logging.logger.debug(f"{os.path.basename(__file__)} {self.nickname} Network_mapupdate: data={data}")
        self._server.SendUpDateMap(data['opp_id'], data['pos'], data['res'])

    def Network_ready(self, data):
        Logging.logger.debug(f"{os.path.basename(__file__)} {self.nickname} Network_ready: data={data}")
        self._server.SetReady(data['id'])

class BattleShipsServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = OrderedDict() # WeakKeyDictionary()
        self.turn = None    # players index of whose turn it is to fire
        Logging.logger.debug(f"{os.path.basename(__file__)} Server {kwargs['localaddr']} started")
        print('Server launched', flush=True) # flush so pytest detects connected 
    
    def send(self, p, data):
        Logging.logger.debug(f"{os.path.basename(__file__)} Server send {p.nickname} {data}")
        p.Send(data)

    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print(f"New Player {player.addr} {player.nickname}, index={len(self.players.keys())}")
        self.players[player] = False    # set True when client send ready
        # wait for nickname before self.SendPlayers() to avoid nickname == "anonymous"
        print("players", [p for p in self.players])
        if self.turn == None:
            self.turn = -1 # this is first player, NextTurn will increment
    
    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player] # TODO: what about whose turn ?
        self.SendPlayers()
    
    def SendPlayers(self):
        self.SendToAll({"action": "players", "players": [p.nickname for p in self.players]})
    
    def SendUpDateMap(self, opp_id, pos, res):
        data = {"action": "updatemap", "opp_id": opp_id, "pos" : pos, "res" : res}
        [self.send(p,data) for p in self.players if p.nickname != opp_id]  # all but client reporting the incoming

    def SendToAll(self, data):
        [self.send(p,data) for p in self.players]
    
    def SendToName(self, nickname, data):
        for p in self.players:
            if p.nickname == nickname:
                self.send(p, data)
    
    def SetReady(self, nickname):
        all_ready = True # False if one not ready
        for p in self.players:
            if self.players[p] == False:
                if p.nickname == nickname:
                    self.players[p] = True
                else:
                    all_ready = False
        if all_ready == True and len(self.players.keys()) > 1:
            self.NextTurn()
        
    def SendFire(self, nickname, pos):
        for p in self.players:
            if p.nickname == nickname:
                if self.players[p] == True:
                    # don't fire until opponent ready
                    self.send(p, {"action": "incoming", "pos": pos})
                else:
                    print('{nickname} not ready so ignore incoming fire from {self.nickname}')
        self.NextTurn()
    
    def NextTurn(self, index=None):
        # may trigger robot client fire
        self.SendToAll({"action": "turn", "turn": False})

        # OrderedDict() so players in date added order
        # players.items() returns [(key1, val1), (key2, val2)]
        #
        items = list(self.players.items())
        if index == None:
            index = self.turn
        index = index + 1   
        if index >= len(items):
            index = 0  # wrap to start of list
        self.turn = index
        p = items[index][0]
        self.send(p, {"action": "turn", "turn": True})

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

# get command line argument of server, port
if __name__ == '__main__':
    host = "localhost"
    port = "31429"
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], f"{host}:{port}")
    else:
        host, port = sys.argv[1].split(":")

    Logging('battleships_server.log')
    s = BattleShipsServer(localaddr=(host, int(port)))
    s.Launch()

