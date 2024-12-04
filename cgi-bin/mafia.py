import random
import json
import shlex
import traceback
import os
import time

USE_BUDDY = False
MANIP_WILDCARD = "$EVERYONE"

#no gay knight
roles = ["investigator","prophet","priest","vigilante","seer", "censusmaster", "fortune teller"] #all the roles
common_roles = ["investigator","prophet","priest","vigilante","seer", "fortune teller"]
straight_roles = ["investigator","prophet","priest","vigilante","seer"] #all the roles that aren't gay

def load_gamestate(game_file):
    with open(game_file) as f:
        return json.load(f)

def setup(game):
    game["deaths"] = {}
    game["votes"] = []
    game["day"] = 0
    game["mafia"] = {"traps":3, "trapped":{}, "untrappable":[], "omens":{}}
    for player in game["players"]:
        game["players"][player]["alive"] = True
        game["players"][player]["jailed"] = False
        game["players"][player]["vote_no_execution"] = False
    for player in game["players"]:
        p = game["players"][player]
        if p["team"] == "sk":
            p["traps"] = 1
            p["trapped"] = []
            p["untrappable"] = []
            p["cooldown"] = 1
        output(player, "{} is a {}".format(player, p["role"]))
        output(player, "{} is <b>{}</b>".format(player, p["team"]))
        p["roleblocked"] = False
        p["vote"] = player
        p["jailbreak_votes"] = []
        p["framed"] = []
        p["additional_powers"] = []
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
            p["kills_investigated"] = {}
        elif p["role"] == "gravedigger":
            p["roleChecks"] = 0
            p["alignmentChecks"] = 1
            p["plants"] = 1
            p["gravedig_guesses"] = {}
        elif p["role"] == "censusmaster":
            p["roleCounts"] = 0
            p["mafiaCounts"] = 0
        elif p["role"] == "fortune teller":
            p["uses"] = 0
            p["killsChecked"] = []
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
    serial_killers = sk
    result = {}
    while not result or (last_gay and not USE_BUDDY):
        random.shuffle(players)
        result = {}
        last_gay = None
        m = mafia
        sk = serial_killers
        for p in players:
            result[p] ={}
            result[p]["buddy"]=""
            if m>0:
                result[p]["team"]="mafia"
                role = random.choice(roles+common_roles)
                m -= 1
            elif sk>0:
                result[p]["team"]="sk"
                role = random.choice(roles+common_roles)
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
                        role = random.choice(roles+common_roles)
                else:
                    role = random.choice(roles+common_roles)
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
def can_vote_no_execution(game):
    return game["day"] <= 1 or not any(game["deaths"][x]["day"] == game["day"] for x in game["deaths"])

