import random
from collections import defaultdict
from utils import Vector2
from quantik import Game, Piece

class AI:
  game: Game

  def __init__(self, game):
    self.game = game

  def calculate_move_scores(self):
    scores = defaultdict(lambda: defaultdict(list))

    for row in range(4):
      for column in range(4):
        vector = Vector2(column, row)

        if self.game.piece_at(vector) is not None:
          continue

        for piece in self.game.allowed_pieces_at(vector)[self.game.active_player]:
          score = self.calculate_score(piece, vector)
          scores[score][piece.type].append(vector)

    return scores

  def calculate_score(self, piece: Piece, vector: Vector2):
    winnig_move, _ = self.game.is_winning_move(piece, vector)
    score = 50

    if winnig_move:
      score = 100

    return score

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