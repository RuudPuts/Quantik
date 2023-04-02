from dataclasses import dataclass
from enum import Enum
import math

def flatten(list):
  return [item for sublist in list for item in sublist]

@dataclass
class Vector2:
  x: int
  y: int

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

class Game:
  player1: Player
  player2: Player
  active_player: Player
  winner = None

  def __init__(self):
    self.player1 = Player(color="white")
    self.player2 = Player(color="black")
    self.active_player = self.player1

  @property
  def players(self):
    return [self.player1, self.player2]

  def toggle_active_player(self):
    if self.active_player == self.player1:
      self.active_player = self.player2
    else:
      self.active_player = self.player1

  def set_position(self, piece, position):
    if self.winner is not None:
      return None

    if self.piece_at(position) != None:
      return None

    if piece.type not in set(map(lambda x: x.type, flatten(self.allowed_pieces_at(position).values()))):
      return None

    piece.position = position

    for positions in self.interesting_positions_for(position)[:-1]:
      section_pieces = positions + [position]
      pieces = list(map(lambda x: self.piece_at(x), section_pieces))
      pieces = set([piece[0].type for piece in pieces if piece is not None])

      if len(pieces) == 4:
        self.winner = (self.active_player, section_pieces)
        return self.winner

    self.toggle_active_player()

    return None

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














import pygame

# pygame setup
pygame.init()
window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Quantik")
clock = pygame.time.Clock()
running = True
dt = 0

game = Game()
selected_piece = None
# result1 = game.set_position(game.player1.cylinder, Vector2(0, 0))
# result2 = game.set_position(game.player2.cylinder, Vector2(1, 2))
# result3 = game.set_position(game.player1.triangle, Vector2(1, 1))
# result4 = game.set_position(game.player2.square, Vector2(1, 0))
# result5 = game.set_position(game.player1.plus, Vector2(0, 1))

def draw_text(text, position, color, size=48):
  font = pygame.font.SysFont(None, size)
  image = font.render(text, True, color)

  window.blit(image, position)

  return image.get_rect()

def determine_board_size():
  board_size = window.get_height() * 0.8

  x_offset = window.get_width() / 2 - board_size / 2
  y_offset = (window.get_height() - board_size) / 2

  return board_size, x_offset, y_offset

def draw_play_board():
  board_size, x_offset, y_offset = determine_board_size()
  square_size = board_size / 2

  # Left top
  pygame.draw.rect(window, "grey", (x_offset, y_offset, square_size, square_size))# ((x_offset, y_offset), (x_offset + square_size / 2, y_offset + square_size / 2)), fill="grey")

  # Right Top
  pygame.draw.rect(window, "lightgrey", (x_offset + square_size, y_offset, square_size, square_size))#((x_offset + square_size / 2, y_offset), (x_offset + square_size, y_offset + square_size / 2)), fill="lightgrey")

  # Right bottom
  pygame.draw.rect(window, "grey", (x_offset + square_size, y_offset + square_size, square_size, square_size))#((x_offset  + square_size / 2, y_offset + square_size / 2), (x_offset + square_size, y_offset + square_size)), fill="grey")

  # Left bottom
  pygame.draw.rect(window, "lightgrey", (x_offset, y_offset + square_size, square_size, square_size))#((x_offset, y_offset + square_size / 2), (x_offset + square_size / 2, y_offset + square_size)), fill="lightgrey")

