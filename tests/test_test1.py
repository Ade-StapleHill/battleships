'''
pytest searches subdirs for filenames test_*.py or *_test.py,
then it runs functions prefixed "test"
python3 -m pytest -k test6_dodgy
'''
import os
#    os.environ[Logging.LOG_ENV] = "1"
os.environ['BattleShips_LOG'] = "1"

from battleships import Map, Player

def test1():
    print(Map.dump_arr([1,2,3], str='1d'))
    print(Map.dump_arr([[1,2,3], [4,5,6]], str='2d'))
    print(Map.dump_arr([[[1,2,3], [4,5,6]], [[11,12,13], [14,15,16]]], str='3d'))

def test2():
    print(Map.dump_arr([1,2,3], str='1d'))
    print(Map.dump_arr([[1,2,3], [4,5,6]], str='2d'))
    print(Map.dump_arr([[[1,2,3], [4,5,6]], [[11,12,13], [14,15,16]]], str='3d'))

def test3_horiz():
    dims = [6, 4]   # nrows, ncols
    vessel_list = Map.vessel_list[0:1] # first vessel type
    player1 = Player(*dims, vessel_list=vessel_list)

    info_arr = Map.info_arr(player1.my_map.map)
    print(f"my_map dims = {info_arr}")
    for i, elem in enumerate(info_arr):
        assert elem == dims[i]

    print(f"{Map.dump_arr(player1.my_map.map, 'my_map')}")
    print(f"{player1.my_map}")

    for idx, vessel in enumerate(player1.my_map.vessels):
        pos_index = player1.my_map.pos_index(index=(idx, idx))
        assert player1.my_map.place(vessel, pos_index, horiz=True) == True
    print(f"{player1.my_map}")

def test4_vert():
    dims = [6, 4]   # nrows, ncols
    vessel_list = Map.vessel_list[0:1] # first vessel type
    player1 = Player(*dims, vessel_list=vessel_list)

    for idx, vessel in enumerate(player1.my_map.vessels):
        pos_index = player1.my_map.pos_index(index=(idx, idx))
        assert player1.my_map.place(vessel, pos_index, horiz=False) == True
    print(f"{player1.my_map}")

def test5_random():
    player1 = Player()
    player1.my_map.random_place()
    print(f"{player1.my_map}")

if __name__ == "__main__":
    # invoked by python and not pytest
    #test1()
    #test2()
    if False:
        test3_horiz()
        test4_vert()
    test5_random()
    pass