

E = '.'
A = 'A'
D = 'D'
K  = 'K'
SIZE = 11
mid = int(SIZE/2)
throne = (mid, mid)
corners = [(0,0), (0,10), (10,0), (10,10)]


def create_board():
    board = [[E for _ in range(SIZE)] for _ in range(SIZE)]
     
    

    board[mid][mid] = K

    defenders = [
        (5,4),(5,6),(4,5),(6,5),
        (5,3),(5,7),(3,5),(7,5),
        (4,4),(4,6),(6,4),(6,6)
    ]

    for x, y in defenders:
        board[x][y] = D

    attackers = [
        (0,3),(0,4),(0,5),(0,6),(0,7),
        (1,5),
        (10,3),(10,4),(10,5),(10,6),(10,7),
        (9,5),
        (3,0),(4,0),(5,0),(6,0),(7,0),
        (5,1),
        (3,10),(4,10),(5,10),(6,10),(7,10),
        (5,9)
    ]

    for x, y in attackers:
        board[x][y] = A

    return board


def print_board(board):
    for row in board:
        print(' '.join(row))
    


board = create_board()
print_board(board)
print("Throne:", throne)
print("Corners:", corners)