def draw_board_pieces():
  board_grid_size = 4

  board_size, board_x_offset, board_y_offset = determine_board_size()
  piece_square_size = board_size / board_grid_size
  piece_size = board_size / 8





  # y = board_y_offset + piece_square_size / 2
  # for row in range(board_grid_size):
  #   x = board_x_offset + piece_square_size / 2
  #   for column in range(board_grid_size):
  #     if column == 1 and row == 0:
  #       exclude_size = 40

  #       blob_x = board_x_offset + column * piece_square_size + piece_square_size / 2
  #       blob_y = board_y_offset + row * piece_square_size + piece_square_size / 2
  #       pygame.draw.circle(window, "lightblue", (blob_x, blob_y), exclude_size)

  #       _, _, _, exclude_positions = game.interesting_positions_for((column, row))

  #       for position in exclude_positions:
  #         exclude_x = board_x_offset + position.x * piece_square_size + piece_square_size / 2
  #         exclude_y = board_y_offset + position.y * piece_square_size + piece_square_size / 2
  #         pygame.draw.rect(window, "red", (exclude_x - exclude_size / 2, exclude_y - exclude_size / 2, exclude_size, exclude_size))

  if game.winner is not None:
    draw_text(f"{game.winner[0].name} player wins!", (window.get_width() / 2 - 140, board_y_offset * 0.4), game.winner[0].color)

    y = board_y_offset + piece_square_size / 2
    for row in range(board_grid_size):
      x = board_x_offset + piece_square_size / 2
      for column in range(board_grid_size):
        if column == 1 and row == 0:
          exclude_size = piece_square_size * 0.75

          for position in game.winner[1]:
            exclude_x = board_x_offset + position.x * piece_square_size + piece_square_size / 2
            exclude_y = board_y_offset + position.y * piece_square_size + piece_square_size / 2
            pygame.draw.rect(window, "green", (exclude_x - exclude_size / 2, exclude_y - exclude_size / 2, exclude_size, exclude_size))

  y = board_y_offset + piece_square_size / 2
  for row in range(board_grid_size):
    x = board_x_offset + piece_square_size / 2
    for column in range(board_grid_size):
      position = Vector2(column, row)

      position_data = game.piece_at(position)
      if position_data:
        piece = position_data[0]
        player = position_data[1]
        draw_piece(piece.type, player.color, (x, y), piece_size)
      else:
        if (column < 2 and row < 2) or (column >= 2 and row >= 2):
          pygame.draw.circle(window, "lightgrey", (x, y), 10)
        else:
          pygame.draw.circle(window, "grey", (x, y), 10)

        allowed_pieces = game.allowed_pieces_at(Vector2(column, row))
        piece_option_size = piece_size / 4
        piece_option_y = y - piece_option_size * 0.75 - 10
        for (allowed_piece_player, allowed_pieces) in allowed_pieces.items():
          piece_option_x = x - (len(allowed_pieces) * piece_option_size * 0.75) / 2
          for allowed_piece in allowed_pieces:
            draw_piece(allowed_piece.type, allowed_piece_player.color, (piece_option_x, piece_option_y), piece_option_size)

            piece_option_x += piece_option_size * 1.2
          piece_option_y += piece_option_size * 2.8


      x += piece_square_size
    y += piece_square_size

inventory_piece_size = 80
inventory_y_offset = 100
inventory_piece_offset = inventory_piece_size * 1.5
def draw_players():
    board_size, board_x_offset, board_y_offset = determine_board_size()
    text_x_offset = 60

    player_x_offset = window.get_width() / 2 + board_size / 2

    for idx, player in enumerate(game.players):
      if idx > 0:
        text_x_offset += player_x_offset

      title_y_offset = board_y_offset
      title_rect = draw_text(f"{player.name} player", (text_x_offset, title_y_offset), player.color)
      if game.active_player == player:
        bar_y_offset = title_y_offset + title_rect.height + 4
        pygame.draw.rect(window, player.color, (text_x_offset, bar_y_offset, title_rect.width, 4))

      piece_x_offset = board_x_offset / 2 # text_x_offset + 110
      if idx > 0:
          piece_x_offset += player_x_offset

      piece_y_offset = board_y_offset + inventory_y_offset
      for idx, piece in enumerate(player.available_pieces):
        draw_piece(piece.type, player.color, (piece_x_offset, piece_y_offset), inventory_piece_size)
        if player == game.active_player and piece == selected_piece:
          pygame.draw.rect(window, player.color, (piece_x_offset - inventory_piece_size/2, piece_y_offset + inventory_piece_size/2 + 4, inventory_piece_size, 4))


        piece_y_offset += inventory_piece_offset

def draw_piece(piece: PieceType, color: str, center, size: int):
  match piece:
    case PieceType.CYLINDER:
      pygame.draw.circle(window, color, center, size / 2)
    case PieceType.TRIANGLE:
      pygame.draw.polygon(window, color, [
        [center[0] - size / 2, center[1] + size / 2], # Left bottom
        [center[0] + size / 2, center[1] + size / 2], # Right bottom
        [center[0], center[1] - size / 2] # Center top
        ])
    case PieceType.PLUS:
      bar_size = size / 4
      pygame.draw.rect(window, color, (center[0] - bar_size / 2, center[1] - size / 2, bar_size, size))
      pygame.draw.rect(window, color, (center[0] - size / 2, center[1] - bar_size / 2, size, bar_size))
    case PieceType.SQUARE:
      pygame.draw.rect(window, color, (center[0] - size / 2, center[1] - size / 2, size, size))

