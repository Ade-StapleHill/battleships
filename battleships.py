# %%
import sys, argparse
import re, random
import logging, os

# %%
class Logging:
  # During development, to save debug values to log file then set env "BattleShips_LOG" and 
  # use api: Logging.logger.debug(f"debug vals") e.g. `BattleShips_LOG=1  python3 battleships.py`
  # import Logging in other modules to share same log config

  LOG_OFF=0
  LOG_LOW=1
  LOG_MED=2
  LOG_HIGH=3
  LOG_ENV = 'BattleShips_LOG'
  LOG_FILE = 'battleships.log'
  logger = logging

  def __init__(self):
    self.log_flag = Logging.LOG_OFF # set 0 to disable logging
    log_env = os.getenv(self.LOG_ENV)
    if log_env:
      self.log_flag = Logging.LOG_LOW 
      try:
          self.log_flag = int(log_env)
      except:
          pass

    if self.log_flag:
      self.logger.basicConfig(filename=self.LOG_FILE, filemode='w', \
          level = logging.DEBUG, format= "%(message)s")

Logging()

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

  def pos(self, pos_index, horiz=True):
    (row, col) = pos_index['index']  # e.g. (0, 0) for top left first row/first col
    (row, col) = (row, col + self.length-1) if horiz == True else (row + self.length-1, col) # end index
    self.position = (pos_index, Map.pos_index_nocheck(index=(row, col), pos=None))

  def is_placed(self):
    return False if self.position == None else True
  
  def __repr__(self):
    return f"{self.name}: {self.position if self.is_placed() else 'not placed'}"

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
class Map:
  (NROWS, NCOLS) = (15, 20) # map dimensions

  # number of each vessel
  vessel_list = [
    [Minesweeper, 3],
    [Submarine, 3],
    [Frigate, 2],
    [Destroyer, 2],
    [Carrier, 1]
  ]

  def __init__(self, nrows=NROWS, ncols=NCOLS, vessel_list=vessel_list):
    self.nrows = nrows
    self.ncols = ncols
    self.map  = [[' 'for i in range(ncols)] for j in range(nrows)]
    self.vessels = []
    for v in vessel_list:
      for i in range(v[1]):
        self.vessels.append(v[0]())
  
  def is_valid_index(self, row, col):
    # test (row, col) is within map dimensions
    return True if ((row >= 0) and (row < self.nrows) and (col >= 0) and (col < self.ncols)) else False
  
  @staticmethod
  def space(map):
    # Return list of spaces in each row, list elem is (column_index, len).
    space_list = [[] for j in range(len(map))]
    pattern = r"\S+|\s+" # group multi (one or more) non-space | multi space

    for row_index, row in enumerate(map):
      space_list[row_index] = []
      row = ''.join(row)
      matches = re.findall(pattern, row)
      # eg. row=' a  bb   ccc    ' => matches=[' ', 'a', '  ', 'bb', '   ', 'ccc', '    ']
      col_index = 0
      for m in matches:
        # todo: test if row has no space then space_list missing index
        if m.startswith(' '):
          space_list[row_index].append((col_index, len(m)))
        col_index += len(m)
    return space_list

  @staticmethod
  def index_to_pos_nocheck(index):
    # Convert 2d array index tuple (row, col) to position e.g. top left (0,0) => 'a1'
    # 2d array index: (<row_index>, <col_index) => pos: '<col_file><row_rank>' 
    # where <col_file> :: 'a' | 'b' | ...; <row_rank> :: 1 | 2 | ...
    # e.g. index: (0, 0) => pos: 'a1'; index: (3, 4) => 'd4'
    # Do not check if index is out of range
    (row, col) = index
    pos = f"{chr(ord('a')+col)}{row+1}"
    return pos
  
  def index_to_pos(self, index):
    # Convert 2d array index tuple (row, col) to position e.g. top left (0,0) => 'a1'
    # 2d array index: (<row_index>, <col_index) => pos: '<col_file><row_rank>' 
    # where <col_file> :: 'a' | 'b' | ...; <row_rank> :: 1 | 2 | ...
    # e.g. index: (0, 0) => pos: 'a1'; index: (3, 4) => 'd4'
    # Return None if index is out of range
    (row, col) = index
    pos = None
    if self.is_valid_index(row, col):
      pos = self.index_to_pos_nocheck(index)
    return pos

  @staticmethod
  def pos_to_index_nocheck(pos):
    # Convert position ref e.g. 'a1' to 2d array index e.g. (0,0)
    # Retrun None if pos invalid, but do not check if out of range
    index = None
    matches = re.match(r"^([a-z]+)(\d+)$", pos) # one or more chars then one or more digits
    if matches != None and (len(matches.groups()) == 2):
      # matches[0] :: <col_file> e.g. 'a'; matches[1] :: <row_rank> e.g. 1
      (file, rank) = matches.groups()
      col = ord(file) - ord('a')
      row = int(rank) - 1
      index = (row, col)
    return index
  
  def pos_to_index(self, pos):
    # Convert position ref e.g. 'a1' to 2d array index e.g. (0,0)
    # Retrun None if pos invalid or out of range
    index = self.pos_to_index_nocheck(pos)
    if index != None and (self.is_valid_index(*index) == False):
      index = None
    return index

  def pos_index(self, pos=None, index=None):
    # Provide either algebraic or array ref
    # Create dict of map position to provide both map array (row, col) and 
    # equivalent algebraic. Keys 'index' : (row,col) e.g. (0,0), 'pos': algebra e.g. 'a1'
    if pos == None:
      pos = self.index_to_pos(index)
    elif index == None:
      index = self.pos_to_index(pos)
    return {'pos' : pos, 'index' : index}
  
  @staticmethod
  def pos_index_nocheck(pos=None, index=None):
    # Same as pos_index() but no check if in range so do not need object access
    if pos == None:
      pos = Map.index_to_pos_nocheck(index)
    elif index == None:
      index = Map.pos_to_index_nocheck(pos)
    return {'pos' : pos, 'index' : index}

  @staticmethod
  def dump_arr(arr, str='', terse=True):
    linebuff = ""

    for idx, elem in enumerate(arr):
      str1 = f"{str}[{idx}]"
      if (len(elem) > 0) and (type(elem) == list) and (type(elem[0]) == list):
        for idx2, elem2 in enumerate(elem):
          str2 = f"\t{str1}[{idx2}]"
          linebuff += Map.dump_arr(elem2, str2, terse)
      else:
        linebuff += f"{str1}[0:{len(elem)-1}]={elem}\n"
    return linebuff
    
  @staticmethod
  def info_arr(arr):
    subarr = arr
    dims = []
    while type(subarr) == list:
        dims.append(len(subarr))
        subarr = subarr[0]
    return dims

  def spaces(self):
    # return two lists of any spaces, first for map in row order, second for map in column_order
    horiz_list = self.space(self.map)
    # transpose array i.e. rows to cols e.g 
    # [['a','b','c'],['d','e','f'],['g','h','i']] => [('a', 'd', 'g'), ('b', 'e', 'h'), ('c', 'f', 'i')]
    vert_list = self.space([*zip(*self.map)])
    if False:
      print("DBG : ", Map.dump_arr((horiz_list, vert_list), "spaces"))
    return (horiz_list, vert_list)
  
  def spans(self, length):
    # return two lists of spaces big enough for len, first row order then col order
    spans = [[], []] # list of any space big enough or bigger 
    spaces = self.spaces() # all space e.g. horiz = [[(0,2), (6,4), ...],...,[(7,2), (12,3), ...]]
    for idx_o, o in enumerate(spaces):
      spans[idx_o] = []
      for row in o:
        spans[idx_o].append([s for s in row if s[1] >= length])
    if False:
      print("DBG : ", Map.dump_arr(spans, "spans"))
    return spans

  def available(self, length):
    # return list of (start, end) positions available to place vessel of length
    # two lists returned, horiz list first with space list per row, vert list is space list per col
    spans = self.spans(length) # horiz and vert lists of any space big enough or bigger 
    available = [[], []] # horiz and vert list of (start, end) position

    if False:
      test1 = [[i for i in range(4)] for _ in range(3)]
      for r_idx, r in enumerate(test1):
        for c_idx, c in enumerate(r):
          test1[r_idx][c_idx] = (r_idx, c_idx)
      print(f"test1={test1}")

      test2 = [*zip(*test1)] # transpose
      print(f"test2={test2}")

    for idx_o, sp in enumerate(spans):
      # spans[0] == horiz; spans[1] == vert
      orient = []
      for idx_r, row in enumerate(sp):
        orient_row = []
        for s in row:
          for i in range(s[1]-length+1):
            # s[0] is start of spaces column, allow for spans bigger than len
            pos = (idx_r, s[0]+i)
            if idx_o == 1:
              # vert so transpose; each row is the col, each col is row
              pos = (pos[1], pos[0])
            orient_row.append(pos)
        orient.append(orient_row)
      available[idx_o].append(orient)

    if False:
      print(f"DBG : available(length={length})", Map.dump_arr(available, "available"))
    
    return available
  
  def place_vessel(self, vessel, pos_index, horiz=True):
    res = False
    vlen = vessel.length
    available = self.available(vlen)
    orient = available[0 if horiz == True else 1][0]
    if 'index' in pos_index:
      (row, col) = pos_index['index']
      if row < len(orient) and (len(orient[row]) > 0) and ((row, col) in orient[row]):
        vessel.pos(pos_index, horiz) # set vessel position
        res = True
    return res
  
  def place(self, vessel, pos_index, horiz=True):
    res = False
    if self.place_vessel(vessel, pos_index, horiz):
      (row, col) = vessel.position[0]['index']  # start index
      for i in range(vessel.length):
        (irow, icol) = (row, col+i) if horiz == True else (row+i, col)
        self.map[irow][icol] = f"{vessel.abbrv}"
      res = True
    return res

  def random_place(self):
    while True:
      vessels = [v for v in self.vessels if not v.is_placed()] # not yet placed
      if len(vessels) == 0:
        break
      for v in random.choices(vessels):
        available = self.available(v.length)
        if available and len(available) > 0:
          orient_index = random.randint(0, 1) # 0: horiz, 1: vert
          orient_list = [d for r in available[orient_index] for c in r for d in c] # flatten 2d array
          map_index = random.choices(orient_list)[0] # random choice from list
          pos_index = self.pos_index(index=map_index)
          if self.place(v, pos_index, horiz=(orient_index == 0)):
            print(f"DBG random_place: {v}")

  def display_map(self):
    str = ""
    col_index = ' '.join([chr(ord('a')+i) for i in range(self.ncols)]) # a b c...
    str += f' \t{col_index}'
    for index, row in enumerate(self.map):
        row = ','.join(row)
        row = row.replace(' ','.')
        row = row.replace(',', ' ')
        str += f"\n{index+1}\t{row}"  # top-left is 'a1'
    return str

  def __repr__(self):
    str = ""
    str += f"vessels: "
    for v in self.vessels:
        str += f"\n\t [{v}]"
    str += f"\nmap:\n{self.display_map()}"
    return str

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
class CmdLine:
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
        
    def parse_input(self, my_map, opponent_map, lines=sys.stdin):
        print(f"Enter command: ")
        for line in lines:
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

# %%
class Player(CmdLine):
  def __init__(self, nrows=Map.NROWS, ncols=Map.NCOLS, vessel_list=Map.vessel_list):
    super().__init__()
    self.my_map = Map(nrows, ncols, vessel_list)
    self.opponent_map = Map(nrows, ncols)
  
  def cmd(self, lines=sys.stdin):
    self.parse_input(self.my_map, self.opponent_map, lines)

  def __repr__(self):
    str = repr(self.my_map) + repr(self.opponent_map)

if __name__ == "__main__":
# %%
  player1 = Player()

  player1.my_map.spaces()
  player1.my_map.random_place()

  player1.cmd(['--info --vessels --show'])

  while True:
      player1.cmd()
