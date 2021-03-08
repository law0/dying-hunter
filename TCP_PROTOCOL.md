
# Dying hunter TCP protocol

The communication between a client and the server is made using a *TCP* connection.

## Protocol

**The server wait for commands from the client and give response to them.**
The first command of a client should always be a *HELLO*

## Commands

Each command will be *12 char* long messages encoded using *UTF-8*
If the message is not long enough, it should be *padded using space char at the end of the message*
Command name and *parameters* are separated using *':' char*

### Setting up the client
#### HELLO
*Params* :
* name : string with 6 char maximum

This should be the first command received by the server

*Example* : "HELLO:Dummy "

### Playing
#### MOVE
*Params* :
* direction : string with one of the following value : UP, DOWN, LEFT, RIGHT

This command will allow you to move on the board during the game

*Example* : "MOVE:UP     "

#### VIEW
*Params* :
*None*

This command will give you :
- Game state
- Remaining time in this state
- A view of the board

*Example* : "VIEW        "

The server will send a VIEW response

## Responses

### FORMAT

Each commands induce a response from the server
The response is 2 char long and could be :
- *KO* : command was rejected
- *OK* : command was accepted and no data is sent by the server
- *LG* : Data have been sent from the server.

In the case of a *LG* response, then *4 char* will be sent specifying the *length* of the data
Those 4 char could be cast to an integer.
Then the server send the *data*
To finish the server send *OK* to confirm *end of transmission*

### PLAYING

#### VIEW
The service will send a data response to the command VIEW.
The response is a JSON representation of the game.

The record is a JSON map containing the following KEYS:
- *state*: value is the current game state as an integer. The states are the following :
    - *0* for *Pending* : The game is not launched yet. Players are connecting. Nothing else could be done.
    - *1* for *Ready* : the game will be launched in a few ticks. Roles, Player status and position are available. Only view is taken into account.
    - *2* for *Running* : the game is running, each player can move and view the board
    - *3* for *End* : the game is over. Nothing could be done.
    - *4* for *Tournament Subscription room* : no game will be run, this is the room to wait first game of a tournament. Nothing could be done.
- *remainingTicks* : value is the remaining ticks (seconds) in the current game state as an integer
- *board* : value is a 2d array representing the board using strings :
    - An *empty case* is represented using an *empty string*
    - A *player* is represented by *"XXXX/Y/Z"* where :
        - *XXXX* is the *name* of the player
        - *Y* is the role : *"P"* for *prey* or *"H"* for *hunter*
        - *Z* is the status : *"S"* for *safe*, *"N"* for *normal* or *"F"* for *frozen*

*Example* : {"remainingTicks": 0, "state": 0, "board": [["", "", "", "", "", "Faker/P/S"], ["", "", "Dumb/P/S", "", "", "Troll/P/S"], ["Dummy/P/S", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]]}
