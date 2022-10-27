#!/usr/bin/python
import cgi
import mafia
import cgitb
import create_page
cgitb.enable()

d = cgi.FieldStorage()
game_id = d.getfirst("id")
player = d.getfirst("player")
action = d.getfirst("action")
command = ""
if action=="vote":
    command = action+" "+d.getfirst("target")
if action=="investigate":
    command = action+" "+d.getfirst("x")+" "+d.getfirst("y")+" for "+d.getfirst("z")+(" as "+d.getfirst("w") if d.getfirst("w") else "")
if action=="predicts":
    command = action+" "+d.getfirst("prophecy")
if action=="roleblock":
    command = action+" "+d.getfirst("target")
if action=="priest":
    command = action+" sinners "+d.getfirst("sinners")+" saints "+d.getfirst("saints")
if action=="guess":
    command = action+" "+d.getfirst("target")
if action=="seer":
    command = action+" "+d.getfirst("target")
(game, valid, messages) = mafia.save_game(game_id, mafia.get_game(game_id)+([player+" "+command] if command else []))
print("Content-type: text/html\n")
print(create_page.player_info(game,player,messages))