def rollover(game):
    r = []
    g = game["players"]
    #count the votes, and limit the saints and sinner lists.
    votes = {}
    alive = sorted([player for player in g if g[player]["alive"]])
    unjailed = sorted([player for player in g if g[player]["alive"] and not g[player]["jailed"]])
    for player in alive:
        p = g[player]
        if p["role"] == "priest":
            #p["tomorrow"]["saints"] = p["tomorrow"]["saints"][:int(len(alive)*.2+.99)]
            #p["tomorrow"]["sinners"] = p["tomorrow"]["sinners"][:int(len(alive)*.2+.99)]
            max_priest_size = int(len(alive)*.4)
            p["tomorrow"]["sinners"] = p["tomorrow"]["sinners"][:max_priest_size]
            max_priest_size -= len(p["tomorrow"]["saints"])
            p["tomorrow"]["saints"] = p["tomorrow"]["saints"][:max_priest_size]

        if not p["jailed"]:
            vote = g[player]["vote"] if not (can_vote_no_execution(game) and g[player]["vote_no_execution"]) else "no-execution"
            if vote not in votes:
                votes[vote] = [player]
            else:
                votes[vote] += [player]
    game["votes"] += [votes]
    #determine who is executed, and publish the results
    if game["day"] > 0:
        d = game["day"]
        #list of players which are winning the current vote, sorted in tiebreak order
        max_vote_players = [player for player in game["tiebreak"] if g[player]["alive"] and not g[player]["jailed"]] + ["no-execution"]
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
        execution = max_vote_players[0]
        if execution!="no-execution":
            g[execution]["jailed"] = True
        output("public", "{} was jailed".format(execution))
        for player in alive+["no-execution"]:
            if player in votes:
                output("public", "{} was voted for by {}  ".format(player, ", ".join(votes[player])))

        #determine who is released from jail
        unjail_threshold = int((len(unjailed))/2+1)
        jailed = sorted([player for player in g if g[player]["alive"] and g[player]["jailed"]])
        for player in jailed:
            unjail_votes = []
            for player2 in unjailed:
                if player in g[player2]["jailbreak_votes"]:
                    unjail_votes.append(player2)
            if len(unjail_votes) >= unjail_threshold:
                g[player]["jailed"] = False
                output("public", "{} was released from jail with {} out of {} needed votes".format(player,len(unjail_votes),unjail_threshold))
            output("public", "votes to release {player}:{votes}".format(player=player, votes=unjail_votes))
        #resent votes to self votes for the next day
        for player in alive:
            p = g[player]
            p["vote"] = player
            p["jailbreak_votes"] = []

        output("public", "living unjailed players:<b>"+", ".join(player for player in alive if not g[player]["jailed"])+"</b>")
        output("public", "living jailed players:<b>"+", ".join(player for player in alive if g[player]["jailed"])+"</b>")

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
        for i in range(len(p["additional_powers"])):
            if p["additional_powers"][i] == "ritual_investigation":
                del p["additional_powers"][i]
        if p["role"] == "investigator":
            p["investigations"] = 1
        elif p["role"] == "gravedigger":
            p["roleChecks"] = 1
        elif p["role"] == "censusmaster":
            p["roleCounts"] = 1
        elif p["role"] == "fortune teller":
            p["uses"] = 1
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
def trapped_manipulations(game, player):
    for x in game["players"]:
        if game["players"][x]["team"]=="sk" and player in game["players"][x]["trapped"]:
            return game["players"][x]["trapped"][player]
    if player in game["mafia"]["trapped"]:
        return game["mafia"]["trapped"][player]
    return None

def trapped(game, player):
    return any(player in game["players"][x]["trapped"] for x in game["players"] if game["players"][x]["team"]=="sk") or player in game["mafia"]["trapped"]

def check_sk_mafia_promotion(game):
    living_sk = [player for player in game["players"] if game["players"][player]["team"] == "sk" and game["players"][player]["alive"]]
    if not any(game["players"][player]["team"] == "mafia" and game["players"][player]["alive"] for player in game["players"]):
        new_mafia = random.choice(living_sk)

def promote_to_mafia(game, player):
    if game["players"][player]["team"] == "sk":
        game["mafia"]["trapped"] += game["players"][player]["trapped"]
        game["mafia"]["untrappable"] += game["players"][player]["untrappable"]
        #game["mafia"]["traps"] += game["players"][player]["traps"]
    game["players"][player]["team"] = "mafia"

