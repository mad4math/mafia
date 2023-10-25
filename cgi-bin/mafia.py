import random
import json
import shlex
import traceback
import os
import time

USE_BUDDY = False

roles = ["investigator","prophet","priest","vigilante","seer","gay knight"] #all the roles
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
        game["players"][player]["alive"] = True
    for player in game["players"]:
        p = game["players"][player]
        if p["team"] == "sk":
            p["traps"] = 0
            p["trapped"] = []
            p["untrappable"] = []
            p["cooldown"] = 1
        output(player, "{} is a {}".format(player, p["role"]))
        output(player, "{} is <b>{}</b>".format(player, p["team"]))
        p["roleblocked"] = False
        p["vote"] = player
        if p["role"] == "prophet":
            #p["tomorrow"] = ""
            #p["today"] = ""
            p["investigations"] = {}
            p["resolved"] = {}
            p["prophecies"] = [""]
        elif p["role"] == "roleblocker":
            p["tomorrow"] = ""
            p["today"] = ""
            p["all_rollblocks"] = []
        elif p["role"] == "priest":
            p["tomorrow"] = {"sinners":[], "saints":[]}
            p["today"] = {"sinners":[], "saints":[]}
            p["active"] = True
        elif p["role"] == "gay knight":
            p["dying"] = False
            p["guesses"] = 2
            p["correct"] = False
        elif p["role"] == "investigator":
            p["frames"] = 1
            p["investigations"] = 0
        elif p["role"] == "vigilante" and get_alive_buddy(game, player) != player:
            p["investigations"] = 1
    output("mafia","{} are the mafia ".format(",".join(x for x in game["players"] if game["players"][x]["team"]=="mafia")))


def generate_players(players,mafia,sk=0):
    """
    players is a list of player names
    m is a mafia count
    """
    s = (int)(random.random()*1e9)
    random.seed(s)
    #print(s)
    last_gay = None
    result = {}
    while not result or (last_gay and not USE_BUDDY):
        random.shuffle(players)
        result = {}
        last_gay = None
        m = mafia
        for p in players:
            result[p] ={}
            result[p]["buddy"]=""
            if m>0:
                result[p]["team"]="mafia"
                role = random.choice(roles+straight_roles)
                m -= 1
            elif sk>0:
                result[p]["team"]="sk"
                role = random.choice(roles+straight_roles)
                sk -= 1
            else:
                result[p]["team"]="town"
                if USE_BUDDY:
                    if last_gay:
                        result[p]["buddy"] = last_gay
                        result[last_gay]["buddy"] = p
                        role = result[last_gay]["role"]
                        if role == "priest":
                            result[p]["mode"] = "sinners"
                            result[last_gay]["mode"] = "saints"
                        last_gay = None
                    else:
                        last_gay = p
                        role = random.choice(roles)
                else:
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
            output("public", "{} was voted for by {}  ".format(player, ", ".join(votes[player])))
        for player in alive:
            p = g[player]
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
        if p["team"] == "sk":
            if p["cooldown"] > 0:
                p["cooldown"] -= 1
        if p["role"] == "investigator":
            p["investigations"] = 2
        elif p["role"] == "vigilante":
            if get_alive_buddy(game, player)!=player:
                p["investigations"] = 1
            else:
                p["investigations"] = 0
        elif p["role"] == "prophet":
            #p["today"] = p["tomorrow"]
            p["prophecies"] += [p["prophecies"][-1]]
            output(player, "{} predicts on day {} that {}".format(player, game["day"]+1, p["prophecies"][game["day"]]))
        elif p["role"] == "roleblocker":
            if p["tomorrow"]:
                g[p["tomorrow"]]["roleblocked"] = True
                output(player, "{} roleblocked {} for day {}".format(player, p["tomorrow"], game["day"]+1))
                p["all_rollblocks"] += [p["tomorrow"]]
            p["tomorrow"] = ""
        elif p["role"] == "priest":
            p["today"] = p["tomorrow"]
            p["tomorrow"] = {"sinners":[x for x in p["today"]["sinners"]], "saints":[x for x in p["today"]["saints"]]}
            if len(p["today"]["saints"])>0 and p["active"]:
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
    # handle rollblocked players
    # commented out because rollblockers don't exist anymore
    """
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
    """
    return r + ["rollover"]

