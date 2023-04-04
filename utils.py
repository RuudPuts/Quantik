from dataclasses import dataclass

@dataclass
class Vector2:
  x: int
  y: int

def flatten(list):
  return [item for sublist in list for item in sublist]