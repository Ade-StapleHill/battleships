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
from BattleShipsClient import BattleShipsClient
from conftest import hostname, port

def test_robot2():
    xargs = {}
    xargs['id'] = 'robot2'
    xargs['cmds'] = ['--info --place d a2 --ready --show']
    c = BattleShipsClient(hostname, int(port), **xargs)
    print(f"test_robot2: {hostname}, {port}, {xargs} opponents: {c.show_opponents()}")

if __name__ == "__main__":
    # invoked by python and not pytest
    if True:
        test_robot2()
    
    pass
