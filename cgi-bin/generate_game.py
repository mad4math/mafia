import mafia
import sys
import json
if __name__=="__main__":
    with open(mafia.get_game_file_location(sys.argv[1])+"players.txt") as file:
        players = [l.rstrip() for l in file.readlines()]
        game = {"players":mafia.generate_players(players,int(sys.argv[2]))}
        with open(mafia.get_game_file_location(sys.argv[1])+"init.txt","w") as out:
            out.write(json.dumps(game))