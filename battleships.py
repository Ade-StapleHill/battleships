# %% [markdown]
# # Sketch Code
# 
# * map is 2D array with '.' for empty square; char for vessel e.g. 's' for submarine
# * List of vessels and length
#   - minesweeper, 2
#   - submarine, 3
#   - frigate, 4
#   - destroyer, 5
#   - aircraft carrier, 6
# 
# * Use Classes for vessels as they behave much the same with only length different

# %%
class Vessel:
  def __init__(self, name, abbrv, length, position=None):
    self.name = name
    self.abbrv = abbrv
    self.length = length
    self.position = position  # tuple: ('a1', 'c1') for len=3 vessel on bottom left
    self.hits = []  # index from bottom left ('a1') hit e.g. [0,2] 
    self.sunk = False

  def pos(self, pos):
    self.position = pos

  def isplaced(self):
    return False if self.position == None else True
  
  def __repr__(self):
    return f"{self.name}: {self.position if self.isplaced() else 'not placed'}"

class Minesweeper(Vessel):
  def __init__(self, name='Minesweeper', abbrv='m', length=2, position=None):
    super().__init__(name, abbrv, length, position)

class Submarine(Vessel):
  def __init__(self, name='Submarine', abbrv='s', length=3, position=None):
    super().__init__(name, abbrv, length, position)

class Frigate(Vessel):
  def __init__(self, name='Frigate', abbrv='f', length=4, position=None):
    super().__init__(name, abbrv, length, position)

class Destroyer(Vessel):
  def __init__(self, name='Destroyer', abbrv='d', length=5, position=None):
    super().__init__(name, abbrv, length, position)

class Carrier(Vessel):
  def __init__(self, name='Aircraft Carrier', abbrv='a', length=6, position=None):
    super().__init__(name, abbrv, length, position)

# %%
NROWS = 20
NCOLS = 20

# number of each vessel
vessel_list = [
    [Minesweeper, 3],
    [Submarine, 3],
    [Frigate, 2],
    [Destroyer, 2],
    [Carrier, 1]
]

class Map:
  def __init__(self):
    self.map  = [['.' for i in range(NCOLS)] for j in range(NROWS)]
    self.vessels = []
    for v in vessel_list:
      for i in range(v[1]):
        self.vessels.append(v[0]())
  
  def __repr__(self):
    str = ""
    str += f"vessels: "
    for v in self.vessels:
        str += f"\n\t [{v}]"
    str += f"\nmap: "
    for r in self.map:
        str += f"\n\t{r}"
    return str

# %%
my_map = Map()
opponent_map = Map()
if False:
    print(f"my_map: {my_map}")

# %% [markdown]
# # cmdline interface
# Commands
# - show [mine | opponent] :: show map, hits/misses displayed as O/X
#   - opponent :: display shots I've made
#   - mine :: display my map showing all my vessels with opponents shots
# - vessels :: list my vessels location or 'not placed'
# - place <v> <pos>:[h|v] :: place vessel <v> starting top left position <pos> either horiz or vert
#   - where <pos> :: <col><row> :: where <col> is 1 to n, <row> is 'a' to 'z'; top left is 'a1'. 
#   - <v> is vessel name or abbreviation e.g. 'd' or 'Destroyer' 
# - reset :: new game
# - ready :: manual place complete, auto-complete unplaced vessels, wait for opponent ready
# - fire <pos> :: returns with value 'hit' | 'miss' | 'sunk' [| 'game over']

# %%
import sys, argparse
class Cmdline:
    def __init__(self):
        self.parser = argparse.ArgumentParser()

        #-hself.parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    
        self.parser.add_argument('-i', '--info', dest ='info', 
                    action ='store_true', help ='display info')

        #args.show == None if input:'-s', else args.show == '' if no -s option
        self.parser.add_argument('-s', '--show', dest ='show', 
                    action ='store', nargs = '?', choices = {'mine', 'opponent'},
                    default = '', help ='display map')  
        
        self.parser.add_argument('-v', '--vessels', dest ='vessels',
                    action ='store_true', help ='list vessels')

        self.parser.add_argument('-r', '--ready', dest ='ready',
                    action ='store_true', help ='ready to fire')
        
        self.parser.add_argument('-n', '--new', dest ='new',
                    action ='store_true', help ='new game')
  
        self.parser.add_argument('-p', '--place', dest ='place', 
                    action ='store', nargs = 2, help ='place <v> <pos>:[h|v]')
    
        self.parser.add_argument('-f', '--fire', dest ='fire', 
                    action ='store', nargs = 1, help ='fire <pos>')
        
    def parse_input(self):
        print(f"Enter command: ")
        for line in sys.stdin:
            args = self.parser.parse_args(line.split())
            print(f"DBG args: {args}")

            if args.info:
                # --info (alias for --help)
                self.parser.print_help()
            
            # --show
            show_mine = False
            show_opponent = False
            if args.show == None:
                show_mine = show_opponent = True
            elif len(args.show) > 0:
                if args.show == 'mine':
                    show_mine = True
                else:
                    show_opponent = True
            if show_mine:
                print(f"my_map: {my_map}")
            if show_opponent:
                print(f"opponent_map: {opponent_map}")

#%%
cmd = Cmdline()
while True:
    cmd.parse_input()
