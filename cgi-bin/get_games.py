#!/usr/bin/python
import mafia
import json
import os
def get_games():
	games = os.listdir(mafia.get_game_file_location(None)[:-1])

	def get_game_time(game):
		try:
			return mafia.get_game(game)[0]["time"]
		except:
			return game

	games.sort(key = get_game_time, reverse=True)
	return json.dumps(games)
