#!/usr/bin/python
import cgi
import mafia
import cgitb
import json
import datetime
cgitb.enable()

game_id = cgi.FieldStorage().getfirst("id")
try:
    commands = mafia.get_game_as_commands(game_id)
except FileNotFoundError:
    mafia.save_game(game_id, [{"time":str(datetime.datetime.now()), "command":{"action":"setup", "name":game_id}}])
(game, valid, messages) = mafia.load_game(game_id)
print("Content-type: text/plain\n")
print(mafia.json_to_commands(mafia.get_game(game_id))+"$"+"<br>\n".join(x for x in messages)+"<br>"+json.dumps(game) + "$" + str(len(mafia.get_game(game_id))) + "$" + str(",".join(p for p in game["players"])))