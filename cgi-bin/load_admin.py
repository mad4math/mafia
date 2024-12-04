#!/usr/bin/python
import mafia
import json
import datetime

def load_admin(d):
    game_id = d["id"][0]
    try:
        commands = mafia.get_game_as_commands(game_id)
    except FileNotFoundError:
        mafia.save_game(game_id, [{"time":str(datetime.datetime.now()), "command":{"action":"setup", "name":game_id}}])
    (game, valid, messages) = mafia.load_game(game_id)
    init = ""
    with open(mafia.get_game_file_location(game_id)+"init.txt") as file:
        init = file.readlines()[0]
    return (mafia.json_to_commands(valid)+"`"+"<br>\n".join(x for x in messages)+"`" + str(len(valid)) + "`"
         + "`" + json.dumps(game)) +"`" + init

#print(mafia.json_to_commands(mafia.get_game(game_id))+"$"+"<br>\n".join(x for x in messages)+"<br>"+json.dumps(game) + "$" + str(len(mafia.get_game(game_id))) + "$" + str(",".join(p for p in game["players"])) + "$")