def get_alive_buddy(game, player):
    if game["players"][player]["buddy"] and game["players"][game["players"][player]["buddy"]]["alive"]:
        return game["players"][player]["buddy"]
    else:
        return player

def kill(game, killer, victim, time, location):
    if game["players"][killer]["roleblocked"]:
        raise IllegalAction()
    game["deaths"][victim] = {"killer":killer,"location":location,"time":time,"investigations":[],"framed":[],"true_killer":killer, "day":game["day"]}
    game["players"][victim]["alive"] = False
    if game["players"][killer]["team"] == "sk":
        game["players"][killer]["cooldown"] = 3
    #handle priests
    for player in game["players"]:
        p = game["players"][player]
        if p["role"] == "priest" and p["active"] and p["alive"]:
            buddy = get_alive_buddy(game, player)
            b = game["players"][buddy]
            sinners = p["today"]["sinners"]+b["today"]["sinners"]
            saints = p["today"]["saints"]+b["today"]["saints"]
            if killer in saints and victim in sinners and (USE_BUDDY or player not in game["mafia"]["trapped"]):
                game["deaths"][victim]["killer"] = ""
                #p["role"] = "none"
                p["active"] = False
                b["active"] = False
                output_player_buddy(game, player, "A saint killed {}! You lose your role powers for the rest of game, and the culprit will be innocent for all investigations.".format(victim))
            elif killer in sinners and victim in saints and (USE_BUDDY or player not in game["mafia"]["trapped"]):
                output_player_buddy(game, player, "A sinner killed {}!".format(victim))
            elif victim in saints:
                output_player_buddy(game, player, "{} wasn't killed by any of {}".format(victim,p["today"]["sinners"]))
            elif victim in sinners:
                output_player_buddy(game, player, "{} wasn't killed by any of {}".format(victim,p["today"]["saints"]))

    output("public", "{} died in {} at {}".format(victim,location,time))
class IllegalAction(Exception):
    pass
def output_player_buddy(game, player, s):
    output(player, s)
    if player != get_alive_buddy(game, player):
        output(get_alive_buddy(game,player), s)

def trap_buddy(game, player, target, guess):
    if game["players"][player]["team"] != "mafia":
        raise IllegalAction("Only mafia can set traps!")
    if game["mafia"]["traps"] < 1:
        raise IllegalAction("Mafia are out of traps!")
    if target in game["mafia"]["untrappable"]:
        raise IllegalAction("Mafia can't trap someone they've already trapped the buddy of!")
    if game["players"][target]["buddy"] == guess:
        game["mafia"]["trapped"] += [target]
        output("mafia", "You successfully trapped {} as the buddy of {}. You may kill one of them for free.".format(target, guess))
    else:
        game["mafia"]["traps"] -= 1
        output("mafia", "You failed to trap {} as {}".format(target, guess))

def trap_role(game, player, target, guess):
    if game["players"][player]["team"] == "town":
        raise IllegalAction("Only mafia can set traps!")
    if game["players"][player]["team"] == "mafia":
        trap_source = game["mafia"]
        trap_source_name = "mafia"
    else:
        trap_source = game["players"][player]
        trap_source_name = player
    if trap_source["traps"] < 1:
        raise IllegalAction("You are out of traps!")
    if target in trap_source["untrappable"]:
        raise IllegalAction("Mafia can't trap someone they've Seen!")
    if game["players"][target]["role"] == guess:
        trap_source["trapped"] += [target]
        output(trap_source_name, "You successfully trapped {} as {}. Their role now will silently fail.".format(target, guess))
    else:
        trap_source["traps"] -= 1
        output(trap_source_name, "You failed to trap {} as {}".format(target, guess))