def draw_mouse():
  mouse_pos = pygame.mouse.get_pos()
  position = Vector2(mouse_pos[0], mouse_pos[1])
  # pygame.draw.circle(window, "orange", (position.x, position.y), 20)
  if selected_piece:
    size = 40
    draw_piece(selected_piece.type, game.active_player.color, (position.x, position.y - size), size)

  board_size, board_x_offset, board_y_offset = determine_board_size()

  mouse_interaction = mouse_interaction_with()
  if mouse_interaction is None:
    return

  section, data = mouse_interaction

  if section == "board":
    square_size = board_size / 4
    column = data[0]
    row = data[1]

    blop_pos = (
      board_x_offset + column * square_size + square_size / 2,
      board_y_offset + row * square_size + square_size / 2
    )
    # pygame.draw.circle(window, "red", blop_pos, 40)
  else:
    row = data
    row_height = inventory_piece_offset

    piece_x_offset = board_x_offset * 0.5
    piece_y_offset = board_y_offset + inventory_y_offset + row * row_height
    if section == "player1" and game.active_player == game.player1:
      pygame.draw.circle(window, game.player2.color, (piece_x_offset, piece_y_offset), int(inventory_piece_size * .8), 5)
      # pygame.draw.rect(window, "blue", (board_x_offset * 0.36, board_y_offset * 1.8 + row * row_height, board_x_offset * 0.6 - board_x_offset * 0.36, row_height))
    elif section == "player2" and game.active_player == game.player2:
      piece_x_offset += board_size + board_x_offset
      pygame.draw.circle(window, game.player1.color, (piece_x_offset, piece_y_offset), int(inventory_piece_size * .8), 5)
      # pygame.draw.rect(window, "yellow", (board_size + board_x_offset + board_x_offset * 0.36, board_y_offset * 1.8 + row * row_height, board_x_offset * 0.6 - board_x_offset * 0.36, row_height))

def mouse_interaction_with():
  mouse_pos = pygame.mouse.get_pos()
  position = Vector2(mouse_pos[0], mouse_pos[1])

  board_size, board_x_offset, board_y_offset = determine_board_size()
  if position.x >= board_x_offset and position.x <= board_x_offset + board_size:
    if position.y >= board_y_offset and position.y <= board_y_offset + board_size:
      # Board
      relative_x = position.x - board_x_offset
      relative_y = position.y - board_y_offset

      square_size = board_size / 4
      column = math.floor(relative_x / square_size)
      row = math.floor(relative_y / square_size)

      return "board", (column, row)
  else:
    # Player inventory
    relative_y = position.y
    relative_x = position.x
    if relative_x > board_x_offset:
      # Player 2
      relative_x = relative_x - board_size - board_x_offset

    if relative_x >= board_x_offset * 0.36 and relative_x <= board_x_offset * 0.6:
      if relative_y >= board_y_offset * 1.8:
        row_height = 115
        row = math.floor((relative_y - board_y_offset * 1.8) / row_height)

        if relative_x != position.x:
          return "player2", row
        else:
          return "player1", row

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                  if game.winner is not None:
                    game = Game()
                  else:
                    mouse_interaction = mouse_interaction_with()
                    if mouse_interaction is None:
                      continue

                    section, data = mouse_interaction
                    if section == "board" and selected_piece is not None:
                      print(f"Place piece {selected_piece} at {data}")
                      game.set_position(selected_piece, Vector2(data[0], data[1]))
                      selected_piece = None
                    elif section =="player1" and game.active_player == game.player1:
                      if data < len(game.player1.available_pieces):
                        selected_piece = game.player1.available_pieces[data]
                        print(f"Select player1 {selected_piece}")
                    elif section =="player2" and game.active_player == game.player2:
                      if data < len(game.player2.available_pieces):
                        selected_piece = game.player2.available_pieces[data]
                        print(f"Select player2 {selected_piece}")

    # fill the window with a color to wipe away anything from last frame
    window.fill("lightgreen")

    draw_play_board()
    draw_board_pieces()
    draw_players()

    draw_mouse()

    # pygame.draw.circle(window, "red", player_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_s]:
      game.toggle_active_player()
    # if keys[pygame.K_w]:
    #     player_pos.y -= 300 * dt
    # if keys[pygame.K_s]:
    #     player_pos.y += 300 * dt
    # if keys[pygame.K_a]:
    #     player_pos.x -= 300 * dt
    # if keys[pygame.K_d]:
    #     player_pos.x += 300 * dt

    # flip() the display to put your work on window
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    # dt = clock.tick(1) / 1000

pygame.quit()