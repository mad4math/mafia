#!/usr/bin/python
import cgi
import mafia
import cgitb
import json
cgitb.enable()

print("Content-type: text/plain\n")
d = cgi.FieldStorage()
if len(mafia.get_game(d.getfirst("id"))) != int(d.getfirst("count")):
    print('$<p style="color:red">Error: game state has changed, please reload the game</p>{} != {}'.format(len(mafia.get_game(d.getfirst("id"))),int(d.getfirst("count"))))
else:
    (game, valid, messages) = mafia.save_game(d.getfirst("id").rstrip(),mafia.commands_to_json(d.getfirst("commands").split("\n")))
    print(mafia.json_to_commands(valid)+"$"+"<br>\n".join(x for x in messages)+"$" + str(len(valid)) + "$"
     + "$" + json.dumps(game))