def kill(game, killer, victim, time, location):
    if game["players"][killer]["roleblocked"]:
        raise IllegalAction()
    game["deaths"][victim] = {"killer":killer,"location":location,"time":time,"investigations":[],"true_killer":killer, "day":game["day"], "omen":[]}
    game["players"][victim]["alive"] = False
    if victim in game["mafia"]["omens"]:
        game["deaths"][victim]["omen"] = [game["mafia"]["omens"][victim]]
    if game["players"][killer]["team"] == "sk":
        game["players"][killer]["cooldown"] = 3
    #handle priests
    for player in game["players"]:
        p = game["players"][player]
        if trapped(game, player) and p["role"] == "prophet":
            pass
            #grant_prophet_investigations(game, player, victim, False, False, False)
        if p["role"] == "priest" and p["active"] and p["alive"]:
            buddy = get_alive_buddy(game, player)
            b = game["players"][buddy]
            sinners = p["today"]["sinners"]+b["today"]["sinners"]
            saints = p["today"]["saints"]+b["today"]["saints"]
            if killer in saints and victim in sinners and (USE_BUDDY or not trapped(game, player)):
                game["deaths"][victim]["killer"] = ""
                #p["role"] = "none"
                p["active"] = False
                b["active"] = False
                output_player_buddy(game, player, "A saint killed {}! You lose your role powers for the rest of game, and the culprit will be innocent for all investigations.".format(victim))
            elif killer in sinners and victim in saints and (USE_BUDDY or not trapped(game, player)):
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
    if target in game["mafia"]["untrappable"]:
        raise IllegalAction("Mafia can't trap someone they've Seen!")
    if game["players"][target]["role"] == guess:
        trap_source["trapped"][target] = {"manipulations":[]}
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
    #trap_source["trapped"] = [p for p in trap_source["trapped"] if p!=target]
    del trap_source["trapped"][target]
    output(trap_source_name, "You released {} from their trap".format(target))


def submit_vote(game, player, vote):
    game["players"][player]["vote"] = vote
    output(player, "{} voted for {}".format(player, vote))

def submit_vote_no_execution(game, player, yes):
    game["players"][player]["vote_no_execution"] = yes
    if yes:
        output(player, "voting for no-execution if legal")
    else:
        output(player, "voting to execute even if no-execution is legal")

def submit_vote_jailbreak(game, player, vote, yes):
    if yes and vote not in game["players"][player]["jailbreak_votes"]:
        game["players"][player]["jailbreak_votes"].append(vote)
    elif not yes and vote in game["players"][player]["jailbreak_votes"]:
        game["players"][player]["jailbreak_votes"].remove(vote)

def grant_prophet_investigations(game, player, kill, correctTime, correctPlace, correctPerson):
    buddy = get_alive_buddy(game, player)
    game["players"][buddy]["investigations"][kill] = 1*(correctPerson + correctPlace + correctTime)
    l = (["time"] if correctTime else []) + (["location"] if correctPlace else []) + (["person"] if correctPerson else [])
    game["players"][player]["resolved"][kill] = 1
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
    if game["players"][player]["frames"] < 1:
        raise IllegalAction("You already used you frame!")
    game["players"][kill]["framed"]+=[target]
    game["players"][player]["frames"] -= 1
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
        if game["players"][player]["team"] == "sk":
            game["mafia"]["untrappable"] += [target]
        possible_results = [game["players"][target]["role"]]
        if trapped(game, player):
            mm = trapped_manipulations(game,player)["manipulations"]
            for x in mm:
                if x["target"] == target:
                    possible_results = [x["result"]]
        #possible_results = roles if trapped(game, player) else [game["players"][target]["role"]]
        if result==None:
            result = random.choice(possible_results)
        #if result not in possible_results:
        #    raise IllegalAction("{} is not a possible result for {} to see as the role of {}".format(result, player, target))
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

def ritual_investigate(game,player, x, y, z, w=None):
    if z not in game["deaths"]:
        raise IllegalAction("Can't investigate someone who never died!")
    if "ritual_investigation" not in game["players"][player]["additional_powers"]:
        raise IllegalAction("You don't have a ritual investigation available!")
    r = do_investigation(game, player, x, y, z, w, trappable=False)
    for i in range(len(game["players"][player]["additional_powers"])):
        if game["players"][player]["additional_powers"][i] == "ritual_investigation":
            del game["players"][player]["additional_powers"][i]
            break
    return r

