import numpy as np

from game.player import *
from math import floor
from math import ceil

# Return pseudo gaussian kernel matrix
def __gauss_kern(length=5, sigma=1.):

    ax = np.linspace(-(length - 1) / 2., (length - 1) / 2., length)
    xx, yy = np.meshgrid(ax, ax)

    kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))

    return kernel / np.sum(kernel)

def __get_my_pos(name, board):
    for x in range(len(board)):
        for y in range(len(board[0])): #strange that it is not row-major
            if board[x][y] is not None:
                if board[x][y].name == name:
                    return (x, y)
    return None

def __get_hunter_pos(board):
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] is not None and board[x][y].role == Role.HUNTER:
                return (x, y)
    return None

def __get_players_pos(board, my_pos):
    players = []
    for x in range(len(board)):
        for y in range(len(board[0])):
            if my_pos == (x,y):
                continue
            if board[x][y] is not None and board[x][y].role != Role.HUNTER:
                players.append((x, y))
    return players

def __add_with_offset(a, b, offset):
    """a.shape >=  b.shape must be True"""

    #print("__add_with_offset {} {} {}".format(a.shape, b.shape, offset))

    A = np.zeros((a.shape[0] * 3, a.shape[1] * 3))
    B = np.zeros((a.shape[0] * 3, a.shape[1] * 3))
    
    A_slice_x = slice(a.shape[0], 2*a.shape[0])
    A_slice_y = slice(a.shape[1], 2*a.shape[1])
    #print("__add_with_offset A_x {}".format(A_slice_x))
    #print("__add_with_offset A_y {}".format(A_slice_y))

    B_slice_x = slice(a.shape[0] + int(offset[0]), a.shape[0] + b.shape[0]+int(offset[0]))
    B_slice_y = slice(a.shape[1] + int(offset[1]), a.shape[1] + b.shape[1]+int(offset[1]))
    #print("__add_with_offset B_x {}".format(B_slice_x))
    #print("__add_with_offset B_y {}".format(B_slice_y))

    # mmh numpy is row-major, but let's just keep the convention
    A[A_slice_x, A_slice_y] += a
    B[B_slice_x, B_slice_y] += b
    A += B

    return np.array(A[A_slice_x, A_slice_y], copy=True)
    

def get_clever_move(name, board):
    my_pos = __get_my_pos(name, board)
    if my_pos is None:
        print("can't get position!")
        return ""
    
    my_role = board[my_pos[0]][my_pos[1]].role
    imHunter = my_role == Role.HUNTER
    ht_pos = __get_hunter_pos(board)
    ps_pos = __get_players_pos(board, my_pos)

    np_board = np.zeros((len(board), len(board[0])))
    min_len = min(len(board), len(board[0])) # I do hope the board will STAY SQUARE
    len_kfilter = min_len - int(min_len % 2 == 0) #stay odd
    half_len = (len_kfilter + 1) / 2

    kfilter = __gauss_kern(length=len_kfilter) * 100

    moves = [("UP", my_pos[0], my_pos[1] - 1),
             ("DOWN", my_pos[0], my_pos[1] + 1),
             ("LEFT", my_pos[0] - 1, my_pos[1]),
             ("RIGHT", my_pos[0] + 1, my_pos[1])]

    #deletes impossible moves
    moves = [move for move in moves if move[1] >= 0 and move[2] >= 0 and move[1] < len(board) and move[2] < len(board[0])]

    direction=""

    if not imHunter:
        # Then run away
        #print("I'm player!")

        corners = [(-half_len + 1 , -half_len + 1),
                   (-half_len + 1, half_len), 
                   (half_len, -half_len + 1),
                   (half_len, half_len)]
        #print(corners)

        # Apply kfilter around corners
        i = 0
        for corner in corners:
                np_board = __add_with_offset(np_board, kfilter * 1.2, corner)
                i += 1
        np_board /= float(i)
       
        # no hunter when pending
        if ht_pos is None:
            return direction
        # Apply kfilter around hunter pos

        off_x = ht_pos[0] - half_len + 1
        off_y = ht_pos[1] - half_len + 1
        np_board = __add_with_offset(np_board, kfilter, (off_x, off_y))
        np_board += np.random.randn(*np_board.shape) #avoid stagnation
        #print(np_board)

        # get the move on which the calculated value is the lowest
        direction = sorted(moves, key=lambda move: np_board[move[1], move[2]])[0][0]
        #print(direction)
    else:
        #print("I'm hunter!")

        # Go to highest value
        #direction = sorted(moves, key=lambda move: np_board[move[1], move[2]], reverse=True)[0][0]
        distance = lambda A, B : abs(A[0] - B[0]) + abs(A[1] - B[1])
        direction = sorted(moves, key=lambda move: min([distance(move[1:], p) for p in ps_pos]))[0][0]
        #print(direction)

    return direction







