#!/usr/bin/python
import mafia
import create_page
import datetime

"""the request has the following structure:
{ id : id,
command : command }
"""



def update_player(d):
        game_id = d["id"]
        command = d["command"]
        player = d["command"]["player"]
        """
        game_id = d["id"][0]
        player = d["player"][0]
        action = d["action"][0]
        command = {"action":action, "player":player}
        if action=="vote":
            command["target"]=d["target"][0]
        if action=="vote-no-execution":
            command["yes"]=1 if d["yes"][0]=="true" else 0
        if action=="investigate":
            command["suspect1"] = d["x"][0]
            command["suspect2"] = d["y"][0]
            command["kill"] = d["z"][0] if "z" in d else ""
            if "w" in d:
                command["result"] = d["w"][0]
        if action=="predicts":
            command["prophecy"] = d["prophecy"][0]
        if action=="roleblock":
            command["target"]=d["target"][0]
        if action=="priest":
            if "sinners" in d:
                command["mode"] = "sinners"
                command["list"] = d["sinners"][0].split(" ")
            elif "saints" in d:
                command["mode"] = "saints"
                command["list"] = d["saints"][0].split(" ")
        if action=="guess":
            command["target"]=d["target"][0]
        if action=="seer":
            command["target"]=d["target"][0]
        if action=="frame":
            command["target"]=d["target"][0]
            command["kill"]=d["kill"][0]
        if action=="trap":
            command["target"]=d["target"][0]
            command["guess"]=d["guess"][0]
        if action=="untrap":
            command["target"]=d["target"][0]
            """
        (game, valid, messages) = mafia.run_commands_and_save(game_id,[command])
        return create_page.player_info(game,player,messages)