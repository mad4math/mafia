#!/usr/bin/python
import cgi
import mafia
import cgitb
import json
import os
cgitb.enable()

print("Content-type: text/plain\n")
games = os.listdir(mafia.get_game_file_location(None)[:-1])

def get_game_time(game):
	return mafia.get_game(game)[0]["time"]

games.sort(key = get_game_time, reverse=True)
print("/".join(games))