def untrap(game, player, target):
    if game["players"][player]["team"] == "town":
        raise IllegalAction("Only mafia can unset traps!")
    if game["players"][player]["team"] == "mafia":
        trap_source = game["mafia"]
        trap_source_name = "mafia"
    else:
        trap_source = game["players"][player]
        trap_source_name = player
    if not target in trap_source["trapped"]:
        raise IllegalAction("You didn't trap that person in the first place!")
    trap_source["trapped"] = [p for p in game["mafia"]["trapped"] if p!=target]
    output(trap_source_name, "You released {} from their trap".format(target))


def grant_prophet_investigations(game, player, kill, correctTime, correctPlace, correctPerson):
    buddy = get_alive_buddy(game, player)
    game["players"][buddy]["investigations"][kill] = 2*(correctPerson + correctPlace + correctTime)
    l = (["time"] if correctTime else []) + (["location"] if correctPlace else []) + (["person"] if correctPerson else [])
    game["players"][player]["resolved"][kill] = 1
    if player in game["mafia"]["trapped"]:
        game["players"][player]["investigations"][kill] = 0
        l = []
    if l:
        output(buddy, "{} correctly identified the correct {} for the death of {}. You now have {} investigations you can use on this death".format(player, ", ".join(l), kill, game["players"][player]["investigations"][kill]))
    else:
        output(buddy, "{} didn't predict anything correctly about the death of {}".format(player,kill))

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
    buddy = get_alive_buddy(game, player)
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't submit a priest list because you are roleblocked")
    elif game["players"][player]["role"]!="priest":
        raise IllegalAction("Can't submit a priest list because you aren't a priest!")
    else:
        if sinners:
            game["players"][player]["tomorrow"]["sinners"]=sinners
            output_player_buddy(game, player, "{} submitted lists of sinners: {} for day {}".format(player,sinners, game["day"]+1))
        if saints:
            game["players"][player]["tomorrow"]["saints"]=saints
            output_player_buddy(game, player, "{} submitted lists of saint: {} for day {}".format(player,saints, game["day"]+1))

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
    buddy = get_alive_buddy(game,player)
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't submit a prophecy because you are roleblocked!")
    if game["players"][player]["role"]!="prophet":
        raise IllegalAction("Can't submit a prophecy because you are not a prophet!")
    else:
        game["players"][player]["prophecies"][game["day"]]=prophecy
        output_player_buddy(game, player, "{} predicts on day {} that {}".format(player, game["day"]+1,prophecy))

def submit_vote(game, player, vote):
    game["players"][player]["vote"] = vote
    output(player, "{} voted for {}".format(player, vote))

def see(game, player, target, result=None):
    buddy = get_alive_buddy(game,player)
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't seer because you are roleblocked!")
    if game["players"][player]["role"]!="seer":
        raise IllegalAction("Can't seer because you are not a seer!")
    if game["players"][player]["uses"]<1:
        raise IllegalAction("You already used your seer ability today!")
    else:
        game["players"][player]["uses"] -= 1
        if game["players"][player]["team"] == "mafia" and not USE_BUDDY:
            game["mafia"]["untrappable"] += [target]
        possible_results = roles if player in game["mafia"]["trapped"] else [game["players"][target]["role"]]
        #possible_results = [game["players"][target]["role"]]
        if result==None:
            result = random.choice(roles) if player in game["mafia"]["trapped"] else game["players"][target]["role"]
        if result not in possible_results:
            raise IllegalAction("{} is not a possible result for {} to see as the role of {}".format(result, player, target))
        else:
            output(buddy, "{} is a {}".format(target, result))
            return result

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
    elif p["role"] == "vigilante":
        if p["investigations"]==0:
            raise IllegalAction("You are out of investigations!")
        else:
            r = do_investigation(game, player, x, y, z, w)
            p["investigations"] -= 1
            game["players"][get_alive_buddy(game,player)]["investigations"] -= 1
            return r
    else:
        raise IllegalAction("Can't investigate because you aren't an investigator or a prophet!")
