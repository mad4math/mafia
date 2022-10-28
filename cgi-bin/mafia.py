import random
import json
import shlex
import traceback
import os
roles = ["investigator","prophet","priest","vigilante","gay knight","seer"] #all the roles
straight_roles = ["investigator","prophet","priest","vigilante","seer"] #all the roles that aren't gay

def load_gamestate(game_file):
    with open(game_file) as f:
        return json.load(f)

def setup(game):
    game["deaths"] = {}
    game["votes"] = []
    game["day"] = 0
    game["mafia"] = {"traps":2, "trapped":[], "untrappable":[]}
    for player in game["players"]:
        p = game["players"][player]
        output(player, "{} is a {}".format(player, p["role"]))
        output(player, "{} is <b>{}</b>".format(player, p["team"]))
        p["roleblocked"] = False
        p["alive"] = True
        p["vote"] = player
        if p["role"] == "prophet":
            p["tomorrow"] = ""
            p["today"] = ""
            p["investigations"] = {}
        elif p["role"] == "roleblocker":
            p["tomorrow"] = ""
            p["today"] = ""
            p["all_rollblocks"] = []
        elif p["role"] == "priest":
            p["tomorrow"] = {"sinners":[], "saints":[]}
            p["today"] = {"sinners":[], "saints":[]}
        elif p["role"] == "gay knight":
            p["dying"] = False
            p["guesses"] = 2
            p["correct"] = False
        elif p["role"] == "investigator":
            p["frames"] = 1
            p["investigations"] = 0
    output("mafia","{} are the mafia ".format(",".join(x for x in game["players"] if game["players"][x]["team"]=="mafia")))


def generate_players(players,mafia):
    """
    players is a list of player names
    m is a mafia count
    """
    s = (int)(random.random()*1e9)
    random.seed(s)
    print(s)
    last_gay = None
    result = {}
    while not result or last_gay:
        random.shuffle(players)
        result = {}
        last_gay = None
        m = mafia
        for p in players:
            result[p] ={}
            if m>0:
                result[p]["team"]="mafia"
                role = random.choice(roles+straight_roles)
            else:
                result[p]["team"]="town"
                role = random.choice(roles)
            if role == "gay knight":
                if last_gay==None:
                    last_gay = p
                else:
                    result[last_gay]["partner"]=p
                    result[p]["partner"]=last_gay
                    last_gay=None
            result[p]["role"]=role
            result[p]["intro"]=0
            m -= 1
    return result

"""
with open("players.txt") as file:
    players = [l.rstrip() for l in file.readlines()]
    game = generate_players(players,3)
    with open("game.txt","w") as out:
        out.write(json.dumps(game))
"""

