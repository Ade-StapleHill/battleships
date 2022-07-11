from __future__ import print_function

import sys, os
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

# This example uses Python threads to manage async input from sys.stdin.
# This is so that I can receive input from the console whilst running the server.
# Don't ever do this - it's slow and ugly. (I'm doing it for simplicity's sake)
from _thread import *

from battleships import Player, Logging

class BattleShipsClient(Player, ConnectionListener):
    def __init__(self, host, port, **kwargs):
        self.Connect((host, port))
        print("BattleShips client started")
        print("Ctrl-C to exit")

        nickname = None
        if 'id' in kwargs:
            nickname = kwargs['id']
        else:
            # get a nickname from the user before starting
            print("Enter your nickname: ")
            nickname = stdin.readline().rstrip("\n")
        super().__init__(nickname)
        self.robot = True if nickname.startswith('robot') else False
        connection.Send({"action": "nickname", "nickname": nickname})
        # if environment variable BattleShips_LOG is set then api call to
        # Logging.logger.debug() will write to <nickname>.log logfile 
        Logging(f'battleships_client_{self.id}.log')
        Logging.logger.debug(f"{os.path.basename(__file__)} {self.id} __init__()")
        print(f"Welcome {self.id}", flush=True) # flush so pytest detects connected

        if 'cmds' in kwargs:
            Logging.logger.debug(f"{os.path.basename(__file__)} {self.id} __init__() cmds={kwargs['cmds']}")
            for cmd in kwargs['cmds']:
                output, _cmds = self.parse_input(cmd)
                if output != None:
                    print(output, flush=True)

        self.turn_callback = [None, None]   # func, param
        if self.robot == True:
            self.turn_callback = [self.robot_turn_callback, None]
            self.set_ready()
        else:
            # launch our threaded input loop
            t = start_new_thread(self.InputLoop, ())
    
    def Loop(self):
        connection.Pump()
        self.Pump()
    
    def InputLoop(self):
        # horrid threaded input loop
        # continually reads from stdin and sends whatever is typed to the server
        count=0
        while 1:
            res = self.cmdline()
            connection.Send({"action": "message", "message": f"{self.id} count={count} res={res}"})
            count += 1
    
    def robot_turn_callback(self, parm=None):
        # Called when this players turn, random fire first opponent
        op_id = self.opponents[0]  # default is first opponent added
        res, pos = self.random_fire(op_id) # robot random fire
        print(f"{self.id}: fire {pos} {op_id}", flush=True)
        return res
    
    #######################################
    ### Network event/message callbacks ###
    #######################################
    
    def Network_players(self, data):
        print("*** players: " + ", ".join([p for p in data['players']]))
        for nickname in data['players']:
            if nickname != self.id and (nickname not in self.opponent_maps):
                self.add_opponent(nickname)
    
    def Network_message(self, data):
        print(data['who'] + ": " + data['message'])
    
    # built in stuff

    def Network_connected(self, data):
        print("You are now connected to the server")
    
    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()
    
    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()
    
    ####################

    def Network_incoming(self, data):
        pos = data['pos']
        res = self.incoming(pos)
        # server gets 'mapupdate' and then sends 'updatemap' to all clients
        connection.Send({"action": "incomingupdate", "opp_id" : self.id, "pos" : pos, "res" : res}) 

    def Network_turn(self, data):
        self.turn = True
        print(f"Your turn {self.id}", flush=True)
        (callback, parm) = self.turn_callback
        if callback != None:
            callback(self, parm)

    def Network_updatemap(self, data):
        opp_id = data['opp_id']
        if opp_id != self.id:
            self.update_map(opp_id, data['pos'], data['res'])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "host:port [id [cmds]]")
        print("e.g.", sys.argv[0], "localhost:31425 robot1 '--place d a1'")
    else:
        host, port = sys.argv[1].split(":")
        xargs = {}
        if len(sys.argv) > 2:
            xargs['id'] = sys.argv[2]
            if len(sys.argv) > 3:
                xargs['cmds'] = sys.argv[3:]
        c = BattleShipsClient(host, int(port), **xargs)
        while 1:
            c.Loop()
            sleep(0.001)