def grant_ritual_investigation(game,player):
    game["players"][player]["additional_powers"] += ["ritual_investigation"]

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
        elif z in p["kills_investigated"] and p["kills_investigated"][z] >= 1:
            raise IllegalAction("Can't investigate the same kill more than once!")
        else:
            r = do_investigation(game, player, x, y, z, w)
            p["investigations"] -= 1
            if z not in p["kills_investigated"]:
                p["kills_investigated"][z] = 1
            else:
                p["kills_investigated"][z] += 1
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
def do_investigation(game, player, x, y, z, w, trappable=True):
    """doesn't check for legality, subroutine of investigate
    returns (x,y,z,w) = (suspect1, suspect2, death, result)"""
    buddy = get_alive_buddy(game,player)
    
    if trappable and trapped(game,player) and not USE_BUDDY:
        if w==None:
            mm = trapped_manipulations(game,player)["manipulations"]
            for m in reversed(mm):
                if m["kill"] == z or m["kill"] == MANIP_WILDCARD:
                    x1 = m["suspect1"]
                    y1 = m["suspect2"]
                    if ((x1 == x or x1 == MANIP_WILDCARD) and (y1 == y or y1 == MANIP_WILDCARD)) or ((x1 == y or x1 == MANIP_WILDCARD) and (y1 == x or y1 == MANIP_WILDCARD)):
                        if x == m["result"] or (m["result"] == MANIP_WILDCARD and x not in [x1,y1]):
                            w = x
                        else:
                            w = y
                        break

        #w = random.choice([x,y]) if w==None else w
        if w != None:
            output(player, "investigation of ({},{}) for {}'s death returns that {} is innocent".format(x,y,z,w))
            return (x,y,z,w)

    guiltiness = lambda x: 1 if (game["deaths"][z]["killer"] == x or x in game["players"][z]["framed"]) else 0
    xGuilt = guiltiness(x)
    yGuilt = guiltiness(y)
    legal = []
    if xGuilt > yGuilt:
        legal = [y]
    elif yGuilt > xGuilt:
        legal = [x]
    else:
        legal = [x,y]
    for i in game["deaths"][z]["investigations"]:
        if (i[0] == x and i[1] == y) or (i[1] == x and i[0] == y):
            legal = [i[2]]
            break
    if w and w not in [x,y]:
        raise IllegalAction("That's not a possible result! {} isn't one of the suspects!".format(w))
    if w and w not in legal:
        output(buddy, "Investigation of {},{} for {} can't produce the result {}".format(x,y,z,w))
        #submitting an illegal seeding as mafia costs you your investigation, but does not do anything other than tell you it was invalid.
    else:
        if not w:
            w = random.choice(legal)
        output(buddy, "investigation of ({},{}) for {}'s death returns that {} is innocent".format(x,y,z,w))
        game["deaths"][z]["investigations"] += [[x,y,w]]
    return (x, y, z, w)

def set_trap_info(game, player, target, info):
    if game["players"][player]["team"] == "town":
        raise IllegalAction("Only mafia can set traps!")
    if game["players"][player]["team"] == "mafia":
        trap_source = game["mafia"]
        trap_source_name = "mafia"
    else:
        trap_source = game["players"][player]
        trap_source_name = player
    if not target in trap_source["trapped"]:
        raise IllegalAction("Can't maniuplate a player you haven't trapped yet!")
    m = trap_source["trapped"][target]["manipulations"]
    if game["players"][target]["role"] == "seer":
        trap_source["trapped"][target]["manipulations"] = [x for x in trap_source["trapped"][target]["manipulations"] if x["target"]!=info["target"]]
    elif game["players"][target]["role"] == "gravedigger":
        trap_source["trapped"][target]["manipulations"] = [x for x in trap_source["trapped"][target]["manipulations"] if x["target"]!=info["target"]]
    elif game["players"][target]["role"] == "censusmaster":
        trap_source["trapped"][target]["manipulations"] = [x for x in trap_source["trapped"][target]["manipulations"] if x["x"]!=info["x"]]
    elif game["players"][target]["role"] == "censusmaster":
        trap_source["trapped"][target]["manipulations"] = [x for x in trap_source["trapped"][target]["manipulations"] if (x["x"]!=info["x"] or x["y"]!=info["y"])]
    trap_source["trapped"][target]["manipulations"] += [info]

def remove_trap_info(game, player, target, i):
    if game["players"][player]["team"] == "town":
        raise IllegalAction("Only mafia can set traps!")
    if game["players"][player]["team"] == "mafia":
        trap_source = game["mafia"]
        trap_source_name = "mafia"
    else:
        trap_source = game["players"][player]
        trap_source_name = player
    if not target in trap_source["trapped"]:
        raise IllegalAction("Can't maniuplate a player you haven't trapped yet!")
    del trap_source["trapped"][target]["manipulations"][i]