def rollover(game):
    r = []
    g = game["players"]
    #count the votes, and limit the saints and sinner lists.
    votes = {}
    alive = [player for player in g if g[player]["alive"]]
    for player in alive:
        p = g[player]
        if p["role"] == "priest":
            p["tomorrow"]["saints"] = p["tomorrow"]["saints"][:int(len(alive)*.2+.99)]
            p["tomorrow"]["sinners"] = p["tomorrow"]["sinners"][:int(len(alive)*.2+.99)]
        vote = g[player]["vote"]
        if vote not in votes:
            votes[vote] = [player]
        else:
            votes[vote] += [player]
    game["votes"] += [votes]
    #determine who is executed, and publish the results
    if game["day"] > 0:
        d = game["day"]
        max_vote_players = [player for player in g if g[player]["alive"]] + ["no-execution"]
        while d > 0 and len(max_vote_players) > 1:
            max_vote_this_day = max_vote_players
            max_vote = 0
            for player in game["votes"][d]:
                if player not in max_vote_players:
                    continue
                if len(game["votes"][d][player]) > max_vote:
                    max_vote_this_day = [player]
                    max_vote = len(game["votes"][d][player])
                elif len(game["votes"][d][player]) == max_vote:
                    max_vote_this_day += [player]
            max_vote_players = [player for player in max_vote_players if player in max_vote_this_day]
            d -= 1
            output("test", max_vote_players)
        execution = sorted(max_vote_players)[0]
        if execution!="no-execution":
            g[execution]["alive"] = False
        output("public", "{} was executed".format(execution))
        for player in votes:
            output("public", "{} was voted for by {}".format(player, ", ".join(votes[player])))
        for player in alive:
            p["vote"] = player

    #submit roleblocks for roleblockers at day start, because their action is mandatory.
    #also set all trapped players to roleblocked
    #roleblocks are gone, so this section is commented out
    """
    for player in alive:
        p = g[player]
        if p["role"] == "roleblocker" and p["tomorrow"] not in alive:
            if p["roleblocked"]:
                p["tomorrow"] = ""
            else:
                x = ""
                y = [y for y in alive if y not in p["all_rollblocks"]]
                if y:
                    x = random.choice(y)
                r += [player+" roleblock "+submit_rollblock(game, player, x)]
        if player not in game["mafia"]["trapped"]:
            p["roleblocked"] = False
        else:
            p["roleblocked"] = True
    """
    alive = [player for player in g if g[player]["alive"]]
    #perform the upkeep for all living players
    for player in alive:
        p = g[player]
        if p["role"] == "investigator":
            p["investigations"] = 2
        elif p["role"] == "prophet":
            p["today"] = p["tomorrow"]
            output(player, "{} predicts on day {} that {}".format(player, game["day"]+1, p["today"]))
        elif p["role"] == "roleblocker":
            if p["tomorrow"]:
                g[p["tomorrow"]]["roleblocked"] = True
                output(player, "{} roleblocked {} for day {}".format(player, p["tomorrow"], game["day"]+1))
                p["all_rollblocks"] += [p["tomorrow"]]
            p["tomorrow"] = ""
        elif p["role"] == "priest":
            p["today"] = p["tomorrow"]
            if len(p["today"]["saints"])>0:
                output(player, "{} priest lists for day {} are sinners: {} saints: {}".format(player, game["day"]+1, p["today"]["sinners"],p["today"]["saints"]))
        elif p["role"] == "vigilante":
            pass
        elif p["role"] == "gay knight":
            if p["dying"]:
                p["alive"] = False
                output("public", "{} died of heartbreak".format(player))
            if not g[p["partner"]]["alive"]:
                p["dying"] = True
        elif p["role"] == "seer":
            p["uses"] = 1
    game["day"] += 1
    output("public","day {} begins!".format(game["day"]))
    for player in alive:
        p = g[player]
        if p["roleblocked"]:
            if p["role"] == "investigator":
                p["investigations"] = 0
            elif p["role"] == "priest":
                p["tomorrow"] = {"sinners":[], "saints":[]}
            elif p["role"] == "seer":
                p["uses"] = 0
            elif p["role"] == "prophet":
                p["tomorrow"] = ""
            output(player, "{} is roleblocked for day {}".format(player, game["day"]))
    return r + ["rollover"]

def kill(game, killer, victim, time, location):
    if game["players"][killer]["roleblocked"]:
        raise IllegalAction()
    game["deaths"][victim] = {"killer":killer,"location":location,"time":time,"investigations":[],"framed":[],"true_killer":killer}
    game["players"][victim]["alive"] = False
    for player in game["players"]:
        p = game["players"][player]
        if p["role"] == "priest" and player not in game["mafia"]["trapped"]:
            if killer in p["today"]["saints"] and victim in p["today"]["sinners"]:
                game["deaths"][victim]["killer"] = ""
                p["role"] = "none"
                output(player, "A saint killed {}! You lose your role powers for the rest of game, and the culprit will be innocent for all investigations.".format(victim))
            elif killer in p["today"]["sinners"] and victim in p["today"]["saints"]:
                output(player, "A sinner killed {}!".format(victim))
            elif victim in p["today"]["saints"]:
                output(player, "{} wasn't killed by any of {}".format(victim,p["today"]["sinners"]))
            elif victim in p["today"]["sinners"]:
                output(player, "{} wasn't killed by any of {}".format(victim,p["today"]["saints"]))

    output("public", "{} died in {} at {}".format(victim,location,time))
class IllegalAction(Exception):
    pass

def trap(game, player, target, role):
    if game["players"][player]["team"] != "mafia":
        raise IllegalAction("Only mafia can set traps!")
    if game["mafia"]["traps"] < 1:
        raise IllegalAction("Mafia are out of traps!")
    if player in game["mafia"]["untrappable"]:
        raise IllegalAction("Mafia can't trapped someone they've used Seer on!")
    if game["players"][target]["role"] == role:
        game["mafia"]["trapped"] += [target]
        output("mafia", "You successfully trapped {} as {}".format(target, role))
    else:
        game["mafia"]["traps"] -= 1
        output("mafia", "You failed to trap {} as {}".format(target, role))

