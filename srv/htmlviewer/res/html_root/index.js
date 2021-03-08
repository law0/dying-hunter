class GameIndexViewer {

    constructor() {
        this.serverSocketUrl = "ws://"+self.location.host.split(":")[0]+":8087"
        this.socket = new WebSocket(this.serverSocketUrl)
        this.connected = false
        let that = this
        this.socket.onopen = function() {
            that.connected = true
            that.fetchData()
        }
        this.socket.onmessage = this.handleMessage
    }

    fetchData() {
        if (this.connected) {
            this.socket.send("tournamentSummary")
        }
    }

    handleMessage(event) {
        var data = JSON.parse(event.data)
        let playerDiv = document.getElementById("PlayersDiv")
        let playerList = data["Players"]
        playerDiv.innerHTML = ""
        let ul = playerDiv.appendChild(document.createElement('ul'));
        for (var i=0; i < playerList.length; i++ ) {
            let name = playerList[i][0]
            let score = playerList[i][1]
            let li = document.createElement('li')
            ul.appendChild(li);
            li.innerHTML = name+" - "+score+" pts"
        }
        let matchsDiv = document.getElementById("MatchsDiv")
        let matchsList = data["Matchs"]
        matchsDiv.innerHTML = ""
        ul = matchsDiv.appendChild(document.createElement('ul'));
        for (var i=0; i < matchsList.length; i++ ) {
            let status = matchsList[i][0]
            let winner = matchsList[i][1]
            let id = matchsList[i][2]
            let li = document.createElement('li')
            let link = document.createElement('a')
            let text = document.createElement('span')
            text.innerHTML = "Game "+id
            if (status == "TODO") {
                text.innerHTML += " - Waiting start signal "
            }  else if (status == "RUNNING") {
                text.innerHTML += " - In progress "
            } else {
                text.innerHTML += " - Winner : "+winner+" "
            }
            link.innerHTML = "View"
            link.href = "./gameView.html?id="+id
            li.appendChild(text)
            li.appendChild(link)
            ul.appendChild(li);
        }
    }
}

let viewer = new GameIndexViewer();

function refreshView() {
    viewer.fetchData()
}

setInterval(refreshView, 5000);
console.log("JS script is loaded");
