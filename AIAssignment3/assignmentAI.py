import tkinter as tk
from PIL import Image, ImageTk

SIZE = 11
CELL_SIZE = 50


E = '.'
A = 'A'
D = 'D'
K  = 'K'
DIRECTIONS = [(1,0),(-1,0),(0,1),(0,-1)]
mid = int(SIZE/2)
throne = (mid, mid)
corners = [(0,0), (0,10), (10,0), (10,10)]
root = tk.Tk()
root.title("Viking Chess - Tafl")  
canvas = tk.Canvas(root, width=SIZE*CELL_SIZE, height=SIZE*CELL_SIZE)
canvas.pack()

attacker_img = Image.open("attacker.png")
attacker_img = attacker_img.resize((40, 40))
attacker_img = ImageTk.PhotoImage(attacker_img)

defender_img = Image.open("defender.png")
defender_img = defender_img.resize((40, 40))
defender_img = ImageTk.PhotoImage(defender_img)

king_img = Image.open("king.png")
king_img = king_img.resize((40, 40))
king_img = ImageTk.PhotoImage(king_img)
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
def inside_board(r, c):
    return 0 <= r < SIZE and 0 <= c < SIZE

def valid_move(board, r, c):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    validmoves = []
    cell = board[r][c]
    
    if cell == E:
        return validmoves
    
    for rd, cd in directions:
        nextrow = r + rd
        nextcol = c + cd
        
        while inside_board(nextrow, nextcol) and board[nextrow][nextcol] == E:
            target = (nextrow, nextcol)
            
            if target == throne or target in corners:
                if cell == K:
                    validmoves.append(target)
            else:
                validmoves.append(target)
            
            nextrow += rd
            nextcol += cd
            
    return validmoves

def captured(board, r, c, cell):
    opponent = A if cell in [D, K] else D
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for rd, cd in directions:
        victim_r, victim_c = r + rd, c + cd
        anchor_r, anchor_c = r + 2 * rd, c + 2 * cd
        
        if inside_board(anchor_r, anchor_c):
            victim_cell = board[victim_r][victim_c]
            anchor_cell = board[anchor_r][anchor_c]
            
            if victim_cell == opponent and victim_cell != K:
                is_trapped = (anchor_cell == cell) or \
                             (anchor_cell == K if cell == D else False) or \
                             ((anchor_r, anchor_c) in corners) or \
                             ((anchor_r, anchor_c) == throne and anchor_cell == E)
                
                if is_trapped:
                    board[victim_r][victim_c] = E

def make_move(board, start, end):
    r1, c1 = start
    r2, c2 = end
    cell = board[r1][c1]
    
    board[r2][c2] = cell
    board[r1][c1] = E
    
    captured(board, r2, c2, cell)
    return board
def utility_function(board):
    score = 0
    king_pos = None
    attackers = 0
    defenders = 0

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == K:
                king_pos = (r,c)
            elif board[r][c] == D:
                defenders += 1
            elif board[r][c] == A:
                attackers += 1

    score += defenders * 2
    score -= attackers * 2

    if king_pos:
        kr,kc = king_pos
        dist = min([abs(kr-x)+abs(kc-y) for x,y in corners])
        score += (SIZE - dist)

        danger = 0
        for dr,dc in DIRECTIONS:
            nr, nc = kr+dr, kc+dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == A:
                danger += 1

        score -= danger * 3

    return score
def draw_board(board):
    canvas.delete("all")

    for r in range(SIZE):
        for c in range(SIZE):

            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x_center = x1 + CELL_SIZE//2
            y_center = y1 + CELL_SIZE//2

            if (r, c) in corners:
                fill_color = "#000000"
            else:
                fill_color = "#ffffff"

            canvas.create_rectangle(
                x1, y1,
                x1 + CELL_SIZE,
                y1 + CELL_SIZE,
                fill=fill_color,
                outline="#b8860b"
            )

            piece = board[r][c]

            if piece == A:
                canvas.create_image(x_center, y_center, image=attacker_img)
            elif piece == D:
                canvas.create_image(x_center, y_center, image=defender_img)
            elif piece == K:
                canvas.create_image(x_center, y_center, image=king_img)
def main():
    global board
    board = create_board()
    draw_board(board)
    root.mainloop()
if __name__ == "__main__":
    main()
