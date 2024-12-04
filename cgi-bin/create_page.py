import mafia

option = lambda x:"<option value=\"{}\">{}</option>".format(x,x)
player_list = lambda game:sorted(game["players"])
game_intro = lambda game: game["intro"] if "intro" in game else "https://mafia.csail.mit.edu/24-01-town-square/m/5nfhnXrLAHyXcZzkg"

def investigation_options(game,mafia):
    return """Investigate <select name="suspect1" class="trapInvestigationX" data-a>{x}</select> and <select name="suspect2" class="trapInvestigationY" data-a>{y}</select>
     for kill <select name="kill" data-a>{z}</select>
    {w}<button name="submit">Submit</button>
    """.format(x="\n".join(option(x) for x in player_list(game)), y="\n".join(option(x) for x in player_list(game)),
        z="\n".join(option(x) for x in game["deaths"]), w = """with result <select class="investigationResultSubmission" name="result" data-a></select>""" if mafia else "")

def role(game, player):
    p = game["players"][player]
    pl = player_list(game)
    role_actions = "You are a <b>{}</b><br>".format(p["role"])
    if not p["intro"]:
        return "Please post your intro on <a href={}>this thread</a>".format(game_intro(game))
    if p["roleblocked"] and p["role"]!="gay knight":
        return role_actions + "<br> You are roleblocked today!"
    if not p["alive"]:
        return role_actions + "<br> You are dead!"
    if p["roleblocked"] and p["role"]=="gay knight":
        role_actions += "<br> You are roleblocked today, but you still have your gay knight abilities."
    all_players_options = "\n".join(option(x) for x in pl)
    alive_options = "\n".join(option(x) for x in pl if game["players"][x]["alive"])
    deaths_options = "\n".join(option(x) for x in game["deaths"])
    if p["role"]=="investigator":
        m = ""
        mf = ""
        if p["team"] == "mafia" or p["team"] == "sk":
            m = """
            with result <select id="w" class="investigationResultSubmission">{}</select>
            """.format(option("")+all_players_options)
            mf = """
            <br>
            Frames left: {frames}<br>
            Frame <select id="framed">{target}</select> for the death of <select id="frame-victim">{victim}</select>
            <button onClick=sendFrame()>Frame</button> (Note that you can frame before a death has happened; it won't have any effect until they die.)
            They will appear guilty for any investigations on this kill.
            <br>
            """.format(frames = p["frames"],target = all_players_options,victim = all_players_options)
        role_actions += """
        Submit an investigation: (You have <b>{}</b> left today.)<br>
        <select id="A">{}</select> and <select id="B">{}</select> for kill <select id="kill">{}</select>{}
        <button onClick=sendInvestigation()>Investigate</button>{}
        """.format(p["investigations"],all_players_options,all_players_options,deaths_options,m,mf)
    elif p["role"] == "vigilante":
        if mafia.get_alive_buddy(game, player) != player:
            role_actions += """
            Submit an investigation: (You have <b>{}</b> left today.)<br>
            <select id="A">{}</select> and <select id="B">{}</select> for kill <select id="kill">{}</select>{}
            <button onClick=sendInvestigation()>Investigate</button>{}
            """.format(p["investigations"],all_players_options,all_players_options,deaths_options)

    elif p["role"] == "prophet":
        deaths_options_a = "\n".join(option(x) for x in game["deaths"] if (x in p["investigations"] and p["investigations"][x]))
        m = ""
        if p["team"] == "mafia" or p["team"] == "sk":
            m = """
            with result <select id="w" class="investigationResultSubmission">{}</select>
            """.format(option("")+all_players_options)
        role_actions += """
                Submit a prophecy:<br>(Note: investigations from prophecies will be granted manually by GMs because locations can be ambiguous sometimes)<br>
        You predict that <select id=victim>{}</select> will die at (time) <input id="time"> in (location) <input id="place">
        <button onclick="sendProphecy()">Submit Prophecy</button>
        <br>
        Prediction for tomorrow: <b>{}</b><br>
        Prediction for today (made yesterday): <b>{}</b>
        <br>
        Investigations remaining:<br>
        {}
        <br>
        Submit an investigation:
        <select id="A">{}</select> and <select id="B">{}</select> for kill <select id="kill">{}</select>{}
        <button onclick="sendInvestigation()">Investigate</button>
        """.format(alive_options, p["prophecies"][game["day"]], p["prophecies"][game["day"]-1], "\n<br>".join("<b>"+target+": "+str(p["investigations"][target])+"</b>" for target in p["investigations"]),
         all_players_options, all_players_options, deaths_options_a, m)
    elif p["role"] == "roleblocker":
        role_actions += """
                Submit a roleblock:<br>
        <select id="target">{}</select>
        <button onclick="sendActionWithTarget('roleblock')">Submit Roleblock</button>
        """.format("\n".join(option(x) for x in pl if game["players"][x]["alive"] and x not in p["all_rollblocks"] and x!=player))
    elif p["role"] == "seer":
        selector = """<select id="target">{}</select>""".format(all_players_options)
        if game["day"]>0 and p["uses"]>0:
            role_actions += """
            Submit a player to see the role of:{}
            <button onclick="sendActionWithTarget('seer')">See</button>
            """.format(selector)
    elif p["role"] == "gravedigger":
        if game["day"]>0 and p["roleChecks"]>0:
            gravedig_options = "\n".join(option(x) for x in player_list(game) if not game["players"][x]["alive"])
            role_actions += """
            You have {x} gravedigs left today. Submit a dead player to gravedig the role the role of:
            <select id="roleTarget">{gravedig_options}</select>
            <button onclick="sendGravedigRole()">Gravedig</button><br>
            You have {y} gravedig alignment checks.
            """.format(gravedig_options = gravedig_options, x = p["roleChecks"], y = p["alignmentChecks"])
            if p["alignmentChecks"] > 0:
                role_actions += """Submit a dead player to gravedig the alignment of:
                <select id="alignmentTarget">{gravedig_options}</select>
                <button onclick="sendGravedigAlignment()">Gravedig</button><br>
                """.format(gravedig_options = gravedig_options)
        if p["team"] != "town":
            role_actions += """
            You can change the role and alignment seen by other gravediggers for a partiuclar player {x} more times this game. (You can plant evidence before the player dies, it won't have any until the player dies.)<br>
            Change <select id="gravedigPlantTarget">{gravedig_options}</select> to role
            <select id="gravedigPlantRole">{role}</select> and alignment
            <select id="gravedigPlantAlignment">{alignment}</select>
            <button onclick="sendPlant()">Plant Evidence</button>
            """.format(x=p["plants"], gravedig_options = "\n".join(option(x) for x in player_list(game)), role = "\n".join(option(x) for x in mafia.roles),
                alignment = "\n".join(option(x) for x in ["town", "mafia"]))
            role_actions += """
            <div data-action="gravedig_guess">
            You can guess the role of a player you've killed, and if you are right, you can frame them. <br>
            (Note: This interface lets you submit a guess and frame for a living player. This is so you can complete your frame before the death is entered into the webapp and announced. <b>It is against the rules to use this on a player you did not kill.</b>)<br>
            Guess the role for the death of <select name="target" data-a>{target}</select> as <select name="role" data-a>{role}</select>
            <button name="submit">Submit</button></div>
            {frames}
            """.format(target = "\n".join(option(x) for x in player_list(game)), role = "\n".join(option(x) for x in mafia.roles), 
                frames = "<br>".join("""<span data-action="gravedig_frame">You correctly guessed that {target} was a {role}. Frame <select name="target" data-a>{frameTarget}</select> for {target}'s death <input type="hidden" name="kill" value="{target}" data-a><button name="submit">Submit</button></span>""".format(
                    target = x, role = p["gravedig_guesses"][x]["role"], frameTarget = all_players_options) for x in p["gravedig_guesses"] if p["gravedig_guesses"][x]["frames_left"] > 0))
    elif p["role"] == "censusmaster":
        if game["day"]>0 and p["roleCounts"]>0:
            role_actions += """
            You have {x} role counts left today. Submit a role to learn how many players left alive have that role:
            <select id="roleTarget">{role_options}</select>
            <button onclick="sendCensus()">Count</button><br>
            You have {y} mafia counts left.
            """.format(role_options = "\n".join(option(x) for x in mafia.roles), x = p["roleCounts"], y = p["mafiaCounts"])
            if p["mafiaCounts"] > 0:
                role_actions += """<button onclick="sendCensusMafia()">Count the mafia!</button><br>
                """
    elif p["role"] == "fortune teller":
        if game["day"]>0 and p["uses"] > 0:
            role_actions += """
            You have {x} fortune tellings remaining today.<br>
            Check <select id="fortuneTarget">{target}</select> for omens about the death of <select id="fortuneKill">{kill}</select>
            <button onclick="sendFortune()">Check fortunes</button>.
            """.format(target = "\n".join(option(x) for x in player_list(game)), kill = "\n".join(option(x) for x in game["deaths"]), x = p["uses"])         


    elif p["role"] == "priest":
        alive_selector = "<select>{}</select><br>".format(option(" ")+alive_options)
        size = int(len([x for x in pl if game["players"][x]["alive"]])*.4)
        future_sinners = ", ".join(x if i < size else "<s>"+x+"</s>" for (i,x) in enumerate(p["tomorrow"]["sinners"]))
        remaining_size = size - len(p["tomorrow"]["sinners"])
        future_saints = ", ".join(x if i < remaining_size else "<s>"+x+"</s>" for (i,x) in enumerate(p["tomorrow"]["saints"]))
        if p["active"]:
            role_actions += """
                    Submit priest lists: (if you lists are too big, the last people on your saints list will be ignored. 
                    The max combined size of the lists is 40 percent of the number of alive players at the end of the day, rounded up.
                    If your lists are currently too big, the entires that will be ignored are shown crossed out)<br>
                    Current sinners list: {future_sinners}<br>
                    Current saints list: {future_saints}<br>
            List type:<select id="mode">{mode}</select><br>
            <div id="priestList">
            {list_selector}    
            <button onclick="sendPriestList()">Submit list</button></div>
            </div>
            Current lists for today:<br>
            Sinners: {sinners}<br>
            Saints: {saints}<br>
            """.format(future_sinners = future_sinners, list_selector = alive_selector*size, future_saints = future_saints,
                sinners = p["today"]["sinners"],saints = p["today"]["saints"], mode = option("sinners")+option("saints"))
        else:
            role_actions += """You lost your priestly role powers!"""
    elif p["role"] == "gay knight":
        a = """
        Your partner is {}.<br>
        """.format(p["partner"])
        if not game["players"][p["partner"]]["alive"]:
            a += """
            Your partner has died! You will die at the end of <b>{}</b>.<br>
            """.format("tonight" if p["dying"] else "tomorrow")
            if p["correct"]:
                a += """
                <br> {} killed your partner! You may revenge kill them with "bang"!
                <br>
                """.format(game["deaths"][p["partner"]]["true_killer"])
            else:
                a += """
                Who do you think did it? You have <b>{}</b> guesses left.<br>
                <select id="target">{}</select>
                <button onclick="sendActionWithTarget('guess')"> Submit </button>
                """.format(p["guesses"],all_players_options)

        role_actions += a
    for power in p["additional_powers"]:
        if power == "ritual_investigation":
            role_actions += """<div data-action="ritual_investigate">
            You have a ritual investigation today! (submit below) <br>{inv}</div>
            """.format(inv = investigation_options(game, p["team"] != "town"))
    return role_actions
