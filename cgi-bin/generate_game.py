import mafia
import sys
if name=="__main__":
    with open(mafia.get_game_file_location(sys.argv[1])+"players.txt") as file:
        players = [l.rstrip() for l in file.readlines()]
        game = generate_players(players,3)
        with open(mafia.get_game_file_location(sys.argv[1])+"init.txt","w") as out:
            out.write(json.dumps(game))