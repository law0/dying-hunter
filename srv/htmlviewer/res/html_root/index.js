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
        if (playerList.length > 0) {
            let ol = playerDiv.appendChild(document.createElement('ol'));
            for (var i=0; i < playerList.length; i++ ) {
                let name = playerList[i][0]
                let score = playerList[i][1]
                let li = document.createElement('li')
                ol.appendChild(li);
                li.innerHTML = name+" - "+score+" pts"
            }
        } else {
            playerDiv.innerHTML = "No players for the moment"
        }
        let matchsDiv = document.getElementById("MatchsDiv")
        let matchsList = data["Matchs"]
        matchsDiv.innerHTML = ""
        if (matchsList.length > 0) {
            let ol = matchsDiv.appendChild(document.createElement('ol'));
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
                var img = document.createElement('img')
                img.alt = "View"
                img.src = "./play.png"
                img.width = 15
                img.className ="playImg"
                link.href = "./gameView.html?id="+id
                link.appendChild(img)
                li.appendChild(text)
                li.appendChild(link)
                ol.appendChild(li);
            }
        } else  {
            matchsDiv.innerHTML = "Unavailable until player subscription ended"
        }
    }
}

let viewer = new GameIndexViewer();

function refreshView() {
    viewer.fetchData()
}

setInterval(refreshView, 5000);
console.log("JS script is loaded");
