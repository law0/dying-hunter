# Dying hunter server

The service use the following ports :
- 8086 : web server to view games and control server
- 8087 : web socket communications
- 8082 : game server

Once launched the server is controlable using the following page :
http://localhost:8086/admin.html

This allow to handle playground and it state and tournaments.

The index page is the tournament view :
http://localhost:8086/

And to view a game use the page:
http://localhost:8086/gameView.html?id=0

where id is the id of the game.

In playground and demo mode the ID of the game is always 0
In tournament mode, index give link to all games of the tournament.
