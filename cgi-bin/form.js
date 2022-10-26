
function setupRequest() {
var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
             document.getElementById("player-info").innerHTML = xhttp.responseText;
      }
  };
  xhttp.open("POST", "update_player.py", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  return xhttp;
}
fuction gg() {
  return "id="+getInput("id")+"&player="+getInput("player");
}
function getInput(i) {
  return document.getElementsById(i).value;
}
function sendVote() {
  var xhttp = setupRequest();
  params = "id="+document.getElementById("id").value+"&player="+document.getElementById("player").value+"&action=vote&target="+document.getElementById("vote").value;
  xhttp.send(params); 
}
function sendInvestigation() {
  var xhttp = setupRequest();
  params = "id="+document.getElementById("id").value+"&player="+document.getElementById("player").value+"&action=investigate&x="+
  document.getElementById("A").value+"&y="+document.getElementById("B").value+"&z="+document.getElementById("kill").value;
  xhttp.send(params); 
}
function sendProphecy() {
  var xhttp = setupRequest();
  params = "id="+document.getElementById("id").value+"&player="+document.getElementById("player").value+"&action=predicts&prophecy=\""+
  document.getElementById("victim").value+" will die at "+document.getElementById("time").value+" in "+document.getElementById("place").value+"\"";
  xhttp.send(params);
}
function sendRoleBlock() {
  var xhttp = setupRequest();
  params = gg()+"&action=roleblock&target="+getInput("target")
  xhttp.send(params);
}