def untrap(game, player, target):
    if game["players"][player]["team"] != "mafia":
        raise IllegalAction("Only mafia can set traps!")
    if not target in game["mafia"]["trapped"]:
        raise IllegalAction("You didn't trap that person in the first place!")
    game["mafia"]["trapped"] = [p for p in game["mafia"]["trapped"] if p!=target]
    output("mafia", "You released {} from their trap".format(target))


def grant_prophet_investigations(game, player, kill, correctTime, correctPlace, correctPerson):
    game["players"][player]["investigations"][kill] = 2*(correctPerson + correctPlace + correctTime)
    l = (["time"] if correctTime else []) + (["location"] if correctPlace else []) + (["person"] if correctPerson else [])
    if player in game["mafia"]["trapped"]:
        game["players"][player]["investigations"][kill] = 0
        l = []
    if l:
        output(player, "{} correctly identified the correct {} for the death of {}. You now have {} investigations you can use on this death".format(player, ", ".join(l), kill, game["players"][player]["investigations"][kill]))
    else:
        output(player, "{} didn't predict anything correctly about the death of {}".format(player,kill))

def submit_rollblock(game, player, target):

    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't submit a roleblock because you are roleblocked!")
    elif game["players"][player]["role"]!="roleblocker":
        raise IllegalAction("Can't roleblock: you are not a roleblocker!")
    elif target in game["players"][player]["all_rollblocks"]:
        raise IllegalAction("Can't roleblock the same person twice!")
    else:
        game["players"][player]["tomorrow"]=target
        output(player, "{} submitted a roleblock of {} for day {}".format(player, target, game["day"]+1))
        return target

def submit_priest_list(game, player, sinners, saints):
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't submit a priest list because you are roleblocked")
    elif game["players"][player]["role"]!="priest":
        raise IllegalAction("Can't submit a priest list because you aren't a priest!")
    else:
        game["players"][player]["tomorrow"]={"sinners":sinners, "saints":saints}
        output(player, "{} submitted preist lists of sinners: {} and saints: {} for day {}".format(player, sinners, saints, game["day"]+1))

def frame(game, player, kill, target):
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't frame because you are roleblocked")
    if game["players"][player]["role"]!="investigator":
        raise IllegalAction("Can't frame because you aren't an investigator!")
    if kill not in game["deaths"]:
        raise IllegalAction("Can't frame someone for a death that didn't happen!")
    if game["players"][player]["frames"] < 1:
        raise IllegalAction("You already used you frame!")
    game["deaths"][kill]["framed"]+=[target]
    output(player, "{} framed {} for the death of {}".format(player, target, kill))

def submit_prophecy(game, player, prophecy):
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't submit a prophecy because you are roleblocked!")
    if game["players"][player]["role"]!="prophet":
        raise IllegalAction("Can't submit a prophecy because you are not a prophet!")
    else:
        game["players"][player]["tomorrow"]=prophecy
        output(player, "{} predicts on day {} that {}".format(player, game["day"]+1,prophecy))

def submit_vote(game, player, vote):
    game["players"][player]["vote"] = vote
    output(player, "{} voted for {}".format(player, vote))

def see(game, player, target):
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't seer because you are roleblocked!")
    if game["players"][player]["role"]!="seer":
        raise IllegalAction("Can't seer because you are not a seer!")
    if game["players"][player]["uses"]<1:
        raise IllegalAction("You already used your seer ability today!")
    else:
        game["players"][player]["uses"] -= 1
        game["mafia"]["untrappable"] += [player]
        result = random.choice(roles) if player in game["mafia"]["trapped"] else game["players"][target]["role"]
        output(player, "{} is a {}".format(target, result))
def infallible_investigate(game, player, guess):
    kill = game["players"][player]["partner"]
    if game["players"][player]["role"]!="gay knight" or game["players"][kill]["alive"] or game["players"][player]["guesses"]<1:
        raise IllegalAction()
    elif game["players"][player]["partner"]!=kill:
        raise IllegalAction()
    else:
        game["players"][player]["guesses"] -= 1
        if game["deaths"][kill]["true_killer"] == guess:
            output(player, "{} killed your partner! You may kill them with bang!".format(guess))
            game["players"][player]["correct"] = True
        else:
            output(player, "{} did not kill your partner.".format(guess))

