#!/usr/bin/python
import mafia
import create_page

def load_player(d):
	game_id = d["id"][0].rstrip()
	player = d["player"][0]
	(game, valid, messages) = mafia.load_game(game_id)
	if player not in game["players"]:
		return"n{} is not a player in this game.".format(player)
	else: 
		h = create_page.main_page(game, player, messages)
		return h