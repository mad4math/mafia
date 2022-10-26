#!/usr/bin/python
import cgi
import mafia
import cgitb
import json
cgitb.enable()

game_id = cgi.FieldStorage().getfirst("id")
commands = mafia.get_game(game_id)
(game, valid, messages) = mafia.load_game(game_id)
print("Content-type: text/plain\n")
print("\n".join(valid)+"$"+"<br>\n".join(x for x in messages)+"<br>"+json.dumps(game) + "$" + str(len(commands)))