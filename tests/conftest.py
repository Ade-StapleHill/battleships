# Start server when pytest starts
# `pytest --xshow`` to display pids and logs e.g. cat   /home/adep/hope/.pytest_cache/d/.xprocess/BattleShipsClient/battleships_client_robot1.log

import sys

import py
import pytest
from xprocess import ProcessStarter
import shlex

import BattleShipsClient
import BattleShipsServer

hostname, port = 'localhost', 31429

@pytest.fixture(autouse=True, scope='session')
def start_battleships_server(xprocess):
    server_name = "BattleShipsServer"

    class Starter(ProcessStarter):
        pattern = "Server launched"
        terminate_on_interrupt = True
        args = [sys.executable, BattleShipsServer.__file__, f"{hostname}:{port}"]

    info = xprocess.ensure(server_name, Starter)
    yield
    xprocess.getinfo(server_name).terminate()


# Note battleships_server passed as param to ensure it has started first
@pytest.fixture(autouse=True, scope='session')
def start_battleships_client(xprocess, start_battleships_server):
    server_name = "BattleShipsClient"
    command_line = f"{sys.executable} {BattleShipsClient.__file__} '{hostname}:{port}' robot1 ' --place d a1 --ready' ' --show'"

    class Starter(ProcessStarter):
        pattern = 'Welcome robot1'
        terminate_on_interrupt = True
        args = shlex.split(command_line) # https://docs.python.org/3/library/subprocess.html#popen-constructor

    info = xprocess.ensure(server_name, Starter)
    yield
    xprocess.getinfo(server_name).terminate()