def investigate(game,player, x, y, z, w=None):
    """
    player p investigates (x,y) for kill z, with desired result w
    an investigation is stored as the 3 element list [x,y,result]
    """
    p = game["players"][player]
    if p["roleblocked"]:
        raise IllegalAction("Can't investigate because you are roleblocked!")
    if z not in game["deaths"]:
        raise IllegalAction("Can't investigate someone who never died!")
    if p["role"] == "investigator":
        if p["investigations"]==0:
            raise IllegalAction("You are out of investigations!")
        else:
            r = do_investigation(game, player, x, y, z, w)
            p["investigations"] -= 1
            return r
    elif p["role"] == "prophet":
        if z not in p["investigations"] or p["investigations"][z]==0:
            raise IllegalAction("You don't have any investigations left for this kill!")
        else:
            r = do_investigation(game, player, x, y, z, w)
            p["investigations"][z] -= 1
            return r
    else:
        raise IllegalAction("Can't investigate because you aren't an investigator or a prophet!")
def do_investigation(game, player, x, y, z, w):
    """doesn't check for legality, subroutine of investigate"""
    if player in game["mafia"]["trapped"]:
        w = random.choice([x,y])
        output(player, "investigation of ({},{}) for {}'s death returns that {} is innocent".format(x,y,z,w))
        return (x,y,z,w)
    legal = []
    if game["deaths"][z]["killer"] == x:
        legal = [y]
    elif game["deaths"][z]["killer"] == y:
        legal = [x]
    elif x in game["deaths"][z]["framed"]:
        if y in game["deaths"][z]["framed"]:
            legal = [x,y]
        else:
            legal = [y]
    elif y in game["deaths"][z]["framed"]:
        legal = [x]
    else:
        legal = [x,y]
    if w:
        if w not in legal:
            raise IllegalAction("That result could never occur!")
    else:
        for i in game["deaths"][z]["investigations"]:
            if (i[0] == x and i[1] == y) or (i[1] == x and i[0] == y):
                w = i[2]
                break
        if not w:
            w = random.choice(legal)
    output(player, "investigation of ({},{}) for {}'s death returns that {} is innocent".format(x,y,z,w))
    game["deaths"][z]["investigations"] += [[x,y,w]]
    return (x, y, z, w)

messages = []
def output(audience, message):
    m = "{}: {}".format(audience, message)
    global messages
    messages += [m]
    #print(m)

def get_game_file_location(game_id):
    with open("config.ini") as file:
        return file.read().rstrip()+game_id+"/"

def get_game(game_id):
    with open(get_game_file_location(game_id)+"game_actions.txt") as file:
        return [l.rstrip() for l in file.readlines()]


def load_game(game_id):
    return do_commands(get_game(game_id))


def save_game(game_id, actions):
    (game, valid, messages) = do_commands(actions)
    with open(get_game_file_location(game_id)+"game_actions.txt","w") as file:
        for line in valid:
            file.write(line+"\n")
    return (game, valid, messages)

def check_valid_player(game,player):
    if player not in game["players"]:
        raise IllegalAction("{} isn't a player".format(player))

def do_commands(commands):
    """
    commands is a list of commands formatted like read_command wants
    """
    global messages
    messages = []
    game = None
    valid = []
    for c in commands:
        try:
            (game, c) = do_command(game, c)
            valid += c.split("\n")
        except IllegalAction as e:
            output("error", str(e))
        except Exception as e:
            traceback.print_exc()
    return (game, valid, reversed(messages))

