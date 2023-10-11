import mafia
import sys
import json
import cgi
import cgitb
import os
import create_page
import datetime
cgitb.enable()


def generate_game(game_id, player_list, mafia_count):
    game = {"players":mafia.generate_players(player_list,int(mafia_count)), "id":game_id}
    if game_id not in os.listdir(mafia.get_game_file_location(None)):
        os.mkdir(mafia.get_game_file_location(None)+game_id)
    with open(mafia.get_game_file_location(game_id)+"init.txt","w") as out:
        out.write(json.dumps(game))
    with open(mafia.get_game_file_location(game_id)+"players.txt","w") as out:
        for p in player_list:
            out.write(p)



d = cgi.FieldStorage()
game_id = d.getfirst("game_id")

player_list = [x.rstrip() for x in d.getfirst("players").split("\n") if x.rstrip()]
mafia_count = d.getfirst("mafia_count")
generate_game(game_id,player_list,mafia_count)
(game, valid, messages) = mafia.save_game(game_id, [{"time":str(datetime.datetime.now()), "command":{"action":"setup", "name":game_id}}])

print("Content-type: text/html\n")
print("""<meta http-equiv="Refresh" content="0; url='../admin.html'" />""")




"""
if __name__=="__main__":
    with open(mafia.get_game_file_location(sys.argv[1])+"players.txt") as file:
        players = [l.rstrip() for l in file.readlines()]
        generate_game(sys.argv[1], players, sys.argv[2])
        game = {"players":mafia.generate_players(players,int(sys.argv[2]))}
        with open(mafia.get_game_file_location(sys.argv[1])+"init.txt","w") as out:
            out.write(json.dumps(game))
"""