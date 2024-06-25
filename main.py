import a_star
import os
import random
import typing
from flask import Flask, request
from flood_fill import *
app = Flask(__name__)

@app.route("/", methods=["GET"])
def on_info():
    return info()

@app.route("/start", methods=["POST"])
def on_start():
    game_state = request.get_json()
    my_head(game_state)
    return "ok"

@app.route("/move", methods=["POST"])
def on_move():
    game_state = request.get_json()
    return move(game_state)

@app.route("/end", methods=["POST"])
def on_end():
    game_state = request.get_json()
    end(game_state)
    return "ok"

@app.after_request
def identify_server(response):
    response.headers.set(
        "server", "battlesnake/replit/starter-snake-python"
    )
    return response

def info() -> typing.Dict:
    print("INFO")
    return {
        "apiversion": "1",
        "author": "Ronald",
        "color": "#D3D3D3",
        "head": "nr-rocket",
        "tail": "bonhomme",
    }

def my_head(game_state: typing.Dict):
    print("GAME my_head")

def end(game_state: typing.Dict):
    print("GAME OVER\n")

def move(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {
      "up": True, 
      "down": True, 
      "left": True, 
      "right": True
    }
    my_head = game_state["you"]["body"][0]
    my_neck = game_state["you"]["body"][1]
    my_size = game_state[ "you"]["length"] 
    my_id = game_state["you"]["id"]
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    my_body = game_state['you']['body']
    opponents = [snake for snake in game_state['board']['snakes'] if snake['id'] != my_id]
    largest_opponent = max(opponents, key=lambda snake: snake['length'], default = None)
    my_tail = game_state["you"]["body"][-1]
    
    if my_neck["x"] < my_head["x"]:
        is_move_safe["left"] = False
    elif my_neck["x"] > my_head["x"]:
        is_move_safe["right"] = False
    elif my_neck["y"] < my_head["y"]:
        is_move_safe["down"] = False
    elif my_neck["y"] > my_head["y"]:
        is_move_safe["up"] = False
    
    
    
    if my_head["x"] == 0:
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:
        is_move_safe["right"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False
    if my_head["y"] == board_height - 1:
        is_move_safe["up"] = False
    
    
    for body_part in my_body[1:]:
        if body_part["x"] == my_head["x"]:
            if body_part["y"] == my_head["y"] - 1:
                is_move_safe["down"] = False
            if body_part["y"] == my_head["y"] + 1:
                is_move_safe["up"] = False
        if body_part["y"] == my_head["y"]:
            if body_part["x"] == my_head["x"] - 1:
                is_move_safe["left"] = False
            if body_part["x"] == my_head["x"] + 1:
                is_move_safe["right"] = False
    
    
    
    for opponent in opponents:
    
        for body_part in opponent['body']:
            if body_part["x"] == my_head["x"]:
                if body_part["y"] == my_head["y"] - 1:
                    is_move_safe["down"] = False
                if body_part["y"] == my_head["y"] + 1:
                    is_move_safe["up"] = False
            if body_part["y"] == my_head["y"]:
                if body_part["x"] == my_head["x"] - 1:
                    is_move_safe["left"] = False
                if body_part["x"] == my_head["x"] + 1:
                    is_move_safe["right"] = False
    
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)
    my_path_tail = a_star.a_star_search((my_head['x'], my_head['y']), (my_tail['x'], my_tail['y']), game_state['board'], game_state['board']['snakes'], my_id)
    
    
    food = game_state['board']['food']
    def calc_board():
        obstacles = set()
        for part in my_body:
            obstacles.add((part["x"], part["y"]))
        for opponent in opponents:
            for part in opponent["body"]:
                obstacles.add((part["x"], part["y"]))
        # Check each possible move using flood fill
        move_options = {}
        for move in safe_moves:
            if move == "up":
                new_head = (my_head["x"], my_head["y"] - 1)
            elif move == "down":
                new_head = (my_head["x"], my_head["y"] + 1)
            elif move == "left":
                new_head = (my_head["x"] - 1, my_head["y"])
            elif move == "right":
                new_head = (my_head["x"] + 1, my_head["y"])

            accessible_area = flood_fill(game_state['board'], new_head[0], new_head[1], board_width, board_height, obstacles)
            move_options[move] = accessible_area
    
    
    
    next_move = None
    if food:
        sorted_foods = sorted(food, key=lambda f: abs(f['x'] - my_head['x']) + abs(f['y'] - my_head['y']))
        for food_item in sorted_foods:
            my_path = a_star.a_star_search((my_head['x'], my_head['y']), (food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)
            if not my_path:
                continue
            closest_food = True
    
            for opponent in opponents:
                opponent_path = a_star.a_star_search((opponent["head"]["x"], opponent["head"]["y"]), (food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)
                if not opponent_path:
                    continue
                if len(opponent_path) < len(my_path) or (len(opponent_path) == len(my_path) and my_size <= opponent["length"]):
                    closest_food = False
                    break   
    
            if closest_food:
                food_tail_path = a_star.a_star_search((food_item['x'], food_item['y']), (my_tail['x'], my_tail['y']), game_state['board'], game_state['board']['snakes'], my_id)
                if len(sorted_foods) == 1 and food_tail_path:
                    print("path")
                    next_move = my_path[0]
                    break
    
                for foods in sorted_foods:
                    food_path = a_star.a_star_search((foods['x'], foods['y']), (food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)
                    if foods != food_item:
                        if not food_path and len(sorted_foods) > 1:
                            if my_path:
                                print("path not safe")
                                is_move_safe[my_path[0]] = False
                        else:
                            if my_path:
                                print("path")
                                next_move = my_path[0]
                                break
                else: 
                    continue   
                break
    
        else:
    
            if largest_opponent['length'] < my_size:
                for foods in sorted_foods:
                    food_path = a_star.a_star_search((foods['x'], foods['y']), (food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)              
                    food_tail_path = a_star.a_star_search((foods['x'], foods['y']), (my_tail['x'], my_tail['y']), game_state['board'], game_state['board']['snakes'], my_id)
                    if foods != food_item:
                        if not food_path and len(sorted_foods) > 1 and not food_tail_path and my_path:
                            print("path not safe")
                            is_move_safe[my_path[0]] = False
                        else:
                            if my_path:
                                print("path size")
                                next_move = my_path[0]
                                break
                            else:
                                calc_board()
                                print("flood fill")
                                next_move = max(move_options, key=move_options.get)
    
                if my_path:  
                    print("path")
                    next_move = my_path[0]       
    
            elif my_path_tail:
                print("tail")
                next_move = my_path_tail[0]
    
            else:
                calc_board()
                print("flood fill")
                next_move = max(move_options, key=move_options.get)
    
    else:
        calc_board()
        print("flood fill")
        next_move = max(move_options, key=move_options.get)
    
    if next_move == None:
        calc_board()
        print("flood fill")
        next_move = max(move_options, key=move_options.get)
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
