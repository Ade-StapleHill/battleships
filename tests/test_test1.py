'''
pytest searches subdirs for filenames test_*.py or *_test.py,
then it runs functions prefixed "test"
python3 -m pytest -k test6_dodgy
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
    
    assert players[0].fire('player1', 'a1') == 'x'  # miss
    assert players[0].fire('player1', 'a1') == 'X'  # dupl miss

    assert players[0].fire('player1', 'a2') == 'm'  # hit
    assert players[0].fire('player1', 'a2') == 'M'  # dupl hit
    assert players[0].fire('player1', 'c2') == 'x'  # miss
    assert players[0].fire('player1', 'b2') == 'ms'  # miss

    for p in players:
        print(p, p.show_opponents())









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
    
    pass