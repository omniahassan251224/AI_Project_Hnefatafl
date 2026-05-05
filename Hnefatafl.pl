:- use_module(library(lists)).
:- use_module(library(aggregate)).

throne(5,5).
corner(0,0). corner(0,10). corner(10,0). corner(10,10).
directions([(1,0),(-1,0),(0,1),(0,-1)]).

board_get(Board, R, C, Cell) :-
    nth0(R, Board, Row), nth0(C, Row, Cell).

board_set(Board, R, C, Cell, NB) :-
    nth0(R, Board, Row),
    replace_nth(C, Row, Cell, NRow),
    replace_nth(R, Board, NRow, NB).

replace_nth(0, [_|T], X, [X|T]) :- !.
replace_nth(N, [H|T], X, [H|T2]) :-
    N > 0, N1 is N-1, replace_nth(N1, T, X, T2).

empty_row(Row) :- length(Row, 11), maplist(=('.'), Row).

create_board(Board) :-
    length(Tmp, 11), maplist(empty_row, Tmp),
    board_set(Tmp, 5, 5, k, B1),
    foldl(place(d),
      [(5,4),(5,6),(4,5),(6,5),(5,3),(5,7),(3,5),(7,5),(4,4),(4,6),(6,4),(6,6)],
      B1, B2),
    foldl(place(a),
      [(0,3),(0,4),(0,5),(0,6),(0,7),(1,5),
       (10,3),(10,4),(10,5),(10,6),(10,7),(9,5),
       (3,0),(4,0),(5,0),(6,0),(7,0),(5,1),
       (3,10),(4,10),(5,10),(6,10),(7,10),(5,9)],
      B2, Board).

place(Piece, (R,C), B, NB) :- board_set(B, R, C, Piece, NB).

print_board(Board) :-
    format("~n     "),
    forall(between(0,9,I),  format(" ~w  ", [I])),
    format(" ~w~n", [10]),
    format("   +"),
    forall(between(0,10,_), format("----", [])),
    nl,
    forall(between(0,10,R),
        ( nth0(R, Board, Row),
          ( R < 10 -> format(" ~w | ", [R]) ; format("~w | ", [R]) ),
          forall(member(Cell, Row),
              ( Cell = '.' -> format(" .  ", [])
              ; format(" ~w  ", [Cell])
              )),
          nl
        )).

inside_board(R, C) :- R >= 0, R =< 10, C >= 0, C =< 10.
is_special(R, C) :- throne(R, C), !.
is_special(R, C) :- corner(R, C).

valid_moves(Board, R, C, Moves) :-
    board_get(Board, R, C, Cell), Cell \= '.',
    directions(Dirs),
    foldl(slides(Board, R, C, Cell), Dirs, [], Moves).

slides(Board, R, C, Cell, (DR,DC), Acc, Res) :-
    R1 is R+DR, C1 is C+DC,
    slide(Board, R1, C1, DR, DC, Cell, Acc, Res).

slide(Board, R, C, DR, DC, Cell, Acc, Res) :-
    inside_board(R, C),
    board_get(Board, R, C, '.'), !,
    ( is_special(R, C), Cell \= k
    ->  R2 is R+DR, C2 is C+DC,
        slide(Board, R2, C2, DR, DC, Cell, Acc, Res)
    ;   R2 is R+DR, C2 is C+DC,
        slide(Board, R2, C2, DR, DC, Cell, [(R,C)|Acc], Res)
    ).
slide(_, _, _, _, _, _, Acc, Acc).

capture_check(Board, R, C, Cell, Caps, NewBoard) :-
    ( Cell = a -> Opp = d ; Opp = a ),
    directions(Dirs),
    foldl(try_cap(Board, R, C, Cell, Opp), Dirs, [], Caps),
    foldl(rm_piece, Caps, Board, NewBoard).

try_cap(Board, R, C, Cell, Opp, (DR,DC), Acc, Res) :-
    VR is R+DR, VC is C+DC,
    AR is R+2*DR, AC is C+2*DC,
    inside_board(VR, VC), inside_board(AR, AC),
    board_get(Board, VR, VC, Opp),
    Opp \= k,
    board_get(Board, AR, AC, Anc),
    ( Anc = Cell ; (Cell = d, Anc = k) ; corner(AR, AC)
    ; (throne(AR, AC), Anc = '.') ), !,
    Res = [(VR,VC)|Acc].
try_cap(_, _, _, _, _, _, Acc, Acc).

rm_piece((R,C), B, NB) :- board_set(B, R, C, '.', NB).

