import os
import random
import typing
from flask import Flask, request

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