def do_investigation(game, player, x, y, z, w):
    """doesn't check for legality, subroutine of investigate"""
    buddy = get_alive_buddy(game,player)
    
    if player in game["mafia"]["trapped"] and not USE_BUDDY:
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
    output(buddy, "investigation of ({},{}) for {}'s death returns that {} is innocent".format(x,y,z,w))
    game["deaths"][z]["investigations"] += [[x,y,w]]
    return (x, y, z, w)

messages = []
def output(audience, message):
    m = "{}: {}".format(audience, message)
    global messages
    #messages += [{"a":audience, "m":message}]
    messages += [m]
    #print(m)

def get_game_file_location(game_id):
    with open("config.ini") as file:
        if game_id:
            return file.read().rstrip()+game_id+"/"
        else:
            return file.read().rstrip()

def get_game(game_id):
    with open(get_game_file_location(game_id)+"game_actions.txt") as file:
        return json.loads(file.read())

def get_game_as_commands(game_id):
    l = get_game(game_id)
    return [x["time"]+" "+json_to_command(x["command"]) for x in l]

def commands_to_json(commands):
    return [{"time":x[:x.find(" ",x.find(" ")+1)],"command":command_to_json(x[x.find(" ",x.find(" ")+1)+1:])} for x in commands if x.rstrip()!=""]


def load_game(game_id):
    g = get_game(game_id)
    now = datetime.datetime.now()
    past = [x for x in g if x["time"] <= str(now)]
    future = [x for x in g if x["time"] > str(now)]
    (g, v, m) = do_commands(past)
    with open(get_game_file_location(game_id)+"game_actions.txt","w") as file:
        file.write(json.dumps(v + future))
    return (g, v + future, m)


def json_to_commands(commands):
    return "\n".join(x["time"]+" "+json_to_command(x["command"]) for x in commands)


def save_game(game_id, actions):
    now = datetime.datetime.now()
    past = [x for x in actions if x["time"] <= str(now)]
    future = [x for x in actions if x["time"] > str(now)]
    (game, valid, messages) = do_commands(past)
    with open(get_game_file_location(game_id)+"game_actions.txt","w") as file:
        file.write(json.dumps(valid + future))
        #for line in valid:
        #    file.write(line+"\n")
    return (game, valid + future, messages)

def check_valid_player(game,player):
    if player not in game["players"]:
        raise IllegalAction("{} isn't a player".format(player))

