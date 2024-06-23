import random
import typing
import a_star
import minimax

import logging
import os
import typing

from flask import Flask
from flask import request


def run_server(handlers: typing.Dict):
    app = Flask("Battlesnake")

    @app.get("/")
    def on_info():
        return handlers["info"]()

    @app.post("/start")
    def on_start():
        game_state = request.get_json()
        handlers["start"](game_state)
        return "ok"

    @app.post("/move")
    def on_move():
        game_state = request.get_json()
        return handlers["move"](game_state)

    @app.post("/end")
    def on_end():
        game_state = request.get_json()
        handlers["end"](game_state)
        return "ok"

    @app.after_request
    def identify_server(response):
        response.headers.set(
            "server", "battlesnake/replit/starter-snake-python"
        )
        return response

    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8000"))

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    print(f"\nRunning Battlesnake at http://{host}:{port}")
    app.run(host=host, port=port)

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
    my_size = game_state["you"]["length"]
    my_id = game_state["you"]["id"]
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    my_body = game_state['you']['body']
    opponents = [snake for snake in game_state['board']
                 ['snakes'] if snake['id'] != my_id]
    largest_opponent = max(
        opponents, key=lambda snake: snake['length'], default=None)
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
    my_path_tail = a_star.a_star_search((my_head['x'], my_head['y']), (
        my_tail['x'], my_tail['y']), game_state['board'], game_state['board']['snakes'], my_id)

    food = game_state['board']['food']

    if food:
        sorted_foods = sorted(food, key=lambda f: abs(
            f['x'] - my_head['x']) + abs(f['y'] - my_head['y']))

        for food_item in sorted_foods:

            my_path = a_star.a_star_search((my_head['x'], my_head['y']), (
                food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)
            if not my_path:
                continue

            closest_food = True

            for opponent in opponents:
                opponent_path = a_star.a_star_search((opponent["head"]["x"], opponent["head"]["y"]), (
                    food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)
                if not opponent_path:
                    continue
                if len(opponent_path) < len(my_path) or (len(opponent_path) == len(my_path) and my_size <= opponent["length"]):
                    closest_food = False
                    break

            if closest_food:
                if len(sorted_foods) == 1:
                    print("path")
                    next_move = my_path[0]
                    break

                for foods in sorted_foods:
                    food_path = a_star.a_star_search((foods['x'], foods['y']), (
                        food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)
                    if foods != food_item:
                        if not food_path and len(sorted_foods) > 1:
                            print("path not safe")
                            is_move_safe[my_path[0]] = False
                        else:
                            print("path")
                            next_move = my_path[0]
                            break
                else:
                    continue
                break

        else:
            if largest_opponent['length'] < my_size:

                for foods in sorted_foods:
                    food_path = a_star.a_star_search((foods['x'], foods['y']), (
                        food_item['x'], food_item['y']), game_state['board'], game_state['board']['snakes'], my_id)
                    food_tail_path = a_star.a_star_search((foods['x'], foods['y']), (
                        my_tail['x'], my_tail['y']), game_state['board'], game_state['board']['snakes'], my_id)
                    if foods != food_item:
                        if not food_path and len(sorted_foods) > 1 and not food_tail_path:
                            print("path not safe")
                            is_move_safe[my_path[0]] = False
                        else:
                            if my_path:
                                print("path size")
                                next_move = my_path[0]
                                break
                            else:
                                print("random")
                                next_move = random.choice(safe_moves)
                if my_path:
                    print("path size")
                    next_move = my_path[0]

            elif my_path_tail:
                print("tail")
                next_move = my_path_tail[0]

            else:
                print("random")
                next_move = random.choice(safe_moves)
    else:
        if len(safe_moves) == 0:
            print(
                f"MOVE {game_state['turn']}: No safe moves detected! Moving to tail")
            next_move = my_path_tail[0]
        if my_path_tail:
            print("tail")
            next_move = my_path_tail[0]
        else:

            print("random")
            next_move = random.choice(safe_moves)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


if __name__ == "__main__":
    from server import run_server

    run_server({
        "info": info,
        "my_head": my_head,
        "move": move,
        "end": end
    })
