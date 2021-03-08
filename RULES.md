# Dying hunter

## Introduction

Dying hunter is a game that is close to wolf game. There is an hunter and preys.
The hunter have to catch a prey. Then the prey become the hunter and the hunter a prey.
The game is time boxed and at the end of the timer the hunter loose.
Then a new hunter is selected and we run the game again until there are a final winner
aka the last prey alive on the board.

## Game

### Description

Dying hunter is a game based on wolf game to create a battle royal game.

The hunter have to catch a prey before the end of a timer.
If he succeed, then the prey become the hunter and the hunter a new prey.
**At the end of the timer the current hunter loose.**


#### Roles

##### Hunter

The hunter need to catch a prey before the end of the round timer.
If he failed, then he loose the game.

If he succeed, then the hunter will be safe for few seconds.

##### Prey

The prey need to run away from the hunter during the whole round.
If he failed, then he will became the hunter and risk to loose the game.

But a prey can freeze an other prey to survive more easily.

Or a prey can reach the hunter if he want to.
Maybe it can be usefull to be safe when the timer hit zero.

#### Status

##### Normal

This is the default status.

##### Safe

This is status means you can't be cautch by the hunter nor frozen by an other prey.
But you can touch the hunter if you want to become the hunter again.

The only mean to become safe if to catch a prey as a hunter.

This status have a timer of 3 table turn.

##### Frozen

This status forbid you to move.

This status is given to a player that was touched by another player.

This status have a timer of 3 table turn.

### Game step by step

#### Setting up a game

Each player start as a safe prey.
We choose randomly who is the first player to be the hunter.
Then we start the first round of the game.
We continue playing round until the last one were there are only two player.

#### Round step by step

A round made by the following steps that repeats until the round timer is over:

- Every player decide to move in a direction (UP, DOWN, LEFT or RIGHT).
- We randomly select player order to move
- If the player is frozen then he stay still
- Else he move in the direction if there is no player already present on this place
- If any player is present then there is a contact
    - No one moves
    - If the player who is moving is the hunter then he catch the other player
    - If the player who is moving touch the hunter then the hunter catch him
    - Otherwise the player who is moving freeze the other player if he is not safe
- To finish if the player is safe or frozen, we decrement the status timer of this player

At the end of the round, the hunter loose.
He is removed from the game and a new hunter is selected randomly.
Then a new round can be started.

#####

## Ranking
If multiple game will be played with the same players then the following rules could be use to give points to each player each games.
This allow to get a global ranking to know who is the winner of the set of games.

At the end of each game, given the rank of each player we give the following point by ranks :
* Nb of player
* Nb of player / 2
* Nb of player / 4
* Nb of player / 8

Etc...

When we reach 2 or less points, following players receive 0 points

Example : given P1 to P8 players :
- P1 - 8 points
- P2 - 4 points
- P3 - 2 points
- P4 - 0 points
- P5 - 0 points
- P6 - 0 points
- P7 - 0 points
- P8 - 0 points
