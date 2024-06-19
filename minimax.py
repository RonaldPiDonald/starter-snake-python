from main import *

def minimax(game_state, depth, is_maximizing):
    if depth == 0 or is_game_over(game_state):
        return evaluate_game_state(game_state)

    if is_maximizing:
        max_eval = float('-inf')
        for move in get_all_possible_moves(game_state, "my_snake"):
            eval = minimax(simulate_move(game_state, move), depth - 1, False)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_all_possible_moves(game_state, "opponent_snake"):
            eval = minimax(simulate_move(game_state, move), depth - 1, True)
            min_eval = min(min_eval, eval)
        return min_eval

def get_best_move(game_state):
    best_move = None
    best_value = float('-inf')
    for move in get_all_possible_moves(game_state, "my_snake"):
        move_value = minimax(simulate_move(game_state, move), 3, False)
        if move_value > best_value:
            best_value = move_value
            best_move = move
    return best_move