def set_gravedig(game, player, target, role, alignment):
    if game["players"][player]["plants"] < 1:
        raise IllegalAction("Can't plant evidence again!")
    check_valid_player(game, target)
    game["players"][player]["plants"] -= 1
    game["players"][target]["setGrave"] = {"role": role, "alignment": alignment}
    output(player, "planted evidence of role {role} and alignment {alignment} on player {target}".format(role=role, alignment=alignment, target=target))

def gravedig(game, player, target, t):
    if game["players"][player]["role"] != "gravedigger":
        raise IllegalAction("Only gravediggers can gravedig!")
    if game["players"][target]["alive"]:
        raise IllegalAction("Can't gravedig a living player!")
    if t not in ["role", "alignment"]:
        raise IllegalAction("Illegal type of gravedig")
    if game["players"][player]["roleChecks"] < 1:
        raise IllegalAction("Can't gravedig again today!")
    if t == "alignment" and game["players"][player]["alignmentChecks"]<1:
        raise IllegalAction("Can't check alignment again!")
    check_valid_player(game, target)
    game["players"][player]["roleChecks"] -= 1
    if t == "alignment":
        game["players"][player]["alignmentChecks"] -= 1
    result = None
    if trapped(game, player):
        mm = trapped_manipulations(game,player)["manipulations"]
        for x in mm:
            if x["target"] == target:
                if t == "role":
                    result = x["roleResult"]
                else:
                    result = x["alignmentResult"]
    if not result:
        if "setGrave" in game["players"][target]:
            result = game["players"][target]["setGrave"][t]
        else:
            result = game["players"][target]["role"] if t == "role" else game["players"][target]["team"]
    output(get_alive_buddy(game, player), "grave dig of {target} reveals they were a {result}".format(target=target, result=result))
    return result

def gravedig_role_guess(game, player, target, role):
    if game["players"][player]["role"] != "gravedigger":
        raise IllegalAction("Only gravediggers can gravedig!")
    if target in game["players"][player]["gravedig_guesses"]:
        raise IllegalAction("Can't guess again for that kill!")
    if (game["players"][player]["team"] == "sk" and target in game["players"][player]["untrappable"]) or target in game["mafia"]["untrappable"]:
        raise IllegalAction("Can't trap players you've already Seen!")
    correct = role == game["players"][target]["role"] 
    game["players"][player]["gravedig_guesses"][target] = {"role" : role, "frames_left": (1 if correct else 0)}
    if correct:
        output(player, "{target} was a {role}. You may now frame someone for their death".format(target=target, role=role))
    else:
        output(player, "{target} was not a {role}.".format(target=target, role=role))

def gravedig_frame(game, player, kill, target):
    if game["players"][player]["roleblocked"]:
        raise IllegalAction("Can't frame because you are roleblocked")
    if game["players"][player]["role"]!="gravedigger":
        raise IllegalAction("Can't frame because you aren't an gravedigger!")
    if kill not in game["players"][player]["gravedig_guesses"] or game["players"][player]["gravedig_guesses"][kill]["frames_left"] < 1:
        raise IllegalAction("You already used you frame!")
    game["players"][kill]["framed"]+=[target]
    game["players"][player]["gravedig_guesses"][kill]["frames_left"] -= 1
    output(player, "{} framed {} for the death of {}".format(player, target, kill))


