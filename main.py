import os
import random
import typing
from flask import Flask, request

app = Flask(__name__)

@app.get("/")
def on_info():
    return info()

@app.post("/start")
def on_start():
    game_state = request.get_json()
    my_head(game_state)
    return "ok"

@app.post("/move")
def on_move():
    game_state = request.get_json()
    return move(game_state)

@app.post("/end")
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
    my_size = game_state["you"]["length"]
    my_id = game_state["you"]["id"]
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    my_body = game_state['you']['body']
    opponents = [snake for snake in game_state['board']['snakes'] if snake['id'] != my_id]
    largest_opponent = max(opponents, key=lambda snake: snake['length'], default=None)
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

    safe_moves = [move for move, isSafe in is_move_safe.items() if isSafe]

    next_move = random.choice(safe_moves) if safe_moves else "up"
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
