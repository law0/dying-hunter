function getUrlParam(name)
{
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    return urlParams.get(name);
}

class Trainer {

    constructor() {
        this.serverSocketUrl = "ws://"+self.location.host.split(":")[0]+":8087";
        this.socket = new WebSocket(this.serverSocketUrl);
        this.connected = false;
        let that = this
        this.socket.onopen = function() {
            that.connected = true;
        };
        this.socket.onmessage = function(event) {
            let game = JSON.parse(event.data);
            let arena = game["board"];
            let state = game["state"];
            let stateRemainingTicks = game["remainingTicks"];
            let stateNames = ["pending", "round will start in ", "round running, remains ", "game over"];

            if (state == 0) {
                document.getElementById("PreGameControls").className = "center"
                document.getElementById("InGameControls").className = "center hidden"
            } else {
                document.getElementById("PreGameControls").className = "center hidden"
                document.getElementById("InGameControls").className = "center"
            }

            document.getElementById("Status").innerHTML = "Status : "+stateNames[state];
            if (state == 1 || state == 2) {
                document.getElementById("Status").innerHTML += stateRemainingTicks+" ticks";
            }
            let holder = document.getElementById("Board");
            holder.innerHTML = '';
            let table = document.createElement('table');
            table.className = "board";
            holder.appendChild(table);
            let length = arena.length;
            let heigth = arena[0].length;
            let nbPlayerAlive = 0;
            for (var y=0; y < heigth; y++ ) {
                let line = document.createElement('tr');
                line.className = "board";
                for (var x=0; x < length; x++ ) {
                    let cell = document.createElement('td');
                    cell.className = "board";
                    let cellX = x;
                    let cellY = y;
                    if (arena[x][y] != "") {
                        nbPlayerAlive += 1;
                        let player = document.createElement('div');
                        player.className = "player";
                        let icon = document.createElement('span');
                        let text = document.createElement('span');

                        let data = arena[x][y].split("/");
                        let name = data[0];
                        let role = data[1];
                        let status = data[2];
                        if (role == "H") {
                            that.hunter = name
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
                        cell.onclick = function () {
                            if (that.mode == 0)
                            {
                                that.selected = name
                                document.getElementById("SelectedPlayer").innerHTML = name+" is selected"
                                document.getElementById("ModeMove").disabled = false
                                let disabled = (that.selected == that.hunter)
                                document.getElementById("SetHunter").disabled = disabled
                                document.getElementById("SetFrozen").disabled = disabled
                                document.getElementById("SetSafe").disabled = disabled
                                document.getElementById("SetNormal").disabled = disabled
                            } else {
                                if (that.selected != undefined) {
                                    that.socket.send("trainingMove "+that.selected+" "+cellX+" "+cellY);
                                }
                            }
                        }
                    } else {
                        cell.onclick = function () {
                            if (that.mode == 1)
                            {
                                if (that.selected != undefined) {
                                    that.socket.send("trainingMove "+that.selected+" "+cellX+" "+cellY);
                                }
                            }
                        }
                    }
                    line.appendChild(cell);
                }
                table.appendChild(line);
            }
        }
        this.mode = 0; // 0:Selection 1:Move
        this.selected = undefined;
        this.hunter = undefined;
    }

    fetchData() {
        if (this.connected) {
            this.socket.send("viewArena 0");
        }
    }

    addDummy() {
        this.socket.send("addTrainingDummy");
    }

    doTick() {
        this.socket.send("doTrainingTick");
    }

    setMode(mode) {
        this.mode = mode;
        if (this.mode == 0) {
            document.getElementById("ModeSelect").className = "activated"
            document.getElementById("ModeMove").className = ""
        } else {
            document.getElementById("ModeSelect").className = ""
            document.getElementById("ModeMove").className = "activated"
        }
    }

    setHunter() {
        if (this.selected != undefined) {
            this.socket.send("trainingSetHunter "+this.selected);
        }
    }

    setFrozen() {
        if (this.selected != undefined) {
            this.socket.send("trainingSetFrozen "+this.selected);
        }
    }

    setSafe() {
        if (this.selected != undefined) {
            this.socket.send("trainingSetSafe "+this.selected);
        }
    }

    setNormal() {
        if (this.selected != undefined) {
            this.socket.send("trainingSetNormal "+this.selected);
        }
    }

}

let trainer = new Trainer();

function refreshView() {
    trainer.fetchData()
}

function addDummy() {
    trainer.addDummy()
}

function setMode(mode) {
    trainer.setMode(mode)
}

function setHunter() {
    trainer.setHunter()
}

function setFrozen() {
    trainer.setFrozen()
}

function setSafe() {
    trainer.setSafe()
}

function setNormal() {
    trainer.setNormal()
}

function doTick() {
    trainer.doTick()
}

setInterval(refreshView, 1000);
console.log("JS script is loaded");