def census(game, player, target):
    result = None
    if game["players"][player]["role"] != "censusmaster":
        raise IllegalAction("Only censusmasters can count!")
    if game["players"][player]["roleCounts"] < 1:
        raise IllegalAction("Can't count again today!")
    if target == "mafia" and game["players"][player]["mafiaCounts"] < 1:
        raise IllegalAction("Can't count the mafia again!")
    game["players"][player]["roleCounts"] -= 1
    if target == "mafia":
        game["players"][player]["mafiaCounts"] -= 1
    if trapped(game, player):
        mm = trapped_manipulations(game,player)["manipulations"]
        for x in mm:
            if x["x"] == target:
                result = x["result"]
    if result == None:
        if target == "mafia":
            result = sum(1 for x in game["players"] if game["players"][x]["alive"] and game["players"][x]["team"]=="mafia")
        else:
            result = sum(1 for x in game["players"] if game["players"][x]["alive"] and game["players"][x]["role"]==target)
    output(get_alive_buddy(game, player), "There are <b>{x}</b> {target} left in the game".format(target=target, x=result))
    return result

def fortune_tell(game, player, target, kill):
    result = None
    if game["players"][player]["role"] != "fortune teller":
        raise IllegalAction("Only fortune tellers can tell fortunes!")
    if game["players"][player]["uses"] < 1:
        raise IllegalAction("Can't tell any more fortunes today!")
    if kill not in game["deaths"]:
        raise IllegalAction("Invalid kill to fortune tell about")
    game["players"][player]["uses"] -= 1
    check_valid_player(game, target)
    if trapped(game, player):
        mm = trapped_manipulations(game,player)["manipulations"]
        for x in mm:
            if x["x"] == target and x["y"] == kill:
                result = x["result"]
    if result == None:
        if game["players"][target]["role"] == "fortune teller":
            result = "Good"
        elif target == game["deaths"][kill]["killer"]:
            result = "Bad"
        elif target in game["deaths"][kill]["omen"] or target in game["players"][kill]["framed"]:
            result = "Bad"
        else:
            result = "Good"
    output(get_alive_buddy(game, player), "You feel {result} omens about {target} for the death of {kill}".format(target=target, result=result, kill=kill))

def add_mafia_omen(game, player, target, kill):
    check_valid_player(game, target)
    check_valid_player(game, kill)
    if not game["players"][kill]["alive"]:
        raise IllegalAction("Can't set omens of players that have already died!")
    game["mafia"]["omens"][kill] = target

def remomve_mafia_omen(game, player, kill):
    check_valid_player(game, kill)
    if not game["players"][kill]["alive"]:
        raise IllegalAction("Can't set omens of players that have already died!")
    del game["mafia"]["omens"][kill]