def faction(game, player):
    alive_options = "\n".join(option(x) for x in player_list(game) if game["players"][x]["alive"])
    role_options = "\n".join(option(x) for x in mafia.roles)
    all_players_options = "\n".join(option(x) for x in player_list(game))
    def trap_interface(count, trapped):
        aa = """
            Use a trap: Trap <select id="trap-target">{}</select> as <select id="trap-guess">{}</select> 
            <button onclick="sendTrap()">Trap!</button> Traps left: <b>{}</b><br>
            Untrap a player: <select id="untrap-target">{}</select><button onclick="sendUntrap()">Untrap</button>
            <br>
            """.format(alive_options, role_options, count, "\n".join(option(x) for x in trapped))
        aa += "<br>".join(trapped_player_settings(player, trapped[player]) for player in trapped)
        return aa
    def trapped_player_settings(player, trapped_settings):
        role = game["players"][player]["role"]
        aa = """
        <br>
        <div id="trapped-{player}">
        Trap settings for <b>{player}</b>({role}):<br>

        """.format(player=player, role=role)
        if role == "investigator" or role == "prophet":
            aa += """
            Now that {player} is trapped, you can control the results they receive on investigations. Using the dropdowns below,
            you can select what results they should receive for specific investigations. Anything you don't specify will resolve as
            if they were not trapped. Because of the wildcard $EVERYONE, multiple rules may apply, in which case the last one submitted (at the bottom of the list) will take precedence.<br>
            <select class="trapInvestigationX">{x}</select> and <select class="trapInvestigationY">{y}</select> for kill <select class="trapInvestigationZ">{z}</select>
            should return <select class="investigationResultSubmission">{w}</select><button onclick="sendTrappedInfo('{player}','investigator')">Submit</button>
            <br>
            """.format(x = "\n".join(option(x) for x in ["$EVERYONE"]+player_list(game)),
            y = "\n".join(option(x) for x in ["$EVERYONE"]+player_list(game)),
            z = "\n".join(option(x) for x in ["$EVERYONE"]+list(game["deaths"].keys())),
            w = "",
            player = player)
            aa += """Current manipulations:<br>
            """ + "<br>".join("""<button onclick="removeTrappedInfo('{player}',{i})">Remove</button>{{<b>{x}, {y}</b>}} for kill <b>{z}</b> returns <b>{w}</b> is innocent.
                """.format(x = trapped_settings["manipulations"][i]["suspect1"], y = trapped_settings["manipulations"][i]["suspect2"], z = trapped_settings["manipulations"][i]["kill"],
                 w = trapped_settings["manipulations"][i]["result"], player = player, i=i) for i in range(len(trapped_settings["manipulations"])))
            #aa += "<br><br>"
        elif role == "seer":
            aa += """
            Now that {player} is trapped, you can control the results they see. Using the dropdowns below, you can select what results they will see
            for specific players. Anything you don't specify will resolve as
            if they were not trapped.<br>
            See player <select class="seerTrapX">{x}</select> as <select class="seerTrapResult">{y}</select><button onclick="sendTrappedInfo('{player}','seer')">Submit</button>
            """.format(x = "\n".join(option(x) for x in player_list(game) if game["players"][x]["alive"]), y = "\n".join(option(x) for x in mafia.roles),
                player = player)
            aa += """Current manipulations:<br>
            """ + "<br>".join("""<button onclick="removeTrappedInfo('{player}',{i})">Remove</button>Sees <b>{x}</b> as <b>{y}</b>
                """.format(x = trapped_settings["manipulations"][i]["target"], y = trapped_settings["manipulations"][i]["result"], player = player, i=i) for i in range(len(trapped_settings["manipulations"])))
            
        elif role == "gravedigger":
            aa += """
            Now that {player} is trapped, you can control the results they see. Using the dropdowns below, you can select what results they will see
            for specific players. Anything you don't specify will resolve as
            if they were not trapped.<br>
            See player <select class="gravediggerTrapX">{x}</select> as role <select class="gravediggerTrapRoleResult">{y}</select> and alignment
            <select class="gravediggerTrapAlignmentResult">{z}</select> 
            <button onclick="sendTrappedInfo('{player}','gravedigger')">Submit</button>
            """.format(x = "\n".join(option(x) for x in player_list(game)), y = "\n".join(option(x) for x in mafia.roles), 
                z = "\n".join(option(x) for x in ["town","mafia"]), player = player) 
            aa += """Current manipulations:<br>
            """ + "<br>".join("""<button onclick="removeTrappedInfo('{player}',{i})">Remove</button>Sees <b>{x}</b> as <b>{y} and {z}</b>
                """.format(x = trapped_settings["manipulations"][i]["target"], y = trapped_settings["manipulations"][i]["roleResult"],
                 z = trapped_settings["manipulations"][i]["alignmentResult"], player = player, i=i) for i in range(len(trapped_settings["manipulations"])))
            
        elif role == "censusmaster":
            aa += """
            Now that {player} is trapped, you can control the results they see. Anything you don't specify will resolve as
            if they were not trapped.<br>
            See role/alignment <select class="censusTrapX">{x}</select> as count <select class="censusTrapResult">{y}</select>
            <button onclick="sendTrappedInfo('{player}','censusmaster')">Submit</button>
            """.format(x = "\n".join(option(x) for x in mafia.roles + ["mafia"]), y = "\n".join(option(x) for x in range(10)), player = player) 
            aa += """Current manipulations:<br>
            """ + "<br>".join("""<button onclick="removeTrappedInfo('{player}',{i})">Remove</button>Sees <b>{x}</b> as having a count of <b>{y}</b>
                """.format(x = trapped_settings["manipulations"][i]["x"], y = trapped_settings["manipulations"][i]["result"], player = player, i=i) for i in range(len(trapped_settings["manipulations"])))
            
        elif role == "fortune teller":
            aa += """
            Now that {player} is trapped, you can control the results they see. Anything you don't specify will resolve as
            if they were not trapped.<br>
            <select class="fortuneTellerTrapX">{x}</select> has a <select class="fortuneTellerTrapResult">{z}</select> omen for the death of 
            <select class="fortuneTellerTrapY">{y}</select><button onclick="sendTrappedInfo('{player}','fortune teller')">Submit</button>
            """.format(x = "\n".join(option(x) for x in player_list(game) if game["players"][x]["alive"]), y = "\n".join(option(x) for x in game["deaths"]),
            z = "\n".join(option(x) for x in ["Good","Bad"]), player = player) 
            aa += """Current manipulations:<br>
            """ + "<br>".join("""<button onclick="removeTrappedInfo('{player}',{i})">Remove</button>Sees <b>{x}</b> as having a <b>{z}</b> omen for the death of <b>{y}</b>
                """.format(x = trapped_settings["manipulations"][i]["x"], y = trapped_settings["manipulations"][i]["y"],
                 z = trapped_settings["manipulations"][i]["result"], player = player, i=i) for i in range(len(trapped_settings["manipulations"])))
            
        aa += "</div>"
        return aa
    a = ""
    if game["players"][player]["team"]=="mafia":
        a += """
        You are the mafia! The mafia team is <b>{}</b><br>""".format(",".join(p for p in game["players"] if game["players"][p]["team"]=="mafia"))
        if mafia.USE_BUDDY:
            a += """
            Use a trap: Trap <select id="trap-target">{}</select> as the buddy of <select id="trap-guess">{}</select> 
            <button onclick="sendTrap()">Trap!</button> Traps left: <b>{}</b>
            """.format(alive_options, all_players_options, game["mafia"]["traps"])
        else:
            a += trap_interface(game["mafia"]["traps"], game["mafia"]["trapped"])
    elif game["players"][player]["team"]=="sk":
        a += """
        You are a serial killer. You are on the mafia's team, but you don't know who the mafia are. You may kill once every 2 game days, starting day 1.<br>
        """
        #        days remaining until you may next kill: <b>{}</b>""".format(game["players"][player]["cooldown"])
        a += trap_interface(game["players"][player]["traps"], game["players"][player]["trapped"])
    else:
        if mafia.USE_BUDDY:
            a += """
            You are <b>town</b>. You buddy is <b>{}</b>. You both know that each other is town, and share some role actions. You should coordinate with each other!
            """.format(game["players"][player]["buddy"])
        else:
            a += """ You are <b>town</b>."""
    if game["players"][player]["team"] == "mafia":
        a += """<br>
        Set a bad omen for a future kill:<select id="mafiaOmenTarget">{target}</select> will have a Bad omen for the future death of <select id="mafiaOmenKill">{kill}</select>
        <button id="addOmen" onclick="sendOmen()">Submit</button>
        <br>(Note: You need to set who will have a bad omen before you make a kill; setting this field has no effect if you never kill the player.)<br>
        Previously set omens:<br>
        {omens}
        <br><br>
        """.format(target = "\n".join(option(x) for x in player_list(game)), kill = "\n".join(option(x) for x in player_list(game) if game["players"][x]["alive"]),
            omens = "\n".join("""<button id="removeOmen" onclick="removeOmen('{y}')">Remove</button> {x} will have a Bad omen for the future death of {y}""".format(x=game["mafia"]["omens"][x],y=x) for x in game["mafia"]["omens"]))
    return a 

