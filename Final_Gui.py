import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

ai_team = 'A'
ai_depth = 3
human_team = 'D'
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

selected = None
valid_moves = []
drag_piece = None

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
        (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
        (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
        (9, 5),
        (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
        (5, 1),
        (3, 10), (4, 10), (5, 10), (6, 10), (7, 10),
        (5, 9)
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
    captured_list = []

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
                    captured_list.append((victim_r, victim_c, victim_cell))
                    board[victim_r][victim_c] = E
    return captured_list


def make_move(board, start, end):
    r1, c1 = start
    r2, c2 = end
    cell = board[r1][c1]
    captured_pieces = []
    board[r2][c2] = cell
    board[r1][c1] = E

    captured_pieces= captured(board, r2, c2, cell)
    return captured_pieces

def undo_move(board, start, end, captured_pieces, original_cell_at_end):
    r1, c1 = start
    r2, c2 = end

    board[r1][c1] = board[r2][c2]
    board[r2][c2] = original_cell_at_end
    for r, c, p in captured_pieces:
        board[r][c] = p

def is_my_piece(piece_char, team):
    if team == 'A':
        return piece_char == 'A'
    else:
        return piece_char == 'D' or piece_char == 'K'

def alpha_beta(board, depth, alpha, beta, maxPlayer, team):
    winner = check_win(board)
    if winner:
        base_score = 10000 if winner == 'D' else -10000
        return base_score + depth if winner == 'D' else base_score - depth, None

    if depth == 0:
        return utility_function(board, team), None

    ai_team = team
    human_team = 'D' if ai_team == 'A' else 'A'
    best_move = None

    if maxPlayer:
        maxEval = -float('inf')
        for r in range(SIZE):
            for c in range(SIZE):
                if is_my_piece(board[r][c], ai_team):
                    for move in valid_move(board, r, c):
                        original_end_cell = board[move[0]][move[1]]
                        captured_list = make_move(board, (r, c), move)

                        eval, _ = alpha_beta(board, depth - 1, alpha, beta, False, team)

                        undo_move(board, (r, c), move, captured_list, original_end_cell)

                        if eval > maxEval:
                            maxEval = eval
                            best_move = ((r, c), move)
                        alpha = max(alpha, eval)
                        if beta <= alpha: break
            if beta <= alpha: break
        return maxEval, best_move
    else:
        minEval = float('inf')
        for r in range(SIZE):
            for c in range(SIZE):
                if is_my_piece(board[r][c], human_team):
                    for move in valid_move(board, r, c):
                        original_end_cell = board[move[0]][move[1]]
                        captured_list = make_move(board, (r, c), move)

                        eval, _ = alpha_beta(board, depth - 1, alpha, beta,True, team)

                        undo_move(board, (r, c), move, captured_list, original_end_cell)

                        if eval < minEval:
                            minEval = eval
                            best_move = ((r, c), move)
                        beta= min(beta, eval)
                        if beta <= alpha: break
            if beta <= alpha: break
        return minEval, best_move


def utility_function(board, ai_team):
    score = 0
    king_pos = None
    attackers = 0
    defenders = 0

    for r in range(SIZE):
        for c in range(SIZE):
            piece = board[r][c]
            if piece == K:
                king_pos = (r, c)
            elif piece == D:
                defenders += 1
            elif piece == A:
                attackers += 1

    if king_pos is None:
        score = -10000
    else:
        kr, kc = king_pos
        if (kr, kc) in corners:
            score = 20000
        else:
            score += (defenders * 20) - (attackers * 10)
            dist = min([abs(kr - x) + abs(kc - y) for x, y in corners])
            score += (20 - dist) * 50

            danger = 0
            for dr, dc in DIRECTIONS:
                nr, nc = kr + dr, kc + dc
                if inside_board(nr, nc) and board[nr][nc] == A:
                    danger += 1

            score -= danger * 100

    if ai_team == 'A':
        return -score
    else:
        return score

def game_settings():
    print("Welcome to Hnefatafl!")
    human_team = ""
    while human_team not in ['A', 'D']:
        human_team = input("Choose Team: Attackers (A) or Defenders (D): ").upper()
    difficulty = ""
    while difficulty not in ['E', 'M', 'H']:
        difficulty = input("Choose Difficulty: Easy (E), Medium (M), Hard (H): ").upper()

    depth_map = {'E': 1, 'M': 2, 'H': 4}
    depth = depth_map.get(difficulty, 1)
    ai_team = 'D' if human_team == 'A' else 'A'

    return human_team, ai_team, depth

def check_win(board):
    king_r, king_c = None, None
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == K:
                king_r, king_c = r, c
                break
        if king_r is not None:
            break

    if king_r is None:
        return False

    if (king_r, king_c) in corners:
        return 'D'

    blocked_sides = 0
    if king_r - 1 < 0 or board[king_r - 1][king_c] == A: blocked_sides += 1
    if king_r + 1 >= SIZE or board[king_r + 1][king_c] == A: blocked_sides += 1
    if king_c - 1 < 0 or board[king_r][king_c - 1] == A: blocked_sides += 1
    if king_c + 1 >= SIZE or board[king_r][king_c + 1] == A: blocked_sides += 1

    if blocked_sides == 4:
        return 'A'

    return False

def AI_turn(board, depth, team):
    print(f"AI ({team}) is thinking...")
    _, best_move = alpha_beta(board, depth, -float('inf'), float('inf'), True, team)

    if best_move:
        start, end = best_move
        print(f"AI moved from {start} to {end}")
        make_move(board, start, end)
    else:
        print("AI has no legal moves!")

# def human_turn(board, team):
#     is_valid_move = False
#     while not is_valid_move:
#         try:
#             start_cell = input(f"[{team}] Select piece:row,col")
#             end_cell = input(f"[{team}] Select destination:row,col")
#             start_r, start_c = map(int, start_cell.split(','))
#             end_r, end_c = map(int, end_cell.split(','))
#
#             if not inside_board(start_r, start_c) or not inside_board(end_r, end_c):
#                 print("ERROR: Cell out of board.")
#                 continue
#
#             piece = board[start_r][start_c]
#             if (team == A and piece != A) or (team == D and piece not in [D, K]):
#                 print("ERROR: select your own piece!")
#                 continue
#
#             possible_moves = valid_move(board, start_r, start_c)
#             if (end_r, end_c) in possible_moves:
#                 make_move(board, (start_r, start_c), (end_r, end_c))
#                 is_valid_move = True
#             else:
#                 print("ERROR: Invalid move.")
#                 continue
#         except ValueError:
#             print("ERROR: Invalid format use numbers separated by a comma.")

# def play_game():
#     board = create_board()
#     human_T, ai_T, ai_depth = game_settings()
#
#     current_turn = 'A'
#     game_running = True
#
#     while game_running:
#         print_board(board)
#         print(f"--- Turn: {'Attackers' if current_turn == 'A' else 'Defenders'} ---")
#
#         if current_turn == human_T:
#             human_turn(board, human_T)
#         else:
#             AI_turn(board,ai_depth,ai_T)
#             pass
#
#         winner = check_win(board)
#         if winner:
#             print_board(board)
#             print(f"\nVictory for the {'Attackers' if winner == 'A' else 'Defenders'}!")
#             game_running = False
#         else:
#             current_turn = 'D' if current_turn == 'A' else 'A'


def draw_pieces():
    for row in range(SIZE):
        for col in range(SIZE):
            if selected and (row, col) == selected and drag_piece is not None:
                continue
            piece = board[row][col]
            x_center = col * CELL_SIZE + CELL_SIZE // 2
            y_center = row * CELL_SIZE + CELL_SIZE // 2
            if piece == A:
                canvas.create_image(x_center, y_center, image=attacker_img)
            elif piece == D:
                canvas.create_image(x_center, y_center, image=defender_img)
            elif piece == K:
                canvas.create_image(x_center, y_center, image=king_img)


def draw_board(board):
    canvas.delete("all")

    for r in range(SIZE):
        for c in range(SIZE):
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE

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

    draw_pieces()


def highlight_moves(moves, sel):
    r, c = sel
    canvas.create_rectangle(
        c * CELL_SIZE, r * CELL_SIZE,
        c * CELL_SIZE + CELL_SIZE, r * CELL_SIZE + CELL_SIZE,
        fill="#ffff00", outline="#b8860b"
    )

    for r, c in moves:
        canvas.create_rectangle(
            c * CELL_SIZE, r * CELL_SIZE,
            c * CELL_SIZE + CELL_SIZE, r * CELL_SIZE + CELL_SIZE,
            fill="#90EE90", outline="#b8860b"
        )

    draw_pieces()


def on_press(event):
    global selected, valid_moves, drag_piece
    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE

    if not inside_board(row, col):
        return

    piece = board[row][col]

    # السطر السحري اللي كان ناقص:
    # بنشيك لو المربع مش فاضي وهل القطعة دي فعلاً تبع فريق الإنسان (human_team)
    if piece != E and is_my_piece(piece, human_team):
        selected = (row, col)
        drag_piece = piece
        valid_moves = valid_move(board, row, col)
        draw_board(board)
        highlight_moves(valid_moves, selected)
    else:
        # لو حاول يحرك قطعة مش بتاعته، بنصفر الاختيار
        selected = None
        drag_piece = None


def on_drag(event):
    if selected is None:
        return
    draw_board(board)
    highlight_moves(valid_moves, selected)
    if drag_piece == A:
        img = attacker_img
    elif drag_piece == D:
        img = defender_img
    elif drag_piece == K:
        img = king_img
    else:
        return
    canvas.create_image(event.x, event.y, image=img)

def call_ai():
    AI_turn(board, ai_depth, ai_team)
    draw_board(board)
    winner = check_win(board)
    if winner:
        messagebox.showinfo("Game Over", f" Game over, {'Attackers' if winner == 'A' else 'Defenders'} win!")
        root.destroy()


def on_release(event):
    global selected, valid_moves, drag_piece
    if selected is None: return
    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE

    if inside_board(row, col) and (row, col) in valid_moves:
        make_move(board, selected, (row, col))
        draw_board(board)

        winner = check_win(board)
        if winner:
            messagebox.showinfo("Game Over", f" Game over, {'Attackers' if winner == 'A' else 'Defenders'} win!")
            root.destroy()
        else:
            root.after(1000, lambda: call_ai())

    selected = None
    valid_moves = []
    drag_piece = None
    draw_board(board)


def main():
    global board, ai_team, ai_depth, human_team

    human_team, ai_team, ai_depth = game_settings()

    board = create_board()
    draw_board(board)

    if ai_team == 'A':
        call_ai()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.mainloop()


if __name__ == "__main__":
    main()