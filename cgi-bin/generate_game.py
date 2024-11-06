#!/usr/bin/python
import mafia
import sys
import json
import os
import create_page
import datetime


def generate_game_a(game_id, player_list, mafia_count, sk_count,intro_link):
    game = {"players":mafia.generate_players(player_list,int(mafia_count),sk=int(sk_count)), "id":game_id, "intro":intro_link}
    if game_id not in os.listdir(mafia.get_game_file_location(None)):
        pass
        os.mkdir(mafia.get_game_file_location(None)+game_id)
    with open(mafia.get_game_file_location(game_id)+"init.txt","w") as out:
        out.write(json.dumps(game))
    with open(mafia.get_game_file_location(game_id)+"players.txt","w") as out:
        for p in player_list:
            out.write(p)

def generate_game(d):

    game_id = d["game_id"][0]

    player_list = [x.rstrip() for x in d["players"][0].split("\n") if x.rstrip()]
    mafia_count = d["mafia_count"][0]
    generate_game_a(game_id,player_list,mafia_count, d["sk_count"][0], d["intro_link"][0])
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