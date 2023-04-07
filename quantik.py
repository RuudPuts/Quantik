from dataclasses import dataclass
from enum import Enum
from utils import flatten, Vector2
import json

class PieceType(Enum):
  CYLINDER = "Cylinder"
  TRIANGLE = "Triange"
  PLUS = "Plus"
  SQUARE = "Square"

@dataclass
class Piece:
  type: PieceType
  position: Vector2 = None

class Player:
  color: str

  cylinder: Piece
  triangle: Piece
  orb: Piece
  square: Piece

  def __init__(self, color: str):
    self.color = color

    self.cylinder = Piece(PieceType.CYLINDER)
    self.triangle = Piece(PieceType.TRIANGLE)
    self.plus = Piece(PieceType.PLUS)
    self.square = Piece(PieceType.SQUARE)

  @property
  def name(self):
    return self.color.capitalize()

  @property
  def pieces(self):
    return [
      self.cylinder,
      self.triangle,
      self.plus,
      self.square
    ]

  @property
  def available_pieces(self):
    return list(filter(lambda x: x.position == None, self.pieces))

  @property
  def used_pieces(self):
    return list(filter(lambda x: x.position != None, self.pieces))

  def get_piece(self, type: PieceType):
    return list(filter(lambda x: x.type == type, self.pieces))[0]

class Game:
  player1: Player
  player2: Player
  active_player: Player
  winner = None

  def __init__(self, data=None):
    if data:
      self.player1 = Player(color=data["player1"]["color"])
      self.player2 = Player(color=data["player2"]["color"])
      if data["active_player"] == self.player1.color:
        self.active_player = self.player1
      else:
        self.active_player = self.player2

      moves = {
        self.player1.color: data["player1"]["pieces"],
        self.player2.color: data["player2"]["pieces"]
      }
      for player_color, pieces in moves.items():
        # 🤷‍♂️
        if player_color == self.player1.color:
          player = self.player1
        else:
          player = self.player2

        for piece_type_value, position in pieces.items():
          if position is None:
            continue
          piece_type = PieceType(piece_type_value)

          piece = player.get_piece(piece_type)
          piece.position = Vector2(position[0], position[1])
    else:
      self.player1 = Player(color="white")
      self.player2 = Player(color="black")
      self.active_player = self.player1

  def dump(self, to_file=False):
    def player_pieces(player):
      pieces = {}
      for piece in player.pieces:
        if piece.position:
          pieces[piece.type.value] = (piece.position.x, piece.position.y)
        else:
          pieces[piece.type.value] = None
      return pieces

    data = {
      "player1": {
        "color": self.player1.color,
        "pieces": player_pieces(self.player1)
      },
      "player2": {
        "color": self.player2.color,
        "pieces": player_pieces(self.player2)
      },
      "active_player": self.active_player.color
    }

    data_json = json.dumps(data, indent=2)
    if to_file:
      with open("game.json", "w") as outfile:
        outfile.write(data_json)
    else:
      print("")
      print(data_json)
      print("")

    return data

  @property
  def players(self):
    return [self.player1, self.player2]

  @property
  def inactive_player(self):
    return list(filter(lambda x: x != self.active_player, self.players))[0]

  def toggle_active_player(self):
    if self.active_player == self.player1:
      self.active_player = self.player2
    else:
      self.active_player = self.player1

  @property
  def in_stale_mate(self):
    if self.winner is not None:
      return False

    return len(self.active_player.available_pieces) == 0

  def set_position(self, piece, position):
    if self.winner is not None:
      return False

    if self.piece_at(position) != None:
      return False

    if piece.type not in set(map(lambda x: x.type, flatten(self.allowed_pieces_at(position).values()))):
      return False

    is_winning_move, winning_move_pieces = self.is_winning_move(piece, position)
    if is_winning_move:
      self.winner = (self.active_player, winning_move_pieces)

    piece.position = position

    self.toggle_active_player()

    return True

  def piece_at(self, position):
    for player in self.players:
      for piece in player.used_pieces:
        if piece.position == position:
          return (piece, player)

    return None

  # def print_pieces(self):
  #   for player in self.players:
  #     for piece in player.used_pieces:
  #       # if piece.position == position:
  #       #   return (piece, player)
  #       print(piece.position, piece)

  #   return None

  def allowed_pieces_at(self, position):
    if self.piece_at(position) is not None:
      return None

    _, _, _, exclude_positions = self.interesting_positions_for(position)
    exclude_pieces_orig = list(map(lambda x: self.piece_at(x), exclude_positions))
    exclude_pieces = set([piece[0].type for piece in exclude_pieces_orig if piece is not None])

    pieces = {}
    for player in self.players:
      pieces[player] = list(filter(lambda x: x.type not in exclude_pieces, player.available_pieces))

    return pieces

  def interesting_positions_for(self, position):
    horizontal_exclusions = [(column, position.y) for column in range(4) if column != position.x]
    vertical_exclusions = [(position.x, row) for row in range(4) if row != position.y]

    column = position.x
    row = position.y
    if (column < 2 and row < 2): # Left top
      quadrant_exclusions = [(0, 0), (1, 0), (0, 1), (1, 1)]
    elif (column < 2 and row >= 2): # Left bottom
      quadrant_exclusions = [(0, 2), (1, 2), (0, 3), (1, 3)]
    elif (column >= 2 and row < 2): # Right top
      quadrant_exclusions = [(2, 0), (3, 0), (2, 1), (3, 1)]
    elif (column >= 2 and row >= 2): # Right bottom)
      quadrant_exclusions = [(2, 2), (3, 2), (2, 3), (3, 3)]
    else:
      raise Exception(f"Can't determine quadrant for position {position}")
    if position in quadrant_exclusions:
      quadrant_exclusions.remove(position)

    horizontal_vectors = list(map(lambda x: Vector2(x[0], x[1]), horizontal_exclusions))
    vertical_vectors = list(map(lambda x: Vector2(x[0], x[1]), vertical_exclusions))
    quadrant_vectors = list(map(lambda x: Vector2(x[0], x[1]), quadrant_exclusions))
    all_vectors = horizontal_vectors + vertical_vectors + quadrant_vectors

    return horizontal_vectors, vertical_vectors, quadrant_vectors, all_vectors

  def is_winning_move(self, piece, position):
    piece.position = position

    for positions in self.interesting_positions_for(position)[:-1]:
      section_pieces = positions + [position]
      pieces = list(map(lambda x: self.piece_at(x), section_pieces))
      pieces = set([piece[0].type for piece in pieces if piece is not None])

      if len(pieces) == 4:
        piece.position = None
        return True, section_pieces

    piece.position = None
    return False, None