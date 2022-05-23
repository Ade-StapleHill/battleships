'''
`pytest` searches subdirs for filenames test_*.py or *_test.py,
then it runs functions prefixed "test"
$ python3 -m pytest -k test6_dodgy

`coverage` to report source lines that tests visit and don't visit:
$ rm -rf .coverage htmlcov; PYTHONPATH=. coverage run -m pytest; coverage html; firefox htmlcov/index.html
'''
import os
#    os.environ[Logging.LOG_ENV] = "1"
os.environ['BattleShips_LOG'] = "1"

from battleships import Map, Player, Minesweeper, Submarine

def test1_horiz():
    dims = [6, 4]   # nrows, ncols
    vessel_list = [ # [type, number]
        [Minesweeper, 3]
    ]
    player1 = Player('test1_horiz', *dims, vessel_list=vessel_list)

    info_arr = Map.info_arr(player1.my_map.map)
    print(f"my_map dims = {info_arr}")
    for i, elem in enumerate(info_arr):
        assert elem == dims[i]

    print(f"{Map.dump_arr(player1.my_map.map, 'my_map')}")
    print(f"{player1.my_map}")

    for idx, vessel in enumerate(player1.my_map.vessels):
        pos_index = player1.my_map.pos_index(index=(idx, idx))
        assert player1.my_map.place(vessel, pos_index['pos'], horiz=True) == True
    print(f"{player1.my_map}")

def test2_vert():
    dims = [6, 4]   # nrows, ncols
    vessel_list = [ # [type, number]
        [Minesweeper, 3]
    ]
    player1 = Player('test2_vert', *dims, vessel_list=vessel_list)
    for idx, vessel in enumerate(player1.my_map.vessels):
        pos_index = player1.my_map.pos_index(index=(idx, idx))
        assert player1.my_map.place(vessel, pos_index['pos'], horiz=False) == True
    print(f"{player1.my_map}")

def test3_simple():
    dims = [4, 3]   # nrows, ncols
    vessel_list = [
        [Minesweeper, 2],
        [Submarine, 2]
    ]
    player1 = Player('test3_simple', *dims, vessel_list=vessel_list)
    vessels = player1.my_map.vessels

    assert player1.my_map.place(vessels[0], 'b1', horiz=False) == True
    assert player1.my_map.place(vessels[2], 'a3', horiz=True) == True
    print(f"{player1.my_map}")
    return player1

def test4_nospace():
    player1 = test3_simple()
    vessels = player1.my_map.vessels

    assert player1.my_map.place(vessels[1], 'a2', horiz=False) == False
    assert player1.my_map.place(vessels[3], 'a1', horiz=True) == False
    print(f"{player1.my_map}")

def test5_random():
    player1 = Player('test5_random')
    assert player1.my_map.random_place_all() == True
    print(f"{player1.my_map}")

def test6_random_nospace():
    dims = [5, 5]   # nrows, ncols; not enough for vlen == 6
    player1 = Player('test6_random_nospace', *dims)
    assert player1.my_map.random_place_all() == False
    print(f"{player1.my_map}")

def test7_dense():
    player1 = test3_simple()
    vessels = player1.my_map.vessels

    assert player1.my_map.random_place(vessels[3]) == True
    assert player1.my_map.random_place(vessels[1]) == True

    print(f"{player1.my_map}")

def test8_fire():
    dims = [4, 3]   # nrows, ncols
    vessel_list = [
        [Minesweeper, 1],
        [Submarine, 1]
    ]
    players = []
    for i in range(3):
        player = Player(f"player{i}", *dims, vessel_list=vessel_list)
        for vidx, v in enumerate(player.my_map.vessels):
            pos = f"a{1+vidx+i}" # e.g. a1, a2 or a2, a3
            assert player.my_map.place(v, pos, horiz=True) == True
        players.append(player)
    
    for p in players:
        for o in players:
            if o != p:
                p.add_opponent(o)

    for p in players:
        print(p)
    
    assert players[0].fire('player1', 'a1') == Player.FIRE_MISS  # 'x' miss
    assert players[0].fire('player1', 'a1') == Player.FIRE_MISS.upper() # 'X' dupl miss

    assert players[0].fire('player1', 'a2') == Player.FIRE_HIT # 'y' hit
    assert players[0].fire('player1', 'a2') == Player.FIRE_HIT.upper()  # dupl hit
    assert players[0].fire('player1', 'c2') == Player.FIRE_MISS  # miss
    assert players[0].fire('player1', 'b2') == Minesweeper().abbrv +  Player.FIRE_SUNK # sunk

    return players

def test9_show():
    players = test8_fire()
    for p in players:
        print(f"test9_show {p}, {p.show_opponents()}")
    
def test10_cmdline():
    players = test8_fire()

    for p in players:
        res, cmds = p.parse_input('--show')
        print(f"{4*'+'} {p.id} {4*'+'}")
        print(f"test10_cmdline cmds: {cmds}\nres: {res}")
        print(f"{4*'-'} {p.id} {4*'-'}")

def test11_allsunk():
    players = test8_fire()

    assert players[0].fire('player1', 'a3') == Player.FIRE_HIT # 'y' hit
    assert players[0].fire('player1', 'b3') == Player.FIRE_HIT

    # (player, opp_map) = self.opponent_maps[opp_id]
    assert players[0].opponent_maps['player1'][1].allsunk == False
    assert players[0].fire('player1', 'c3') == Submarine().abbrv +  Player.FIRE_SUNK.upper() # allsunk
    assert players[0].opponent_maps['player1'][1].allsunk == True

    for p in players[:2]:
        print(f"{4*'+'} test11_allsunk {p.id} {4*'+'}")
        print(p)
        print(f"{4*'-'} test11_allsunk {p.id} {4*'-'}")

def test12_random():
    all_players = test8_fire()
    players = all_players[:2]   # two players

    index = 0
    while True:
        opp_player = players[index]
        opp_id = opp_player.id

        index = not index # toggle 0/1
        player = players[index]
        id = player.id

        if player.my_map.allsunk == True or (player.opponent_maps[opp_id][1].allsunk == True):
            print(f"{id if player.my_map.allsunk == True else opp_id} lost")
            break
        res = player.random_fire(opp_id)
        assert res != None 
    
    for p in players:
        print(f"{4*'+'} test12_random {p.id} {4*'+'}")
        print(p)
        print(f"{4*'-'} test12_random {p.id} {4*'-'}")

if __name__ == "__main__":
    # invoked by python and not pytest
    if False:
        test1_horiz()
        test2_vert()
        test3_simple()
        test4_nospace()
        test5_random()
        test6_random_nospace()
        test7_dense()
        test8_fire()
        test10_cmdline()
        test11_allsunk()
    test12_random()
    
    pass