make_move(Board, (R1,C1), (R2,C2), NewBoard, Caps) :-
    board_get(Board, R1, C1, Cell),
    board_set(Board, R1, C1, '.', B1),
    board_set(B1, R2, C2, Cell, B2),
    capture_check(B2, R2, C2, Cell, Caps, NewBoard).

find_king(Board, KR, KC) :-
    between(0,10,KR), between(0,10,KC),
    board_get(Board, KR, KC, k), !.

check_win(Board, Result) :-
    ( \+ find_king(Board, _, _) -> Result = a
    ; find_king(Board, KR, KC),
      ( corner(KR, KC)   -> Result = d
      ; king_surrounded(Board, KR, KC) -> Result = a
      ; Result = none
      )
    ).

king_surrounded(Board, KR, KC) :-
    directions(Dirs),
    forall(member((DR,DC), Dirs),
       ( NR is KR+DR, NC is KC+DC,
         ( \+ inside_board(NR, NC) -> true
         ; board_get(Board, NR, NC, a)
         )
       )).

count_piece(Board, P, N) :-
    aggregate_all(count,
        (between(0,10,R), between(0,10,C), board_get(Board,R,C,P)), N).

min_corner_dist(KR, KC, D) :-
    findall(X, (corner(CR,CC), X is abs(KR-CR)+abs(KC-CC)), Ds),
    min_list(Ds, D).

danger_adj(Board, KR, KC, Count) :-
    directions(Dirs),
    aggregate_all(count,
        (member((DR,DC), Dirs), NR is KR+DR, NC is KC+DC,
         inside_board(NR,NC), board_get(Board, NR, NC, a)),
        Count).

utility(Board, AITeam, Score) :-
    ( \+ find_king(Board,_,_) -> Raw = -10000
    ; find_king(Board, KR, KC),
      ( corner(KR, KC) -> Raw = 10000
      ; count_piece(Board, d, Defs),
        count_piece(Board, a, Atts),
        min_corner_dist(KR, KC, Dist),
        danger_adj(Board, KR, KC, Danger),
        Raw is Defs*10 - Atts*10 + (20-Dist)*25 - Danger*50
      )
    ),
    ( AITeam = a -> Score is -Raw ; Score = Raw ).

is_my(a, a).
is_my(d, d).
is_my(d, k).

all_moves(Board, Team, Moves) :-
    findall((S,E),
        ( between(0,10,R), between(0,10,C),
          board_get(Board, R, C, Cell),
          is_my(Team, Cell),
          valid_moves(Board, R, C, EL),
          member(E, EL),
          S = (R,C)
        ), Moves).


%% Returns Score and BestMove=(Start,End) or none

alpha_beta(Board, Depth, Alpha, Beta, MaxOrMin, Team, Score, BestMove) :-
    check_win(Board, W),
    ( W \= none
    ->  utility(Board, Team, Score), BestMove = none
    ;   Depth =:= 0
    ->  utility(Board, Team, Score), BestMove = none
    ;   MaxOrMin = max
    ->  ( Team = a -> Opp = d ; Opp = a ),
        all_moves(Board, Team, Moves),
        ( Moves = []
        ->  utility(Board, Team, Score), BestMove = none
        ;   max_loop(Board, Depth, Alpha, Beta, Team, Moves,
                     -1000000, none, Score, BestMove)
        )
    ;   % min
        ( Team = a -> Opp = d ; Opp = a ),
        all_moves(Board, Opp, Moves),
        ( Moves = []
        ->  utility(Board, Team, Score), BestMove = none
        ;   min_loop(Board, Depth, Alpha, Beta, Team, Moves,
                     1000000, none, Score, BestMove)
        )
    ).

max_loop(_, _, Alpha, _, _, [], Alpha, M, Alpha, M).
max_loop(Board, Depth, Alpha, Beta, Team, [(S,E)|Rest],
         CurBest, CurM, OutScore, OutMove) :-
    E = (ER,EC),
    board_get(Board, ER, EC, OrgEnd),
    make_move(Board, S, E, NB, Caps),
    D1 is Depth - 1,
    alpha_beta(NB, D1, Alpha, Beta, min, Team, Score, _),
    % manual undo not needed - we use the original Board for next iterations
    ( Score > CurBest -> NB2 = Score, NM = (S,E) ; NB2 = CurBest, NM = CurM ),
    NAlpha is max(Alpha, NB2),
    ( Beta =< NAlpha
    ->  OutScore = NB2, OutMove = NM
    ;   max_loop(Board, Depth, NAlpha, Beta, Team, Rest, NB2, NM, OutScore, OutMove)
    ).

