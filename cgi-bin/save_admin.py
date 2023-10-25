#!/usr/bin/python
import mafia
import json

def save_admin(d):
    if len(mafia.get_game(d["id"][0].rstrip())) != int(d["count"][0]):
        return ('$<p style="color:red">Error: game state has changed, please reload the game</p>{} != {}'.format(len(mafia.get_game(d["id"][0])),int(d["count"][0])))
    else:
        (game, valid, messages) = mafia.save_game(d["id"][0].rstrip(),mafia.commands_to_json(d["commands"][0].split("\n")))
        return (mafia.json_to_commands(valid)+"$"+"<br>\n".join(x for x in messages)+"$" + str(len(valid)) + "$"
         + "$" + json.dumps(game))