"""
def set_trap_investigation(game, player, target, x, y, z, w):
    if game["players"][player]["team"] == "town":
        raise IllegalAction("Only mafia can set traps!")
    if game["players"][player]["team"] == "mafia":
        trap_source = game["mafia"]
        trap_source_name = "mafia"
    else:
        trap_source = game["players"][player]
        trap_source_name = player
    if not target in trap_source["trapped"]:
        raise IllegalAction("Can't maniuplate a player you haven't trapped yet!")
    m = trap_source["trapped"][target]["manipulations"]
    trap_source["trapped"][target]["manipulations"] = [mm for mm in m if not (((mm["x"]==x and mm["y"]==y) or (mm["x"]==y and mm["y"]==x)) and mm["z"]==z)] + ([{"x":x, "y":y, "z":z, "w":w}] if w != "$Default" else [])
    output(trap_source_name, "set {{{x},{y}}} returns {w} is innocent for kill {z}".format(x=x,y=y,z=z,w=w))
"""
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
    elif l[0] == "introlink":
        return {"action":"introlink", "link":l[1]}
    else:
        player = l[0]
        if l[1] == "investigate" or l[1] == "ritual_investigate":
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
        elif l[1] == "vote-no-execution":
            return {"action":l[1],"player":l[0],"yes":int(l[2])}
        elif l[1] == "vote-jailbreak":
            return {"action":l[1], "player":l[0],"target":l[2],"yes":int(l[3])}
        elif l[1] == "frame":
            return {"action":l[1],"player":l[0],"target":l[2], "kill":l[4]}
        elif l[1] == "trap":
            return {"action":l[1],"player":l[0],"target":l[2], "guess":l[4]}
        elif l[1] == "untrap":
            return {"action":l[1],"player":l[0],"target":l[2]}
        elif l[1] == "trap-manipulate-investigator":
            return {"action":l[1],"player":l[0],"target":l[2],"suspect1":l[3],"suspect2":l[4],"kill":l[6],"result":l[8]}
        elif l[1] == "trap-manipulate":
            return {"action":l[1],"player":l[0],"target":l[2],"info":json.loads(l[3])}
        elif l[1] == "trap-manipulate-remove-index":
            return {"action":l[1],"player":l[0],"target":l[2],"index":int(l[3])}
        elif l[1] == "intro":
            return {"action":l[1],"player":l[0]}
        elif l[1] == "drop":
            return {"action":l[1],"player":l[0]}
        elif l[1] == "conscript":
            return {"action":l[1],"player":l[0]}
        elif l[1] == "gravedig":
            return {"action":l[1],"player":l[0], "target":l[2], "type":l[3]}
        elif l[1] == "grave_plant":
            return {"action":l[1],"player":l[0], "target":l[2], "role":l[3], "alignment":l[4]}
        elif l[1] == "census":
            return {"action":l[1],"player":l[0], "target":l[2]}
        elif l[1] == "fortune_tell":
            return {"action":l[1],"player":l[0], "target":l[2], "kill":l[3]}
        elif l[1] == "set_omen":
            return {"action":l[1],"player":l[0], "target":l[2], "kill":l[3]}
        elif l[1] == "remove_omen":
            return {"action":l[1],"player":l[0], "kill":l[2]}
        elif l[1] == "gravedig_guess":
            return {"action":l[1],"player":l[0], "target":l[2], "role":l[3]}
        elif l[1] == "gravedig_frame":
            return {"action":l[1],"player":l[0],"target":l[2], "kill":l[4]}
        elif l[1] == "grant_ritual_investigation":
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
    elif action == 'introlink':
        return 'introlink ' + json_obj['link']
    else:
        player = json_obj['player']
        if action == 'investigate' or action == 'ritual_investigate':
            command = player + ' {} '.format(action) + json_obj['suspect1'] + ' ' + json_obj['suspect2'] + ' '
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
                command += ' result "' + json_obj['result'] + '"'
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
        elif action == 'vote-no-execution':
            return player + ' vote-no-execution ' + str(json_obj['yes'])
        elif action == 'vote-jailbreak':
            return player + ' vote-jailbreak ' + json_obj['target'] + ' ' + str(json_obj['yes'])
        elif action == 'frame':
            return player + ' frame ' + json_obj['target'] + ' kill ' + json_obj['kill']
        elif action == 'trap':
            return player + ' trap ' + json_obj['target'] + ' guess "' + (json_obj['guess'] if json_obj['guess'] else "") + '"'
        elif action == 'untrap':
            return player + ' untrap ' + json_obj['target']
        elif action == 'trap-manipulate-investigator':
            return player + ' trap-manipulate-investigator ' + json_obj['target'] + ' ' + json_obj['suspect1'] + json_obj['suspect2'] + ' kill ' + json_obj['kill'] + ' result ' + json_obj['result']
        elif action == 'trap-manipulate':
            return player + ' trap-manipulate ' + json_obj['target'] + " '" + json.dumps(json_obj['info']) + "'"
        elif action == 'trap-manipulate-remove-index':
            return player + ' trap-manipulate-remove-index ' + json_obj['target'] + ' ' + str(json_obj['index'])
        elif action == 'intro':
            return player + ' intro'
        elif action == 'drop':
            return player + ' drop'
        elif action == 'conscript':
            return player + ' conscript'
        elif action == 'gravedig':
            return player + ' gravedig ' + json_obj['target'] + ' ' +json_obj['type']
        elif action == 'grave_plant':
            return player + ' grave_plant ' + json_obj['target'] + ' '+json_obj['role']+' '+json_obj['alignment']
        elif action == 'census':
            return player + ' census ' + json_obj['target']
        elif action == 'fortune_tell':
            return player + ' fortune_tell ' + json_obj['target'] + ' ' + json_obj['kill'] 
        elif action == 'set_omen':
            return player + ' set_omen ' + json_obj['target'] + ' ' + json_obj['kill'] 
        elif action == 'remove_omen':
            return player + ' remove_omen ' + json_obj['kill'] 
        elif action == 'gravedig_guess':
            return player + ' gravedig_guess ' + json_obj['target'] + ' '+json_obj['role']
        elif action == 'gravedig_frame':
            return player + ' gravedig_frame ' + json_obj['target'] + ' for ' + json_obj['kill']
        elif action == 'grant_ritual_investigation':
            return player + ' ' + action
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
        if not "tiebreak" in game:
            game["tiebreak"] = []
            for player in game["players"]:
                game["tiebreak"] += [player]
            random.shuffle(game["tiebreak"])
            with open(get_game_file_location(command["name"])+"init.txt","w") as file:
                file.write(json.dumps(game))
    elif action == "seed":
        random.seed(command["seed"])
    elif action == "rollover":
        rollover(game)
    elif action == "introlink":
        game["intro"] = command["link"]
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
            if "result" not in command or command["result"]=="":
                (x,y,z,w) = investigate(game, player, x, y, z)
                command["result"] = w
            else:
                w = command["result"]
                check_valid_player(game, w)
                investigate(game, player, x, y, z, w=w)
        elif action == "ritual_investigate":
            x = command["suspect1"]
            y = command["suspect2"]
            z = command["kill"]
            check_valid_player(game, x)
            check_valid_player(game, y)
            check_valid_player(game, z)
            if "result" not in command or command["result"]=="":
                (x,y,z,w) = ritual_investigate(game, player, x, y, z)
                command["result"] = w
            else:
                w = command["result"]
                check_valid_player(game, w)
                ritual_investigate(game, player, x, y, z, w=w)
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
        elif action == "gravedig":
            gravedig(game, player, command["target"], command["type"])
        elif action == "grave_plant":
            set_gravedig(game, player, command["target"], command["role"], command["alignment"])
        elif action == "census":
            census(game, player, command["target"])
        elif action == "fortune_tell":
            fortune_tell(game, player, command["target"], command["kill"])
        elif action == "set_omen":
            add_mafia_omen(game, player, command["target"], command["kill"])
        elif action == "remove_omen":
            remomve_mafia_omen(game, player, command["kill"])
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
        elif action == "vote-no-execution":
            submit_vote_no_execution(game, player, command["yes"])
        elif action == "vote-jailbreak":
            submit_vote_jailbreak(game, player, command["target"], command["yes"])
        elif action == "frame":
            check_valid_player(game, command["target"])
            check_valid_player(game, command["kill"])
            frame(game, player, command["kill"], command["target"])
        elif action == "gravedig_guess":
            check_valid_player(game, command["target"])
            gravedig_role_guess(game, player, command["target"], command["role"])
        elif action == "gravedig_frame":
            check_valid_player(game, command["target"])
            check_valid_player(game, command["kill"])
            gravedig_frame(game, player, command["kill"], command["target"])
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
        elif action == "trap-manipulate-investigator":
            target = command["target"]
            x = command["suspect1"]
            y = command["suspect2"]
            z = command["kill"]
            w = command["result"]
            set_trap_investigation(game, player, target, x, y, z, w)
        elif action == "trap-manipulate":
            target = command["target"]
            set_trap_info(game, player, target, command["info"])
        elif action == "trap-manipulate-remove-index":
            remove_trap_info(game,player, command["target"], command["index"])
        elif action == "intro":
            game["players"][player]["intro"]=1
        elif action == "drop":
            game["players"][player]["alive"]=0
        elif action == "conscript":
            promote_to_mafia(game, player)
        elif action == "grant_ritual_investigation":
            grant_ritual_investigation(game,player)
    return (game, command)

if __name__=="__main__":
    with open("game_actions.txt") as file:
        (game, valid, messages) = do_commands([l.rstrip() for l in file.readlines()])
        with open("game_actions_valid.txt","w") as file:
            for line in valid:
                file.write(line+"\n")
