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
    self.hits = [False for i in range(length)]  # index from bottom left ('a1') hit e.g. [0,2] 
    self.sunk = False

  def pos(self, pos_index, horiz=True):
    # save start/end in algebraic pos format e.g ('a1', 'a3')
    (row, col) = pos_index['index']  # e.g. (0, 0) for top left first row/first col
    (row, col) = (row, col + self.length-1) if horiz == True else (row + self.length-1, col) # end index
    self.position = (pos_index['pos'], Map.pos_index_nocheck(index=(row, col), pos=None)['pos'])

  def is_placed(self):
    return False if self.position == None else True
  
  def __repr__(self):
    return f"{self.name}: {self.position if self.is_placed() else 'not placed'} hits={self.hits}"

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

  # Default number of each vessel
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
    self.allsunk = False  # True if all vessels sunk
    self.map  = [[' 'for i in range(ncols)] for j in range(nrows)]
    self.vessels = []
    self.vlist = vessel_list
    for v in self.vlist:
      for i in range(v[1]):
        self.vessels.append(v[0]()) # object init
  
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
    matches = re.match(r"^([a-z])(\d+)$", pos) # one or more chars then one or more digits
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
  
  @staticmethod
  def pos_index_nocheck(pos=None, index=None):
    # Same as pos_index() but no check if in range so do not need object access
    if pos == None:
      pos = Map.index_to_pos_nocheck(index)
    elif index == None:
      index = Map.pos_to_index_nocheck(pos)
    return {'pos' : pos, 'index' : index}

  def pos_index(self, pos=None, index=None):
    # Provide either algebraic 'a1' or array ref (0,0)
    # Create dict of map position to provide both map array (row, col) and 
    # equivalent algebraic. Keys 'index' : (row,col) e.g. (0,0), 'pos': algebra e.g. 'a1'
    pos_index = Map.pos_index_nocheck(pos, index)
    idx = pos_index['index']
    if idx == None or (self.is_valid_index(*idx) == False):
      pos_index = None
    return pos_index
  
  def pos_index_offset(self, pos_index):
    # (row, col) to offset from (0, 0) assuming rows concatenated
    pos_index_offset = pos_index
    (row, col) = pos_index['index']
    pos_index_offset['offset'] = row*self.nrows + col
    return pos_index_offset
  
  def offset_to_index(self, offset):
    # map offset to (row, col) index
    row = offset / self.nrows
    col = offset - (row * self.nrows)
    return (row, col)

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
    horiz_list = self.space(self.map) # list of (col, len) spaces for each map row
    # transpose array i.e. rows to cols e.g 
    # [['a','b','c'],['d','e','f'],['g','h','i']] => [('a', 'd', 'g'), ('b', 'e', 'h'), ('c', 'f', 'i')]
    vert_list = self.space([*zip(*self.map)]) # list of (row, len) spaces for each map col
    if False:
      print("DBG : ", Map.dump_arr((horiz_list, vert_list), "spaces"))
    return horiz_list, vert_list

  def available(self, length):
    # return list of (start, end) positions available to place vessel of length
    # two lists returned, horiz list first with space list per row, vert list is space list per col
    available = [[], []] # horiz and vert list of start positions for len
    for idx_o, sp in enumerate(self.spaces()):
      # spaces[0] == horiz; spaces[1] == vert
      orient = []
      for idx_r, row in enumerate(sp):
        orient_row = []
        for s in [s for s in row if s[1] >= length]:
          # space big enough for len
          # s[0] is start of spaces column/row, allow for spans bigger than len
          for i in range(s[1]-length+1):
            # if horiz then s is col; 
            (row, col) = (idx_r, s[0]+i)
            if idx_o == 1:
              (row, col) = (col, row) # vert then s is row start
            orient_row.append((row, col))
        orient.append(orient_row)
      available[idx_o] = orient

    if False:
      print(f"DBG : available(length={length})", Map.dump_arr(available, "available"))
    
    return available
  
  def place_vessel(self, vessel, pos_index, horiz=True):
    res = False
    available = self.available(vessel.length)
    orient = available[0 if horiz == True else 1]
    if pos_index['index'] in [c for r in orient for c in r]:
      # found (row, col) in available
      vessel.pos(pos_index, horiz) # set vessel position
      res = True
    return res
  
  def place(self, vessel, pos, horiz=True):
    # pos is algebra e.g. 'a1'
    res = False
    pos_index = self.pos_index(pos=pos)
    if self.place_vessel(vessel, pos_index, horiz):
      (row, col) = self.pos_index(pos=vessel.position[0])['index']  # start index
      for i in range(vessel.length):
        (irow, icol) = (row, col+i) if horiz == True else (row+i, col)
        self.map[irow][icol] = f"{vessel.abbrv}"
      res = True
    return res

  def random_place(self, v):
    res = False
    avail_flat = []
    random_index_orient = None  # (index, orient_idx)

    available = self.available(v.length)
    for idx_o, orient in enumerate(available):
      # flatten 2d array 
      avail_flat += [(c, idx_o) for r in orient for c in r]
    if len(avail_flat):
      random_index_orient = random.choices(avail_flat)[0]
    if random_index_orient != None:
      index = random_index_orient[0]
      horiz = True if random_index_orient[1] == 0 else False
      res = self.place(v, self.index_to_pos(index), horiz=horiz)
    if res == False:
      print(f"Error: cannot place {v}")
    else:
      print(f"DBG random_place: {v}")
      pass

    return res

  def random_place_all(self):
    res = True
    while res:
      vessels = [v for v in self.vessels if not v.is_placed()] # not yet placed
      if len(vessels) == 0:
        return True
      v = random.choices(vessels)
      res = self.random_place(v[0])
    return res

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
  
  def index_to_vessel(self, index):
    # Return (vessel, offset) at map index, else None
    res = None
    for v in self.vessels:
      (start_pos, end_pos) = v.position
      (start_index, end_index) = (self.pos_to_index(start_pos), self.pos_to_index(end_pos))
      (row, col) = start_index
      horiz = True if row == end_index[0] else False  # horiz if same row

      for i in range(v.length):
        (irow, icol) = (row, col+i) if horiz == True else (row+i, col)
        if (irow, icol) == index:
          res = (v, i) # hit so stop looking
          break
    return res

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
# - fire <pos> :: returns with value 'hit' | 'miss' | 'sunk' | 'game over'

