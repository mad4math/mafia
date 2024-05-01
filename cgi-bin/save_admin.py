#!/usr/bin/python
import mafia
import json

def save_admin(d):
    if len(mafia.get_game(d["id"].rstrip())) != int(d["count"]):
        return ('`<p style="color:red">Error: game state has changed, please reload the game</p>{} != {}'.format(len(mafia.get_game(d["id"])),int(d["count"])))
    else:
        (game, valid, messages) = mafia.save_game(d["id"].rstrip(),mafia.commands_to_json(d["commands"].split("\n")))
        return (mafia.json_to_commands(valid)+"`"+"<br>\n".join(x for x in messages)+"`" + str(len(valid)) + "`"
         + "`" + json.dumps(game))

def update_admin_single_command(d):
        game_id = d["id"]
        command = d["command"]
        (game, valid, messages) = mafia.run_commands_and_save(game_id,[command])
        return (mafia.json_to_commands(valid)+"`"+"<br>\n".join(x for x in messages)+"`" + str(len(valid)) + "`"
         + "`" + json.dumps(game))
