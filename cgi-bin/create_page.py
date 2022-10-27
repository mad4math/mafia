

option = lambda x:"<option value={}>{}</option>".format(x,x)
player_list = lambda game:sorted(game["players"])

def role(game, player):
    p = game["players"][player]
    pl = player_list(game)
    role_actions = "You are a {}<br>".format(p["role"])
    if not p["intro"]:
        return "Please post your intro on <a href=https://mafia.csail.mit.edu/22-02-town-square/m/s3coEzHXqvaFeeESY>this thread</a>"
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
        if p["team"] == "mafia":
            m = """
            with result <select id="w">{}</select>
            """.format(all_players_options)
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
    elif p["role"] == "prophet":
        role_actions += """
                Submit a prophecy:<br>(Note: investigations from prophecies will be granted manually by GMs because locations can be ambiguous sometimes)<br>
        You predict that <select id=victim>{}</select> will die at (time) <input id="time"> in (location) <input id="place">
        <button onclick="sendProphecy()">Submit Prophecy</button>
        <br>
        Investigations remaining:<br>
        {}
        <br>
        Submit an investigation:
        <select id="A">{}</select> and <select id="B">{}</select> for kill <select id="kill">{}</select>
        <button onclick="sendInvestigation()">Investigate</button>
        """.format(alive_options, "\n<br>".join("<b>"+target+": "+str(p["investigations"][target])+"</b>" for target in p["investigations"]),
         all_players_options, all_players_options, deaths_options)
    elif p["role"] == "roleblocker":
        role_actions += """
                Submit a roleblock:<br>
        <select id="target">{}</select>
        <button onclick="sendRoleblock()">Submit Roleblock</button>
        """.format("\n".join(option(x) for x in pl if game["players"][x]["alive"] and x not in p["all_rollblocks"] and x!=player))
    elif p["role"] == "seer":
        selector = """<select id="target">{}</select><br>""".format(all_players_options)
        if game["day"]>0:
            role_actions += """
            <br>Submit a player to see the role of:{}<br>
            <button onclick="sendSeer()">See</button>
            """.format(selector)
    elif p["role"] == "priest":
        alive_selector = "<select>{}</select><br>".format(alive_options)
        size = int(len([x for x in pl if game["players"][x]["alive"]])*.2+.99)
        role_actions += """
                Submit priest lists: (if enough people die before day rollover, the last entry from each will be ignored)<br>
        Sinners:<div id="sinners">
        {}
        </div>Saints:<div id="saints">
        {}
        </div><button onclick="sendPriestList()">Submit lists</button>
        """.format(alive_selector*size,alive_selector*size)
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
                <button onclick="sendInfallible()"> Submit </button>
                """.format(p["guesses"],all_players_options)

        role_actions += a

    return role_actions
def display(game, player, messages):
    allowed = [player, "public", "error"]
    if game["players"][player]["team"]=="mafia":
        allowed += ["mafia"]
    return "<br>\n".join(x for x in messages if any((y+":") in x for y in allowed))

def player_info(game, player, messages):
    return """
    <div id="role-abilities">
    {}
    </div>
    <h4> Game Log </h4>
    <div id="display" >{}</div>
    """.format(role(game,player), display(game,player,messages))

def main_page(game, player, messages): 
    votable=[x for x in player_list(game) if game["players"][x]["alive"]]
    if game["day"]<2:
        votable+=["no-execution"]
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
                game ID:<input id="id" value="fall22-01" disabled><br>
                username:<input id="player" value="{}" disabled><br>
              </div>
              <div>
                Vote for a player to execute:<br>
                <select id="vote">
                {}
                </select>
      <button onClick=sendVote()>Send Vote</button>
    </div>
      <div id="player-info">
      {}
    </div>
      </div>
    </body>
    </html>
    """.format(player, "\n".join(option(x) for x in votable), player_info(game, player, messages))
    return h