import datetime
def run_commands_and_save(game_id, commands):
    g = get_game(game_id)
    now = datetime.datetime.now()
    past = [x for x in g if x["time"] <= str(now)]
    future = [x for x in g if x["time"] > str(now)]
    return save_game(game_id, past + [{"time":str(datetime.datetime.now()), "command":command} for command in commands] + future)

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
            (game, c1) = do_command(game, c["command"])
            c["command"] = c1
            valid += [c]
        except IllegalAction as e:
            output("error", str(e))
        except Exception as e:
            traceback.print_exc()
    return (game, valid, reversed(messages))


    """
    language of commands
    setup [file]
        file has a json of roles/alignments. The first command should always be this one
    rollover
        does a day rollover
    edit
        manually edit the json, each argument is another level into the json
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

def command_to_json(command):
    l = shlex.split(command)
    if l[0]=="setup":
        return {"action":"setup","name":l[1]}
    elif l[0] == "seed":
        return {"action":l[0],"seed":l[1]}
    elif l[0] == "rollover":
        return {"action":l[0]}
    elif l[0] == "edit":
        return {"action":l[0], "path":l[1:-1], "code":l[-1]}
    else:
        player = l[0]
        if l[1] == "investigate":
            d = {"action":l[1],"player":l[0],"suspect1":l[2],"suspect2":l[3],"kill":l[5]}
            if len(l)==6:
                return d
            else:
                d["result"]=l[7]
                return d
        elif l[1] == "priest":
            if l[2] == "sinners":
                return {"action":l[1],"player":l[0],"mode":"sinners","list":l[3:]}
            elif l[2] == "saints":
                return {"action":l[1],"player":l[0],"mode":"saints","list":l[3:]}
            else:
                raise IllegalAction("Invalid priest list syntax")
        elif l[1] == "predicts":
            return {"action":l[1],"player":l[0],"prophecy":l[2]}
        elif l[1] == "roleblock":
            return {"action":l[1],"player":l[0],"target":l[2]}
        elif l[1] == "seer":
            if len(l)<4:
                return {"action":l[1],"player":l[0],"target":l[2]}
            else:
                return {"action":l[1],"player":l[0],"target":l[2],"result":l[4]}
        elif l[1] == "kill":
            if len(l) < 7 or l[3]!="at" or l[5]!="in":
                raise IllegalAction("bad syntax: "+command)
            return {"action":l[1],"player":l[0],"target":l[2],"time":l[4],"location":l[6]}
        elif l[1] == "predicted":
            return {"action":l[1],"player":l[0],"correctTime":"time" in l[2:-2],"correctPlace":"location" in l[2:-2],"correctPerson":"person" in l[2:-2],"kill":l[-1]}
        elif l[1] == "guess":
            return {"action":l[1],"player":l[0],"target":l[2]}
        elif l[1] == "vote":
            return {"action":l[1],"player":l[0],"target":l[2]}
        elif l[1] == "frame":
            return {"action":l[1],"player":l[0],"target":l[2], "kill":l[4]}
        elif l[1] == "trap":
            return {"action":l[1],"player":l[0],"target":l[2], "guess":l[4]}
        elif l[1] == "untrap":
            return {"action":l[1],"player":l[0],"target":l[2]}
        elif l[1] == "intro":
            return {"action":l[1],"player":l[0]}
        elif l[1] == "drop":
            return {"action":l[1],"player":l[0]}
        raise IllegalAction("bad syntax command not recognized:"+command)


def json_to_command(json_obj):
    action = json_obj['action']
    if action == 'setup':
        return 'setup ' + json_obj['name']
    elif action == 'seed':
        return 'seed ' + json_obj['seed']
    elif action == 'rollover':
        return 'rollover'
    elif action == 'edit':
        return 'edit ' + ' '.join(json_obj['path']) + ' ' + json_obj['code']
    else:
        player = json_obj['player']
        if action == 'investigate':
            command = player + ' investigate ' + json_obj['suspect1'] + ' ' + json_obj['suspect2'] + ' '
            command += 'kill ' + json_obj['kill']
            if 'result' in json_obj:
                command += ' result ' + json_obj['result'] + ' '
            return command
        elif action == 'priest':
            mode = json_obj['mode']
            if mode == 'sinners':
                return player + ' priest sinners ' + ' '.join(json_obj['list'])
            elif mode == 'saints':
                return player + ' priest saints ' + ' '.join(json_obj['list'])
            else:
                raise ValueError('Invalid priest list syntax')
        elif action == 'predicts':
            return player + ' predicts "' + json_obj['prophecy'] + '"'
        elif action == 'roleblock':
            return player + ' roleblock ' + json_obj['target']
        elif action == 'seer':
            command = player + ' seer ' + json_obj['target']
            if 'result' in json_obj:
                command += ' result ' + json_obj['result'] + ' '
            return command
        elif action == 'kill':
            return player + ' kill ' + json_obj['target'] + ' at ' + json_obj['time'] + ' in "' + json_obj['location'] + '"'
        elif action == 'predicted':
            command = player + ' predicted '
            if json_obj['correctTime']:
                command += 'time '
            if json_obj['correctPlace']:
                command += 'location '
            if json_obj['correctPerson']:
                command += 'person '
            command += 'of ' + json_obj['kill']
            return command
        elif action == 'guess':
            return player + ' guess ' + json_obj['target']
        elif action == 'vote':
            return player + ' vote ' + json_obj['target']
        elif action == 'frame':
            return player + ' frame ' + json_obj['target'] + ' kill ' + json_obj['kill']
        elif action == 'trap':
            return player + ' trap ' + json_obj['target'] + ' guess ' + (json_obj['guess'] if json_obj['guess'] else "")
        elif action == 'untrap':
            return player + ' untrap ' + json_obj['target']
        elif action == 'intro':
            return player + ' intro'
        elif action == 'drop':
            return player + ' drop'
        else:
            raise ValueError('Invalid action type: ' + action)



def do_command(game, command):
    """
    takes a dict of the command, and performs the game action
    """
    action = command["action"]
    if action=="setup":
        with open(get_game_file_location(command["name"])+"init.txt") as file:
            game = json.loads(file.readlines()[0])
            setup(game)
    elif action == "seed":
        random.seed(command["seed"])
    elif action == "rollover":
        rollover(game)
    elif action == "edit":
        g = game
        for i in range(len(command["path"])-1):
            g = g[command["path"][i]]
        g[command["path"][-1]] = command["code"]
        output("admin","game"+''.join("[\""+x+"\"]" for x in command["path"][:-1])+"=\"{}\"".format(command["code"]))
    else:
        player = command["player"]
        check_valid_player(game, player)
        if action == "investigate":
            x = command["suspect1"]
            y = command["suspect2"]
            z = command["kill"]
            check_valid_player(game, x)
            check_valid_player(game, y)
            check_valid_player(game, z)
            if "result" not in command:
                (x,y,z,w) = investigate(game, player, x, y, z)
                command["result"] = w
            else:
                w = command["result"]
                check_valid_player(game, w)
                investigate(game, player, x, y, z, w=w)
        elif action == "priest":
            if command["mode"] == "sinners":
                submit_priest_list(game, player, command["list"], [])
            elif command["mode"] == "saints":
                submit_priest_list(game, player, [], command["list"])
            else:
                raise IllegalAction
        elif action == "predicts":
            submit_prophecy(game, player, command["prophecy"])
        elif action == "roleblock":
            check_valid_player(game, command["target"])
            submit_rollblock(game, player, command["target"])
        elif action == "seer":
            check_valid_player(game, command["target"])
            if "result" in command:
                see(game, player, command["target"], result=command["result"])
            else:
                result = see(game, player, command["target"])
                command["result"] = result
        elif action == "kill":
            check_valid_player(game, command["target"])
            if game["players"][command["target"]]["alive"]:
                kill(game, player, command["target"], command["time"], command["location"])
            else:
                raise IllegalAction("can't kill a dead player!")
        elif action == "predicted":
            check_valid_player(game, command["kill"])
            grant_prophet_investigations(game, player, command["kill"], command["correctTime"], command["correctPlace"], command["correctPerson"])
        elif action == "guess":
            check_valid_player(game, command["target"])
            infallible_investigate(game, player, command["target"])
        elif action == "vote":
            if command["target"]!="no-execution":
                check_valid_player(game, command["target"])
            submit_vote(game, player, command["target"])
        elif action == "frame":
            check_valid_player(game, command["target"])
            check_valid_player(game, command["kill"])
            frame(game, player, command["kill"], command["target"])
        elif action == "trap":
            check_valid_player(game, command["target"])
            if USE_BUDDY and command["guess"] not in game["players"] and command["guess"]:
                raise IllegalAction("Not a valid possible buddy!")
            elif not USE_BUDDY and command["guess"] not in roles:
                raise IllegalAction("Not a valid possible role!")
            if USE_BUDDY:
                trap_buddy(game, player, command["target"], command["guess"])
            else:
                trap_role(game, player, command["target"], command["guess"])
        elif action == "untrap":
            check_valid_player(game, command["target"])
            untrap(game, player, command["target"])
        elif action == "intro":
            game["players"][player]["intro"]=1
        elif action == "drop":
            game["players"][player]["alive"]=0
    return (game, command)

if __name__=="__main__":
    with open("game_actions.txt") as file:
        (game, valid, messages) = do_commands([l.rstrip() for l in file.readlines()])
        with open("game_actions_valid.txt","w") as file:
            for line in valid:
                file.write(line+"\n")