min_loop(_, _, _, Beta, _, [], Beta, M, Beta, M).
min_loop(Board, Depth, Alpha, Beta, Team, [(S,E)|Rest],
         CurBest, CurM, OutScore, OutMove) :-
    E = (ER,EC),
    board_get(Board, ER, EC, _OrgEnd),
    make_move(Board, S, E, NB, _Caps),
    D1 is Depth - 1,
    alpha_beta(NB, D1, Alpha, Beta, max, Team, Score, _),
    ( Score < CurBest -> NB2 = Score, NM = (S,E) ; NB2 = CurBest, NM = CurM ),
    NBeta is min(Beta, NB2),
    ( NBeta =< Alpha
    ->  OutScore = NB2, OutMove = NM
    ;   min_loop(Board, Depth, Alpha, NBeta, Team, Rest, NB2, NM, OutScore, OutMove)
    ).


read_team(Team) :-
    write('Choose team - type a (Attackers) or d (Defenders): '),
    read_line_to_string(user_input, Line),
    ( Line = "a" -> Team = a
    ; Line = "d" -> Team = d
    ; write('Invalid. Please type a or d'), nl, read_team(Team)
    ).

read_difficulty(Depth) :-
    write('Choose difficulty - type e (Easy), m (Medium), h (Hard): '),
    read_line_to_string(user_input, Line),
    ( Line = "e" -> Depth = 1
    ; Line = "m" -> Depth = 2
    ; Line = "h" -> Depth = 4
    ; write('Invalid. Please type e, m or h'), nl, read_difficulty(Depth)
    ).

read_int(Prompt, N) :-
    write(Prompt),
    read_line_to_string(user_input, Line),
    ( number_string(N, Line), integer(N)
    ->  true
    ;   write('Please enter a whole number.'), nl,
        read_int(Prompt, N)
    ).


human_turn(Board, Team, NewBoard) :-
    read_int('  Piece row: ', R1),
    read_int('  Piece col: ', C1),
    ( \+ inside_board(R1, C1)
    ->  write('  Out of board.'), nl, human_turn(Board, Team, NewBoard)
    ;   board_get(Board, R1, C1, Cell),
        ( \+ is_my(Team, Cell)
        ->  write('  Not your piece!'), nl, human_turn(Board, Team, NewBoard)
        ;   valid_moves(Board, R1, C1, VMs),
            ( VMs = []
            ->  write('  No legal moves for that piece.'), nl,
                human_turn(Board, Team, NewBoard)
            ;   read_int('  Dest  row: ', R2),
                read_int('  Dest  col: ', C2),
                ( member((R2,C2), VMs)
                ->  make_move(Board, (R1,C1), (R2,C2), NewBoard, _)
                ;   write('  Invalid destination.'), nl,
                    human_turn(Board, Team, NewBoard)
                )
            )
        )
    ).

ai_turn(Board, Depth, Team, NewBoard) :-
    format("~nAI (~w) is thinking...~n", [Team]),
    alpha_beta(Board, Depth, -1000000, 1000000, max, Team, _Score, BestMove),
    ( BestMove = (Start, End)
    ->  format("AI moved ~w -> ~w~n", [Start, End]),
        make_move(Board, Start, End, NewBoard, _)
    ;   write("AI has no moves!"), nl, NewBoard = Board
    ).


play_game :-
    write('=== Welcome to Hnefatafl ==='), nl,
    read_team(HumanTeam),
    read_difficulty(Depth),
    ( HumanTeam = a -> AITeam = d ; AITeam = a ),
    create_board(Board),
    game_loop(Board, a, HumanTeam, AITeam, Depth).

game_loop(Board, Turn, HumanTeam, AITeam, Depth) :-
    nl, print_board(Board),
    ( Turn = a -> write('--- Attackers turn ---') ; write('--- Defenders turn ---') ), nl,
    ( Turn = HumanTeam
    ->  format("Your turn (~w). Enter row/col when prompted.~n", [HumanTeam]),
        human_turn(Board, HumanTeam, NewBoard)
    ;   ai_turn(Board, Depth, AITeam, NewBoard)
    ),
    check_win(NewBoard, Winner),
    ( Winner \= none
    ->  nl, print_board(NewBoard),
        ( Winner = a -> write('*** Attackers win! ***') ; write('*** Defenders win! ***') ), nl
    ;   ( Turn = a -> Next = d ; Next = a ),
        game_loop(NewBoard, Next, HumanTeam, AITeam, Depth)
    ).

:- initialization(play_game, main).