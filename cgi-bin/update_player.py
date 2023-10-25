#!/usr/bin/python
import mafia
import create_page
import datetime

def update_player(d):

    game_id = d["id"][0]
    player = d["player"][0]
    action = d["action"][0]
    command = {"action":action, "player":player}
    if action=="vote":
        command["target"]=d["target"][0]
    if action=="investigate":
        command["suspect1"] = d["x"][0]
        command["suspect2"] = d["y"][0]
        command["kill"] = d["z"][0]
        if d["w"][0]:
            command["result"] = d["w"][0]
    if action=="predicts":
        command["prophecy"] = d["prophecy"][0]
    if action=="roleblock":
        command["target"]=d["target"][0]
    if action=="priest":
        if d["sinners"][0]:
            command["mode"] = "sinners"
            command["list"] = d["sinners"][0].split(" ")
        elif d["saints"][0]:
            command["mode"] = "saints"
            command["list"] = d["saints"][0].split(" ")
    if action=="guess":
        command["target"]=d["target"][0]
    if action=="seer":
        command["target"]=d["target"][0]
    if action=="trap":
        command["target"]=d["target"][0]
        command["guess"]=d["guess"][0]
    (game, valid, messages) = mafia.run_commands_and_save(game_id,[command])
    return create_page.player_info(game,player,messages)