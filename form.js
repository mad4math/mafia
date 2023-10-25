
function setupRequest() {
var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
             document.getElementById("player-info").innerHTML = xhttp.responseText;
      }
  };
  xhttp.open("POST", "update-player", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  return xhttp;
}
function gg() {
  return "id="+getInput("id")+"&player="+getInput("player");
}
function getInput(i) {
  return document.getElementById(i).value;
}
function sendVote() {
  var xhttp = setupRequest();
  params = "id="+document.getElementById("id").value+"&player="+document.getElementById("player").value+"&action=vote&target="+document.getElementById("vote").value;
  xhttp.send(params); 
}
function sendVoteNoExecution() {
  var xhttp = setupRequest();
  params = "id="+document.getElementById("id").value+"&player="+document.getElementById("player").value+"&action=vote-no-execution&yes="+document.getElementById("no-execution-checkbox").checked;
  console.log(document.getElementById("no-execution-checkbox").checked);
  xhttp.send(params); 

}
function sendInvestigation() {
  var xhttp = setupRequest();
  params = "id="+document.getElementById("id").value+"&player="+document.getElementById("player").value+"&action=investigate&x="+
  document.getElementById("A").value+"&y="+document.getElementById("B").value+"&z="+document.getElementById("kill").value;
  if(document.getElementById("w"))
    params += "&w="+getInput("w");
  xhttp.send(params); 
}
function sendProphecy() {
  var xhttp = setupRequest();
  params = "id="+document.getElementById("id").value+"&player="+document.getElementById("player").value+"&action=predicts&prophecy="+
  document.getElementById("victim").value+" will die at "+document.getElementById("time").value+" in "+document.getElementById("place").value;
  xhttp.send(params);
}
function sendRoleblock() {
  var xhttp = setupRequest();
  params = gg()+"&action=roleblock&target="+getInput("target");
  xhttp.send(params);
}
function sendPriestSinnersList() {
  var xhttp = setupRequest();
  sinners = Array.from(document.getElementById("sinners").getElementsByTagName("select")).map(x => x.value).join(" ");
  params = gg()+"&action=priest&sinners="+sinners;
  xhttp.send(params)
}
function sendPriestSaintsList() {
  var xhttp = setupRequest();
  saints = Array.from(document.getElementById("saints").getElementsByTagName("select")).map(x => x.value).join(" ");
  params = gg()+"&action=priest&saints="+saints;
  xhttp.send(params)
}
function sendInfallible() {
  var xhttp = setupRequest();
  params = gg() + "&action=guess&target="+getInput("target");
  xhttp.send(params);
}
function sendSeer() {
  var xhttp = setupRequest();
  params = gg()+"&action=seer&target="+getInput("target");
  xhttp.send(params);
}
function sendTrap() {
  var xhttp = setupRequest();
  params = gg()+"&action=trap&target="+getInput("trap-target")+"&guess="+getInput("trap-guess");
  xhttp.send(params);
}
function sendUntrap() {
  if(getInput("untrap-target")) {
    console.log(getInput("untrap-target"))
    var xhttp = setupRequest();
    params = gg()+"&action=untrap&target="+getInput("untrap-target");
    xhttp.send(params);
  }
}
function sendActionWithTarget(action) {
  var xhttp = setupRequest();
  params = gg()+"&action="+action+"&target="+getInput("target");
  xhttp.send(params);
}