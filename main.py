import math
import pygame
from ai import AI
from collections import defaultdict
from utils import Vector2
from quantik import Game, PieceType

# pygame setup
pygame.init()
window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Quantik")
clock = pygame.time.Clock()
running = True
frame_time = 0

# game setup
game = Game()
selected_piece = None

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
  board_grid_size = 4

  board_size, board_x_offset, board_y_offset = determine_board_size()
  square_size = board_size / 2
  piece_square_size = board_size / board_grid_size

  # Left top
  pygame.draw.rect(window, "grey", (board_x_offset, board_y_offset, square_size, square_size))

  # Right Top
  pygame.draw.rect(window, "lightgrey", (board_x_offset + square_size, board_y_offset, square_size, square_size))

  # Right bottom
  pygame.draw.rect(window, "grey", (board_x_offset + square_size, board_y_offset + square_size, square_size, square_size))

  # Left bottom
  pygame.draw.rect(window, "lightgrey", (board_x_offset, board_y_offset + square_size, square_size, square_size))

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
  elif game.in_stale_mate:
    draw_text(f"It's a draw!", (window.get_width() / 2 - 110, board_y_offset * 0.4), "orange")


def draw_board_pieces():
  board_grid_size = 4

  board_size, board_x_offset, board_y_offset = determine_board_size()
  piece_square_size = board_size / board_grid_size
  piece_size = board_size / 8

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

      if player2_is_bot and game.active_player == game.player2:
        ai = AI(game)
        scores = ai.calculate_move_scores()

        # Convert scores to position:[piece] mapping
        ai_scores = defaultdict(lambda: defaultdict(dict))
        for score in scores:
          for piece in scores[score]:
            for vector in scores[score][piece]:
              ai_scores[(vector.x, vector.y)][piece] = score

        allowed_pieces = game.allowed_pieces_at(Vector2(column, row))
        if allowed_pieces is not None:
          piece_option_size = piece_size / 4
          piece_option_y = y - piece_option_size * 0.75 - 10
          for (allowed_piece_player, allowed_pieces) in allowed_pieces.items():
            if allowed_piece_player != game.player2:
              piece_option_y += piece_option_size * 2.8
              continue

            piece_option_x = x - (len(allowed_pieces) * piece_option_size * 0.75) / 2
            for allowed_piece in allowed_pieces:
              draw_piece(allowed_piece.type, allowed_piece_player.color, (piece_option_x, piece_option_y), piece_option_size)
              if player2_is_bot and allowed_piece_player == game.player2:
                score = ai_scores[(column, row)][allowed_piece.type]
                draw_text(str(score), (piece_option_x - piece_option_size/2, piece_option_y+piece_option_size/1.6), "red", 20)

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
      title = f"{player.name} player"
      if player2_is_bot and player == game.player2:
        title += " (AI)"
      title_rect = draw_text(title, (text_x_offset, title_y_offset), player.color)
      if game.active_player == player:
        bar_y_offset = title_y_offset + title_rect.height + 4
        pygame.draw.rect(window, player.color, (text_x_offset, bar_y_offset, title_rect.width, 4))

      piece_x_offset = board_x_offset / 2
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

  if selected_piece:
    piece_size = 40
    draw_piece(selected_piece.type, game.active_player.color, (position.x, position.y - piece_size), piece_size)

  board_size, board_x_offset, board_y_offset = determine_board_size()

  highlight_mouse = False
  if highlight_mouse:
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
      pygame.draw.circle(window, "red", blop_pos, 40)
    else:
      row = data
      row_height = inventory_piece_offset

      piece_x_offset = board_x_offset * 0.5
      piece_y_offset = board_y_offset + inventory_y_offset + row * row_height
      if section == "player1" and game.active_player == game.player1:
        pygame.draw.circle(window, game.player2.color, (piece_x_offset, piece_y_offset), int(inventory_piece_size * .8), 5)
      elif section == "player2" and game.active_player == game.player2:
        piece_x_offset += board_size + board_x_offset
        pygame.draw.circle(window, game.player1.color, (piece_x_offset, piece_y_offset), int(inventory_piece_size * .8), 5)

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


# game.set_position(game.player1.cylinder, Vector2(0, 0))
# result2 = game.set_position(game.player2.cylinder, Vector2(1, 2))
# result3 = game.set_position(game.player1.triangle, Vector2(1, 1))
# result4 = game.set_position(game.player2.square, Vector2(1, 0))
# result5 = game.set_position(game.player1.plus, Vector2(0, 1))

player2_is_bot = True
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                  if game.winner is not None or game.in_stale_mate:
                    game = Game()
                  else:
                    if player2_is_bot and game.active_player == game.player2:
                      ai = AI(game)
                      piece_type, position = ai.calculate_best_move()
                      game.set_position(game.active_player.get_piece(piece_type), position)
                    else:
                      mouse_interaction = mouse_interaction_with()
                      if mouse_interaction is None:
                        continue

                      section, data = mouse_interaction
                      if section == "board" and selected_piece is not None:
                        # Place piece on location on board
                        game.set_position(selected_piece, Vector2(data[0], data[1]))
                        selected_piece = None
                      elif section =="player1" and game.active_player == game.player1:
                        if data < len(game.player1.available_pieces):
                          # Clicked on item in Player 1 inventory
                          selected_piece = game.player1.available_pieces[data]
                      elif section =="player2" and game.active_player == game.player2:
                        if data < len(game.player2.available_pieces):
                          # Clicked on item in Player 2 inventory
                          selected_piece = game.player2.available_pieces[data]

    # fill the window with a color to wipe away anything from last frame
    window.fill("lightgreen")

    draw_play_board()
    draw_board_pieces()
    draw_players()

    draw_mouse()


    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
      game = Game()

    pygame.display.flip()

    # limits FPS to 60
    frame_time = clock.tick(60) / 1000

pygame.quit()