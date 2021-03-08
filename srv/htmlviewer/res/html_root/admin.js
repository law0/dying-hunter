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
            var changed = that.cur_mode != data
            that.cur_mode = data
            if (changed) {
                that.cur_step = "stopped"
                let nextStepNode = document.getElementById("NextStep");
                nextStepNode.innerHTML = "Start"
            }
            let modeNode = document.getElementById("CurrentMode");
            let stepNode = document.getElementById("CurrentStep");
            modeNode.innerHTML = "Mode : "+that.cur_mode
            stepNode.innerHTML = "Step : "+that.cur_step
        }
        this.cur_mode = "demo"
        this.cur_step = "stopped"
    }

    fetchData() {
        if (this.connected) {
            this.socket.send("getMode")
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
                    this.cur_step = "subscription"
                    nextStepName = "close subscription"
                    cmd = "startTournament"
                } else if (this.cur_step == "subscription") {
                    this.cur_step = "running"
                    nextStepName = "Launch"
                    cmd = "closeSubs"
                } else {
                    this.cur_step = "running"
                    nextStepName = "Start next game"
                    cmd = "startNextGame"
                }
            } else {
                if(this.cur_step == "stopped") {
                    if (this.cur_mode == "demo") {
                        this.cur_step = "started"
                        nextStepName = "Stop"
                    } else {
                        this.cur_step = "pending"
                        nextStepName = "Run"
                    }
                    cmd = "startPG"
                } else if(this.cur_step == "pending") {
                    this.cur_step = "started"
                    nextStepName = "Stop"
                    cmd = "startNextGame"
                } else {
                    this.cur_step = "stopped"
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
