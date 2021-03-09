class GameAdminViewer {

    constructor() {
        this.serverSocketUrl = "ws://"+self.location.host.split(":")[0]+":8087"
        this.socket = new WebSocket(this.serverSocketUrl)
        this.connected = false
        let that = this
        this.socket.onopen = function() {
            that.connected = true
        }
        this.socket.onmessage = function(event) {
            var data = JSON.parse(event.data)
            var mode = data["mode"]
            var cur_step = data["CurServerStep"]
            var cur_game = data["CurGameStatus"]
            console.log(cur_step)
            var changed = that.cur_mode != mode
            that.cur_mode = mode
            that.cur_step = cur_step
            that.cur_game = cur_game
            if (changed) {
                that.cur_step = "stopped"
                let nextStepNode = document.getElementById("NextStep");
                nextStepNode.innerHTML = "Start"
            }
            let modeNode = document.getElementById("CurrentMode");
            let stepNode = document.getElementById("CurrentStep");
            let gameNode = document.getElementById("CurrentGame");
            modeNode.innerHTML = "Mode : "+that.cur_mode
            stepNode.innerHTML = "Step : "+that.cur_step
            gameNode.innerHTML = "Game : "+that.cur_game
        }
        this.cur_mode = "demo"
        this.cur_step = "stopped"
        this.cur_game = "none"
    }

    fetchData() {
        if (this.connected) {
            this.socket.send("getServerView")
        }
    }

    sendCmd(cmd) {
        if (this.connected) {
            this.socket.send(cmd)
        }
    }

    nextStep() {
        if (this.connected) {
            let nextStepNode = document.getElementById("NextStep");
            var nextStepName = "Undef"
            var cmd = "Undef"
            if (this.cur_mode == "tournament") {
                if(this.cur_step == "stopped") {
                    nextStepName = "close subscription"
                    cmd = "startTournament"
                } else if (this.cur_step == "subscription") {
                    nextStepName = "Launch"
                    cmd = "closeSubs"
                } else {
                    nextStepName = "Start next game"
                    cmd = "startNextGame"
                }
            } else {
                if(this.cur_step == "stopped") {
                    if (this.cur_mode == "demo") {
                        nextStepName = "Stop"
                    } else {
                        nextStepName = "Run"
                    }
                    if (this.cur_mode == "match") {
                        cmd = "startMatch"
                    } else {
                        cmd = "startPG"
                    }
                } else if(this.cur_step == "pending") {
                    nextStepName = "Stop"
                    cmd = "startNextGame"
                } else {
                    nextStepName = "Start"
                    cmd = "stopPG"
                }
            }
            nextStepNode.innerHTML = nextStepName
            this.socket.send(cmd)
        }
    }
}

let viewer = new GameAdminViewer();

function refreshView() {
    viewer.fetchData()
}

function sendCmd(cmd) {
    viewer.sendCmd(cmd)
}

function nextStep() {
    viewer.nextStep()
}

setInterval(refreshView, 1000);
console.log("JS script is loaded");
