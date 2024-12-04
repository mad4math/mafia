
function setupRequest() {
var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
             document.getElementById("player-info").innerHTML = xhttp.responseText;
             setupListeners();
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
  c.command.yes = document.getElementById("no-execution-checkbox").checked? 1 : 0;
  xhttp.send(JSON.stringify(c));
}
function sendVoteJailbreak(player) {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "vote-jailbreak";
  c.command.target = player;
  c.command.yes = document.getElementById("jailbreak-checkbox-"+player).checked? 1 : 0;
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
function sendPriestList() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "priest";
  c.command.mode = getInput("mode");
  c.command.list = Array.from(document.getElementById("priestList").getElementsByTagName("select")).map(x => x.value).filter(x => x!=" ");
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

function sendGravedigRole() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "gravedig";
  c.command.target = getInput("roleTarget");
  c.command.type = "role";
  xhttp.send(JSON.stringify(c));
}
function sendGravedigAlignment() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "gravedig";
  c.command.target = getInput("alignmentTarget");
  c.command.type = "alignment";
  xhttp.send(JSON.stringify(c));
}
function sendCensus() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "census";
  c.command.target = getInput("roleTarget");
  xhttp.send(JSON.stringify(c));
}
function sendCensusMafia() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "census";
  c.command.target = "mafia";
  xhttp.send(JSON.stringify(c));
}
function sendFortune() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "fortune_tell";
  c.command.target = getInput("fortuneTarget");
  c.command.kill = getInput("fortuneKill");
  xhttp.send(JSON.stringify(c));
}
function sendOmen() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "set_omen";
  c.command.target = getInput("mafiaOmenTarget");
  c.command.kill = getInput("mafiaOmenKill");
  xhttp.send(JSON.stringify(c));
}
function removeOmen(y) {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "remove_omen";
  c.command.kill = y;
  xhttp.send(JSON.stringify(c));
}
function sendPlant() {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "grave_plant";
  c.command.target = getInput("gravedigPlantTarget");
  c.command.role = getInput("gravedigPlantRole");
  c.command.alignment = getInput("gravedigPlantAlignment");
  xhttp.send(JSON.stringify(c));
}


function sendTrappedInvestigation(player) {
  var xhttp = setupRequest();
  var c = gg();
  var trapped_player = document.getElementById("trapped-"+player);
  c.command.action = "trap-manipulate-investigator";
  c.command.target = player;
  c.command.suspect1 = trapped_player.getElementsByClassName("trapInvestigationX")[0].value;
  c.command.suspect2 = trapped_player.getElementsByClassName("trapInvestigationY")[0].value;
  c.command.kill = trapped_player.getElementsByClassName("trapInvestigationZ")[0].value;
  c.command.result = trapped_player.getElementsByClassName("investigationResultSubmission")[0].value;
  xhttp.send(JSON.stringify(c));
}

trappedRoleKeys = {
  "investigator": {
    "trapInvestigationX" : "suspect1",
    "trapInvestigationY" : "suspect2",
    "trapInvestigationZ" : "kill",
    "investigationResultSubmission" : "result"
  },
  "seer" : {
    "seerTrapX" : "target",
    "seerTrapResult" : "result"
  },
  "gravedigger" : {
    "gravediggerTrapX" : "target",
    "gravediggerTrapRoleResult" : "roleResult",
    "gravediggerTrapAlignmentResult" : "alignmentResult"
  },
  "censusmaster" : {
    "censusTrapX" : "x",
    "censusTrapResult" : "result"
  },
  "fortune teller" : {
    "fortuneTellerTrapX" : "x",
    "fortuneTellerTrapY" : "y",
    "fortuneTellerTrapResult" : "result"
  }
}

function sendTrappedInfo(player, role) {
  var xhttp = setupRequest();
  var c = gg();
  var trapped_player = document.getElementById("trapped-"+player);
  c.command.action = "trap-manipulate";
  c.command.target = player;
  info = trappedRoleKeys[role];
  c.command.info = {};
  for(x in info) {
    c.command.info[info[x]] = trapped_player.getElementsByClassName(x)[0].value;
  }
  xhttp.send(JSON.stringify(c));
}

function removeTrappedInfo(player, index) {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "trap-manipulate-remove-index";
  c.command.target = player;
  c.command.index = index;
  xhttp.send(JSON.stringify(c));
}

function removeTrappedInvestigation(player, x, y, z) {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "trap-manipulate-investigator";
  c.command.target = player;
  c.command.suspect1 = x;
  c.command.suspect2 = y;
  c.command.kill = z;
  c.command.result = "$Default";
  xhttp.send(JSON.stringify(c));
}
function sendTrappedSeer(player) {
  var xhttp = setupRequest();
  var c = gg();
  var trapped_player = document.getElementById("trapped-"+player);
  c.command.action = "trap-manipulate-seer";
  c.command.target = player;
  c.command.x = trapped_player.getElementsByClassName("seerTrapX")[0].value;
  c.command.result = trapped_player.getElementsByClassName("seerTrapResult")[0].value;
  xhttp.send(JSON.stringify(c));
}
function removeTrappedSeer(player, x) {
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = "trap-manipulate-seer";
  c.command.target = player;
  c.command.x = x;
  xhttp.send(JSON.stringify(c));

}



function setPossibleInvestigationResults(e) {

  var x = e.target.parentElement.getElementsByClassName("trapInvestigationX")[0].value;
  var y = e.target.parentElement.getElementsByClassName("trapInvestigationY")[0].value;
  var s = "<option value=\""+x+"\">"+x+"</option>" + "<option value=\""+y+"\">"+y+"</option>";// + "<option value=\"$Default\">Default</option>";
  e.target.parentElement.getElementsByClassName("investigationResultSubmission")[0].innerHTML = s;

}

roleActionKeys = {
  "gravedigger": {

  }
}

function sendAction(e) {
  //send a role action. e is the event fired from pressing the submit button in that container.
  var xhttp = setupRequest();
  var c = gg();
  c.command.action = e.target.parentElement.getAttribute("data-action");
  for(var ee of e.target.parentElement.querySelectorAll("[data-a]")) {
    c.command[ee.name] = ee.value;
  }
  xhttp.send(JSON.stringify(c));
}

function setupListeners() {
  for(var ee of document.getElementsByClassName("investigationResultSubmission")) {
      for(var e of ee.parentElement.getElementsByClassName("trapInvestigationX")) {
        e.addEventListener('change', setPossibleInvestigationResults);
      }
      for(var e of ee.parentElement.getElementsByClassName("trapInvestigationY")) {
        e.addEventListener('change', setPossibleInvestigationResults);
      }
    }
    for(var e of document.getElementsByName("submit")) {
      e.addEventListener('click', sendAction);
    }
}
window.addEventListener("load", function(){
    setupListeners();
});