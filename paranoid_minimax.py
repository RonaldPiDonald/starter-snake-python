import main

def get_possible_moves(game_state):
    # Die möglichen Züge könnten die sicheren Züge sein
    return [move for move, isSafe in main.move.is_move_safe.items() if isSafe]



def game_over(game_state):
    # Das Spiel ist vorbei, wenn die Schlange tot ist
    return game_state['you']['health'] == 0

def evaluate(game_state):
    # Eine einfache Bewertungsfunktion könnte die Gesundheit der Schlange sein
    return game_state['you']['health']

def get_children(node):
    # Die Kinder eines Knotens könnten die möglichen Züge von diesem Knoten aus sein
    return get_possible_moves(node)



def simulate_move(game_state, move):
    # Erstellt eine Kopie des Spielzustands, um den Zug zu simulieren
    new_game_state = game_state.copy()

    # Aktualisiert die Position des Kopfes der Schlange basierend auf dem Zug
    if move == "up":
        new_game_state['you']['body'][0]['y'] += 1
    elif move == "down":
        new_game_state['you']['body'][0]['y'] -= 1
    elif move == "left":
        new_game_state['you']['body'][0]['x'] -= 1
    elif move == "right":
        new_game_state['you']['body'][0]['x'] += 1

    # Aktualisiert die Gesundheit der Schlange
    new_game_state['you']['health'] -= 1

    return new_game_state


def paranoid_minimax(node, depth, maximizing_player, game_state):

  if maximizing_player:
      max_eval = float('-inf')
      for child in get_children(node):
          eval = paranoid_minimax(child, depth - 1, False, game_state)
          max_eval = max(max_eval, eval)
      return max_eval
  else:
      min_eval = float('inf')
      for child in get_children(node):
          eval = paranoid_minimax(child, depth - 1, True, game_state)
          min_eval = min(min_eval, eval)
      return min_eval

def get_best_move(game_state):
  best_score = float('-inf')
  best_move = None

  for move in get_possible_moves(game_state):
      new_game_state = simulate_move(game_state, move)
      score = paranoid_minimax(new_game_state, 3, False, new_game_state)  # 3 ist die Suchtiefe
      if score > best_score:
          best_score = score
          best_move = move

  return best_move


