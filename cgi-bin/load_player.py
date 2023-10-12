#!/usr/bin/python
import cgi
import mafia
import cgitb
import create_page
cgitb.enable()


d = cgi.FieldStorage()
game_id = d.getfirst("id").rstrip()
player = d.getfirst("player")
(game, valid, messages) = mafia.load_game(game_id)
if player not in game["players"]:
	print("Content-type: text/html\n{} is not a player in this game.".format(player))
else: 
	h = create_page.main_page(game, player, messages)
	print("Content-type: text/html\n")
	print(h)