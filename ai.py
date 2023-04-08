import random
import sys
from collections import defaultdict
from utils import Vector2
from quantik import Game, Piece

class AI:
  game: Game

  def __init__(self, game):
    self.game = game

  def available_vectors(self, game: Game):
    vectors = []
    for row in range(4):
      for column in range(4):
        vector = Vector2(column, row)

        if game.piece_at(vector) is None:
          vectors.append(vector)
    return vectors

  def calculate_move_scores(self, log=False):
    print(" >> CALCULATING!")
    # print(f"    {sys.maxsize}")
    scores = defaultdict(lambda: defaultdict(list))

    for vector_idx, vector in enumerate(self.available_vectors(self.game)):
        # print(f"    Position {vector_idx} - {vector}")
        for piece_idx, piece in enumerate(self.game.allowed_pieces_at(vector)[self.game.active_player]):
          score = self.calculate_score(self.game, piece, vector, log=log)
          # print(f"       Piece {piece_idx} - {piece.type} -> {score}")
          scores[score][piece.type].append(vector)
    print(" >> DONE!")

    return scores

  def calculate_score(self, game: Game, piece: Piece, vector: Vector2, depth=0, is_maximizing=True, log=False):
    score = 0

    if depth >= 2:
      return score

    if log:
      print("")
      print("")
      print(f"game orig: {len(self.available_vectors(game))}")
    game = game.clone()
    piece = game.active_player.get_piece(piece.type)
    if log:
      print(f"game clone: {len(self.available_vectors(game))}")
    winning_move = game.set_position(piece, vector)
    if log:
      print(f"game change: {len(self.available_vectors(game))}")
      print("")
      print("")

    if winning_move:
      score = 1
      if game.active_player != self.game.active_player:
        score += -1
    else:
      best_score = sys.maxsize
      if is_maximizing:
        best_score *= -1

      for vector in self.available_vectors(game):
        pieces = game.allowed_pieces_at(vector)
        if pieces == None:
          continue

        for piece in pieces[game.active_player]:
          piece_score = self.calculate_score(game, piece, vector, depth=depth+1, is_maximizing=not is_maximizing)

          if is_maximizing:
            best_score = max(best_score, piece_score)
          else:
            best_score = min(best_score, piece_score)

      score = best_score

    return score - depth

    # return score

  def calculate_best_move(self):
    scores = self.calculate_move_scores()
    max_score = max(scores.keys())

    moves = scores[max_score]

    pieces = list(moves.keys())
    best_piece_types = map(lambda x: x.type, self.game.inactive_player.available_pieces)
    best_pieces = list(filter(lambda x: x in best_piece_types, pieces))
    if len(best_pieces) > 0:
      pieces = best_pieces

    random_piece = random.choice(pieces)
    random_position = random.choice(moves[random_piece])

    return random_piece, random_position