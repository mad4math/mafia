
function setupRequest() {
var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
             document.getElementById("player-info").innerHTML = xhttp.responseText;
      }
  };
  xhttp.open("POST", "update-player", true);
  xhttp.setRequestHeader("Content-type", "application/json");
  return xhttp;
}
function gg() {
  return {"id": getInput("id"),
"command": {
  "player" : getInput("player")
}};
}
function getInput(i) {
  return document.getElementById(i).value;
}
function sendVote() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "vote"
  c.command.target = getInput("vote");
  xhttp.send(JSON.stringify(c));
}
function sendVoteNoExecution() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "vote-no-execution";
  c.command.yes = document.getElementById("no-execution-checkbox").checked;
  xhttp.send(JSON.stringify(c));
}
function sendInvestigation() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "investigate";
  c.command.suspect1 = getInput("A");
  c.command.suspect2 = getInput("B");
  c.command.kill = getInput("kill");
  if(document.getElementById("w"))
      c.command.result = getInput("w");
  xhttp.send(JSON.stringify(c));
}
function sendProphecy() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "predicts";
  c.command.prophecy = getInput("victim") + " will die at "+getInput("time")+" in "+getInput("place");
  xhttp.send(JSON.stringify(c));
}
function sendRoleblock() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "roleblock";
  c.command.target = getInput("target");
  xhttp.send(JSON.stringify(c));
}
function sendPriestSinnersList() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "priest";
  c.command.mode = "sinners";
  c.command.list = Array.from(document.getElementById("sinners").getElementsByTagName("select")).map(x => x.value);
  xhttp.send(JSON.stringify(c));
}
function sendPriestSaintsList() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "priest";
  c.command.mode = "saints";
  c.command.list = Array.from(document.getElementById("saints").getElementsByTagName("select")).map(x => x.value);
  xhttp.send(JSON.stringify(c));
}
function sendInfallible() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "guess";
  c.command.target = getInput("target");
  xhttp.send(JSON.stringify(c));
}
function sendSeer() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "seer";
  c.command.target = getInput("target");
  xhttp.send(JSON.stringify(c));
}
function sendFrame() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "frame";
  c.command.target = getInput("framed");
  c.command.kill = getInput("frame-victim");
  xhttp.send(JSON.stringify(c));
}
function sendTrap() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "trap";
  c.command.target = getInput("trap-target");
  c.command.guess = getInput("trap-guess");
  xhttp.send(JSON.stringify(c));
}
function sendUntrap() {
  if(getInput("untrap-target")) {
    var xhttp = setupRequest();
    var c = gg();
    c.command.action = "untrap";
    c.command.target = getInput("untrap-target");
  xhttp.send(JSON.stringify(c));
  }
}
function sendActionWithTarget(action) {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = action;
  c.command.target = getInput("target");
  xhttp.send(JSON.stringify(c));
}
function sendTrappedPlayerSettings(player) {
  var xhttp = setupRequest();
  var c = gg();
  var trapped_player = document.getElementById("trapped-"+player);
  c.command.action = "trap-manipulate-investigator";
  c.command.target = player;
  c.command.suspect1 = trapped_player.getElementsByClassName("trap-investigation-x")[0].value;
  c.command.suspect2 = trapped_player.getElementsByClassName("trap-investigation-y")[0].value;
  c.command.kill = trapped_player.getElementsByClassName("trap-investigation-z")[0].value;
  c.command.result = trapped_player.getElementsByClassName("trap-investigation-w")[0].value;
  xhttp.send(JSON.stringify(c));
}