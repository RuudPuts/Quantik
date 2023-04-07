import random
from collections import defaultdict
from utils import Vector2
from quantik import Game

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
          winnig_move = False # copy.deepcopy(self.game).set_position(piece, vector) is not None

          if winnig_move:
            scores[100][piece.type].append(vector)
          else:
            scores[50][piece.type].append(vector)

    return scores

  def calculate_best_move(self):
      scores = self.calculate_move_scores()
      max_score = max(scores.keys())

      moves = scores[max_score]
      # print("")
      # print(f"{max_score=}")
      # print(f"{moves=}")

      pieces = list(moves.keys())
      best_piece_types = map(lambda x: x.type, self.game.inactive_player.available_pieces)
      best_pieces = list(filter(lambda x: x in best_piece_types, pieces))
      # print(f"{pieces=}")
      # print(f"{best_pieces=}")
      if len(best_pieces) > 0:
        pieces = best_pieces

      random_piece = random.choice(pieces)
      random_position = random.choice(moves[random_piece])

      # print(f"{random_piece=}")
      # print(f"{random_position=}")


      return random_piece, random_position