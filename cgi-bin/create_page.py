import mafia

option = lambda x:"<option value=\"{}\">{}</option>".format(x,x)
player_list = lambda game:sorted(game["players"])
game_intro = lambda game: game["intro"] if "intro" in game else "https://mafia.csail.mit.edu/24-01-town-square/m/5nfhnXrLAHyXcZzkg"

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
            with result <select id="w">{}</select>
            """.format(option("")+all_players_options)
            mf = """
            <br>
            Frames left: {}<br>
            Frame <select id="framed">{}</select> for <select id="frame-victim">{}</select>
            <br>
            """.format(p["frames"],all_players_options, deaths_options)
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
            with result <select id="w">{}</select>
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
         all_players_options, all_players_options, deaths_options_a, m) + """<br>
        prophecy for today that you made yesterday: {}<br>
        prophecy for tomorrow: {}
        """.format(p["prophecies"][game["day"]-1],p["prophecies"][game["day"]])
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
    elif p["role"] == "priest":
        alive_selector = "<select>{}</select><br>".format(alive_options)
        size = int(len([x for x in pl if game["players"][x]["alive"]])*.2+.99)
        if p["active"]:
            role_actions += """
                    Submit priest lists: (if enough people die before day rollover, the last entry from each will be ignored. The max size of each list is 20 percent of the number of alive players at the end of the day, rounded up.)<br>
            Sinners:(<b>current selection for tomorrow is {}</b>)<div id="sinners">
            {}    
            <button onclick="sendPriestSinnersList()">Submit sinners list</button></div>
            Saints:(<b>current selection for tomorrow is {}</b>)<div id="saints">
            {}
            <button onclick="sendPriestSaintsList()">Submit saints list</button></div>
            Current lists for today:<br>
            Sinners: {}<br>
            Saints: {}<br>
            """.format(p["tomorrow"]["sinners"],alive_selector*size,p["tomorrow"]["saints"],alive_selector*size,p["today"]["sinners"],p["today"]["saints"])
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

    return role_actions
def faction(game, player):
    alive_options = "\n".join(option(x) for x in player_list(game) if game["players"][x]["alive"])
    role_options = "\n".join(option(x) for x in mafia.roles)
    all_players_options = "\n".join(option(x) for x in player_list(game))
    def trap_interface(count, trapped):
        return """
            Use a trap: Trap <select id="trap-target">{}</select> as <select id="trap-guess">{}</select> 
            <button onclick="sendTrap()">Trap!</button> Traps left: <b>{}</b><br>
            Untrap a player: <select id="untrap-target">{}</select><button onclick="sendUntrap()">Untrap</button>
            """.format(alive_options, role_options, count, "\n".join(option(x) for x in trapped))

    if game["players"][player]["team"]=="mafia":
        a = """
        You are the mafia! The mafia team is <b>{}</b><br>""".format(",".join(p for p in game["players"] if game["players"][p]["team"]=="mafia"))
        if mafia.USE_BUDDY:
            a += """
            Use a trap: Trap <select id="trap-target">{}</select> as the buddy of <select id="trap-guess">{}</select> 
            <button onclick="sendTrap()">Trap!</button> Traps left: <b>{}</b>
            """.format(alive_options, all_players_options, game["mafia"]["traps"])
        else:
            a += trap_interface(game["mafia"]["traps"], game["mafia"]["trapped"])
        return a
    elif game["players"][player]["team"]=="sk":
        a = """
        You are a serial killer. You are on the mafia's team, but you don't know who the mafia are. You may kill once every 2 game days, starting day 1.<br>
        """
        #        days remaining until you may next kill: <b>{}</b>""".format(game["players"][player]["cooldown"])
        a += trap_interface(game["players"][player]["traps"], game["players"][player]["trapped"])
        return a
    else:
        if mafia.USE_BUDDY:
            a = """
            You are <b>town</b>. You buddy is <b>{}</b>. You both know that each other is town, and share some role actions. You should coordinate with each other!
            """.format(game["players"][player]["buddy"])
        else:
            a = """ You are <b>town</b>."""
        return a
def display(game, player, messages):
    allowed = [player, "public", "error"]
    if game["players"][player]["team"]=="mafia":
        allowed += ["mafia"]
    return "<br>\n".join(x for x in messages if any((y+":") in x for y in allowed))

def player_info(game, player, messages):
    votable=[x for x in player_list(game) if game["players"][x]["alive"]]
    if game["day"]<2:
        votable+=["no-execution"]
    return """
              <div>
                Vote for a player to execute:<br>
                <select id="vote">
                {}
                </select>
      <button onClick=sendVote()>Send Vote</button>
      Currently voting for: <b>{}</b>
      <input type="checkbox" onClick=sendVoteNoExecution() id="no-execution-checkbox" {}><label for="no-execution-checkbox">Vote no execution if legal</label>
    </div>
    <div id="faction-abilities">
    {}
    </div>
    <div id="role-abilities">
    {}
    </div>
    <h4> Game Log </h4>
    <div id="display" >{}</div>
    """.format("\n".join(option(x) for x in votable), 
        game["players"][player]["vote"], "checked" if game["players"][player]["vote_no_execution"] else "", faction(game,player),role(game,player), display(game,player,messages))

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