# %%
class Player():
  def __init__(self, id, nrows=Map.NROWS, ncols=Map.NCOLS, vessel_list=Map.vessel_list):
    self.id = id
    self.parser = argparse.ArgumentParser()
    self.parse_init()
    self.my_map = Map(nrows, ncols, vessel_list)
    self.opponent_maps = {}
    self.first_opponent = None

  def parse_init(self):
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
                action ='store', nargs = '+', help ='fire <pos> [id]')
  
  def parse_input(self, lines=sys.stdin):
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
            print(self.show_mine())
        if show_opponent:
            print(self.show_opponents())
        
        # --place <v> <pos>:[h|v]
        if args.place != None:
          print(f"DBG place {args.place}")

        # --fire <pos> [<id>]
        if args.fire != None:
          print(f"DBG fire {args.fire} returns with value 'hit' | 'miss' | 'sunk' | 'game over'")
          pos_index = None
          id = None
          if len(args.fire) > 0:
            pos_index = self.my_map.pos_index(pos=args.fire[0])
            if pos_index:
              if len(args.fire) > 1:
                id = args.fire[1]
                if id not in self.opponent_maps:
                  id = None
              else:
                id = self.first_opponent
          if pos_index != None and id != None:
            self.fire(id, pos_index['pos'])

  def incoming(self, pos):
    # Test if vessel at pos
    # Return 'x' if 
    res = None
    pos_index = self.my_map.pos_index(pos=pos)
    if pos_index == None:
      return None

    (row, col) = pos_index['index']
    target = self.my_map.map[row][col]
    if target == ' ':
      res = 'x' # miss
      target = res
    elif target.lower() == 'x':
      res = 'X' # repeated miss
      target = res
    else:
      res = target  # lower if not yet hit, upper if previous hit
      if target == target.lower():
        # first time hit
        v_offset = self.my_map.index_to_vessel((row, col))
        assert v_offset != None, f"internal error expected vessel at index {(row, col)}"
        (v, offset) = v_offset
        v.hits[offset] = True
        target = target.upper() # res is lower, next time this index will be upper
        if False not in v.hits:
          # Entire vessel hit, check if any remain
          v.sunk = True
          allsunk = True # assume all sunk
          for v in self.my_map.vessels:
            if v.sunk == False:
              allsunk = False # found one not sunk, so just this vessel sunk, others remain
              break
          self.my_map.allsunk = allsunk
          info_char = 'S' if allsunk else 's'
          res = f"{res}{info_char}"
    self.my_map.map[row][col] = target
    return res

  def update_map(self, opp_id, pos, res):
    # Update map for opponent opp_id
    index = self.my_map.pos_to_index(pos)
    if index != None and (opp_id in self.opponent_maps):
      # result from specific player
      (_player, opp_map) = self.opponent_maps[opp_id]
      (row, col) = index
      opp_map.map[row][col] = res

  def fire(self, opp_id, pos):
    res = None
    index = self.my_map.pos_to_index(pos)

    if index != None and (opp_id in self.opponent_maps):
      # result from specific player
      (player, _map) = self.opponent_maps[opp_id]
      res = player.incoming(pos)

    if res != None:
      # update opp_id map for self and all others 
      players = [self.opponent_maps[id][0] for id in self.opponent_maps if id != opp_id]
      players.append(self)
      for p in players:
        p.update_map(opp_id, pos, res)

    return res

  def add_opponent(self, player):
    res = False
    if hasattr(player, 'id'):
      id = player.id
      if (id != self.id) and ((id in self.opponent_maps) == False):
        self.opponent_maps[id] = (player, Map(self.my_map.nrows, self.my_map.ncols, self.my_map.vlist))
        if self.first_opponent == None:
          self.first_opponent = id
        res = True
    return res
  
  def cmd(self, lines=sys.stdin):
    self.parse_input(lines)
  
  def show_mine(self):
    str = f"id: {self.id} map:{self.my_map.__repr__()}"
    return str
  
  def show_opponent(self, id):
    opp_tuple = self.opponent_maps[id] # (player, map)
    return f"opponent id: {id} map:{opp_tuple[1]}"

  def show_opponents(self):
    str = ""
    for k in self.opponent_maps:
      (player, map) = self.opponent_maps[k]
      str += f"\n{self.show_opponent(k)}"
    return str

  def __repr__(self):
    return f"\n{self.show_mine()}\nopponents ids: {[k for k in self.opponent_maps]}"

if __name__ == "__main__":
# %%
  players = {}
  id = 'me'; players[id] = Player(id)
  id = 'bad2'; players[id] = Player(id)
  id = 'bad3'; players[id] = Player(id)

  ids = [k for k in players]
  for id in ids:
    players[id].my_map.random_place_all()
    other_ids = ids
    other_ids.remove(id)
    for o in other_ids:
      players[id].add_opponent(players[o])

  player1 = players['me']
  player1.cmd(['--info --vessels --show'])
  while True:
      player1.cmd()
