function getUrlParam(name)
{
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    return urlParams.get(name);
}

class GameViewer {

    constructor() {
        this.serverSocketUrl = "ws://"+self.location.host.split(":")[0]+":8087";
        this.socket = new WebSocket(this.serverSocketUrl);
        this.connected = false;
        let that = this
        this.socket.onopen = function() {
            that.connected = true;
        };
        this.socket.onmessage = this.handleMessage;
    }

    fetchData() {
        if (this.connected) {
            this.socket.send("viewArena "+getUrlParam("id"));
        }
    }

    handleMessage(event) {
        let game = JSON.parse(event.data);
        let arena = game["board"];
        let state = game["state"];
        let stateReminingTicks = game["remainingTicks"];
        let stateNames = ["is pending", "- Round will start in ", "- Remining turn time : ", "is over"];
        let ranking = game["ranking"];
        document.getElementById("Title").innerHTML = "Game "+getUrlParam("id")+" "+stateNames[state];
        if (state == 1 || state == 2) {
            document.getElementById("Title").innerHTML += stateReminingTicks+" seconds";
        }
        let holder = document.getElementById("Board");
        holder.innerHTML = '';
        let table = document.createElement('table');
        table.className = "board";
        holder.appendChild(table);
        let length = arena.length;
        let heigth = arena[0].length;
        for (var y=0; y < heigth; y++ ) {
            let line = document.createElement('tr');
            line.className = "board";
            for (var x=0; x < length; x++ ) {
                let cell = document.createElement('td');
                cell.className = "board";
                if (arena[x][y] != "") {
                    let player = document.createElement('div');
                    player.className = "player"
                    let icon = document.createElement('span');
                    let text = document.createElement('span');

                    let data = arena[x][y].split("/");
                    let name = data[0];
                    let role = data[1];
                    let status = data[2];
                    if (role == "H") {
                        if (state == 3) {
                            icon.className="em em-skull logo";
                        } else {
                            icon.className="em em-vampire logo";
                        }
                    } else {
                        if (status == "S") {
                            icon.className="em em-innocent logo";
                        } else if (status == "F") {
                            icon.className="em em-scream logo";
                        } else {
                            if (state == 3) {
                                icon.className="em em-innocent logo";
                            } else {
                                icon.className="em em-smiley logo";
                            }
                        }
                    }
                    text.innerHTML = "<br>"+name;
                    player.appendChild(icon);
                    player.appendChild(text);
                    cell.appendChild(player);
                }
                line.appendChild(cell);
            }
            table.appendChild(line);
        }
        let rankingNode = document.getElementById("Ranking");
        rankingNode.innerHTML = ""
        var ul = rankingNode.appendChild(document.createElement('ul'));
        for (var i in ranking) {
            var li = document.createElement('li')
            ul.appendChild(li);
            li.innerHTML = ranking[i]
        }
    }
}

let viewer = new GameViewer();

function refreshView() {
    viewer.fetchData()
}

setInterval(refreshView, 1000);
console.log("JS script is loaded");
