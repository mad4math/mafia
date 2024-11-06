This webapp processes the role abilities and votes in a Live Action Mafia Game. It does not provide a method for player communication. For that you should use the mafia coauthor.
It also does not provide any security guarentees: There are no passwords or similar protections to logging in as another player.

#### To start a server

```
python cgi-bin/server.py [hostname] [port]
```

(defaults to localhost 8080)


### To GM a game

Go to `hostname/admin.html`.

## Making a new game

Click the new game link. Fill in the url of the thread for intros, the mafia and serial killer counts, and the list of player usernames.
These will be the usernames that players log in to the webapp with and identify other players. The click generate game.

In the main admin page, select a game name and click "load game" to view the state of that game.
The main text box gives the game history as a list of commands along with timestamps. When any player loads the game, all lines of the game history with timestamp <= now will be run, and ones for future timestamps will be ignored. This lets you do things like schedule a day rollover or a kill announcement to happen at a future time. 

You can freely edit this textbox to change the game history. Any lines which don't parse will be deleted from the history.

### To submit actions as a player

Go to `hostname/mafia.html`. Type in your username, and select the right game name (most recent one is selected by default).