def display(game, player, messages):
    allowed = [player, "public", "error"]
    if game["players"][player]["team"]=="mafia":
        allowed += ["mafia"]
    return "<br>\n".join(x for x in messages if any((y+":") in x for y in allowed))

def player_info(game, player, messages):
    votable=[x for x in player_list(game) if game["players"][x]["alive"]]
    if game["day"]<200:
        pass
        votable+=["no-execution"]
    jailbreak_votes = "\n".join("""
      <input type="checkbox" onClick=sendVoteJailbreak("{p}") id="jailbreak-checkbox-{p}" {is_checked}><label for="jailbreak-checkbox-{p}">Release {p} from jail</label>
    """.format(p=p, is_checked = "checked" if p in game["players"][player]["jailbreak_votes"] else "")
    for p in game["players"] if game["players"][p]["jailed"] and game["players"][p]["alive"]
    )
    #<input type="checkbox" onClick=sendVoteNoExecution() id="no-execution-checkbox" {no_execute}><label for="no-execution-checkbox">Vote no execution if legal</label>
    voting = """
              <div>
                Vote for a player to jail:<br>
                <select id="vote">
                {vote_options}
                </select>
      <button onClick=sendVote()>Send Vote</button>
      Currently voting for: <b>{vote}</b>
      <div>
      Vote to release players from jail:<br>
      {jailbreak_votes}""".format(vote_options = "\n".join(option(x) for x in votable), 
        vote = game["players"][player]["vote"] if not (mafia.can_vote_no_execution(game) and game["players"][player]["vote_no_execution"]) else """
        <span style="text-decoration: line-through">{}</span>No Execution""".format(game["players"][player]["vote"]), no_execute = "checked" if game["players"][player]["vote_no_execution"] else "",
        jailbreak_votes = jailbreak_votes)
    return """
    {voting}
    </div>
    <div id="faction-abilities">
    {faction}
    </div>
    <div id="role-abilities">
    {role}
    </div>
    <h4> Game Log </h4>
    <div id="display" >{display}</div>
    """.format(voting = "You are jailed. You can't vote, and can't make kills, but you otherwise may still participate and take actions.<br>" if game["players"][player]["jailed"] else voting,
        faction = faction(game,player),role = role(game,player), display = display(game,player,messages),
        )

def main_page(game, player, messages): 
    h="""
    <html>
    <head>
    <meta charset="utf-8">

      <script type="text/javascript" src="../form.js">
      </script>
    </head>
    <body>
      <div style="width: 100%; overflow: hidden;">
        <div>
                game ID:<input id="id" value="{}" disabled><br>
                username:<input id="player" value="{}" disabled><br>
              </div>
      <div id="player-info">
      {}
    </div>
      </div>
    </body>
    </html>
    """.format(game["id"], player, player_info(game, player, messages))
    return h
