#!/usr/bin/python
import cgi
import mafia
import cgitb
import create_page
import datetime
cgitb.enable()

d = cgi.FieldStorage()
game_id = d.getfirst("id")
player = d.getfirst("player")
action = d.getfirst("action")
command = {"action":action, "player":player}
if action=="vote":
    command["target"]=d.getfirst("target")
if action=="investigate":
    command["suspect1"] = d.getfirst("x")
    command["suspect2"] = d.getfirst("y")
    command["kill"] = d.getfirst("z")
    if d.getfirst("w"):
        command["result"] = d.getfirst("w")
if action=="predicts":
    command["prophecy"] = d.getfirst("prophecy")
if action=="roleblock":
    command["target"]=d.getfirst("target")
if action=="priest":
    if d.getfirst("sinners"):
        command["mode"] = "sinners"
        command["list"] = d.getfirst("sinners").split(" ")
    elif d.getfirst("saints"):
        command["mode"] = "saints"
        command["list"] = d.getfirst("saints").split(" ")
if action=="guess":
    command["target"]=d.getfirst("target")
if action=="seer":
    command["target"]=d.getfirst("target")
if action=="trap":
    command["target"]=d.getfirst("target")
    command["guess"]=d.getfirst("guess")
(game, valid, messages) = mafia.run_commands_and_save(game_id,[command])
print("Content-type: text/html\n")
print(create_page.player_info(game,player,messages))