def do_command(game, command):
    """
    language of commands
    setup [file]
        file has a json of roles/alignments. The first command should always be this one
    rollover
        does a day rollover
    [player] investigate [x] [y] for [z] [as w]
        player does an investigation of x and y for kill z [intending to return w]
    [player] priest sinners [[  separated list of sinnners]] saints [[  separated list of sinnners]]
        submit a priest list
    [player] predicts "[x]"
        submit a prophecy as a prophet
    [player] roleblock [x]
        submit a roleblock
    [player] seer [x]
        submit a seer query
    [player] kill [x] at [time] in [place]
        log a kill.
    [player] predicted location|time|person of [x]
        allocate investigations to prophets.
    [player] guess [x]
        submit a gay knight infallible investigation
    [player] vote [x]
        submit a vote for player x
    [player] frame [x] for [y]
        frame a player x for the death of y
    [player] trap [x] as [y]
        player is a mafia, using a trap on player x as role y
    [player] untrap [x]
        player is a mafia, untrap x.
    [player] drop
        remove player from the game
    """
    l = shlex.split(command)
    if l[0]=="setup":
        with open(get_game_file_location(l[1])+"init.txt") as file:
            game = json.loads(file.readlines()[0])
            setup(game)
            return (game, command)
    elif l[0] == "seed":
        random.seed(l[1])
        return (game, command)
    elif l[0] == "rollover":
        commands = "\n".join(rollover(game))
        return (game, commands)
    else:
        player = l[0]
        check_valid_player(game, player)
        if l[1] == "investigate":
            if len(l)==6:
                x = l[2]
                y = l[3]
                z = l[5]
                check_valid_player(game, x)
                check_valid_player(game, y)
                check_valid_player(game, z)
                (x,y,z,w) = investigate(game, player, x, y, z)
                command = command + " as " + w
            elif len(l)==8:
                x = l[2]
                y = l[3]
                z = l[5]
                w = l[7]
                check_valid_player(game, x)
                check_valid_player(game, y)
                check_valid_player(game, z)
                check_valid_player(game, w)
                investigate(game, player, x, y, z, w=w)
            else:
                raise IllegalAction("bad syntax: "+command)
        elif l[1] == "priest":
            i = 2
            sinners = []
            saints = []
            mode = 0 #0 for sinners, 1 for saints
            while i < len(l):
                if l[i] == "sinners":
                    mode = 1
                elif l[i] == "saints":
                    mode = 0
                else:
                    check_valid_player(game, l[i])
                    if mode:
                        sinners += [l[i]]
                    else:
                        saints += [l[i]]
                i += 1
            submit_priest_list(game, player, sinners, saints)
        elif l[1] == "predicts":
            submit_prophecy(game, player, l[2])
        elif l[1] == "roleblock":
            check_valid_player(game, l[2])
            submit_rollblock(game, player, l[2])
        elif l[1] == "seer":
            check_valid_player(game, l[2])
            see(game, player, l[2])
        elif l[1] == "kill":
            if len(l) < 7 or l[3]!="at" or l[5]!="in":
                raise IllegalAction("bad syntax: "+command)
            check_valid_player(game, l[2])
            if game["players"][l[2]]["alive"]:
                kill(game, player, l[2], l[4], l[6])
            else:
                raise IllegalAction("can't kill a dead player!")
        elif l[1] == "predicted":
            i=2
            correctTime = False
            correctPlace = False
            correctPerson = False
            while l[i] in ["location","time","person"]:
                if l[i]=="location":
                    correctPlace = True
                elif l[i]=="time":
                    correctTime = True
                elif l[i]=="person":
                    correctPerson = True
                i+=1
            check_valid_player(game, l[i+1])
            grant_prophet_investigations(game, player, l[i+1], correctTime, correctPlace, correctPerson)
        elif l[1] == "guess":
            check_valid_player(game, l[2])
            infallible_investigate(game, player, l[2])
        elif l[1] == "vote":
            if l[2]!="no-execution":
                check_valid_player(game, l[2])
            submit_vote(game, player, l[2])
        elif l[1] == "frame":
            check_valid_player(game, l[2])
            check_valid_player(game, l[4])
            frame(game, player, l[4], l[2])
        elif l[1] == "trap":
            check_valid_player(game, l[2])
            if l[4] not in roles:
                raise IllegalAction("Not a valid role!")
            trap(game, player, l[2], l[4])
        elif l[1] == "untrap":
            check_valid_player(game, l[2])
            untrap(game, player, l[2])
        elif l[1] == "intro":
            game["players"][l[0]]["intro"]=1
        elif l[1] == "drop":
            game["players"][l[0]]["alive"]=0
        return (game, command)

if __name__=="__main__":
    with open("game_actions.txt") as file:
        (game, valid, messages) = do_commands([l.rstrip() for l in file.readlines()])
        with open("game_actions_valid.txt","w") as file:
            for line in valid:
                file.write(line+"\n")
