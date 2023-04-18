from typing import Optional
import pygame


COLOURS = {'red': (255, 0, 0),
           'orange': (240, 127, 14),
           'yellow': (255, 255, 0),
           'lime': (0, 255, 0),
           'green': (10, 87, 10),
           'blue': (2, 145, 247),
           'indigo': (33, 11, 133),
           'purple': (82, 1, 143),
           'magenta': (117, 1, 117),
           'white': (255, 255, 255)}
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

# Default values: 50, 6, 7 (size of a classic Connect 4 game board)
# Greater values are not advised - this is your warning!
COIN_RADIUS = 50
ROWS, COLUMNS = 6, 7

WIDTH = (COIN_RADIUS + 1) * (COLUMNS + 2) * 2
HEIGHT = (COIN_RADIUS + 1) * (ROWS + 2) * 2


class InvalidValueError(Exception):
    """An error raised when any of selected values for the coin radius or the
    number of row and columns in a Connect 4 game are invalid.
    """
    def __init__(self, radius: int, rows: int, cols: int) -> None:
        message = ''
        if radius <= 0:
            message += 'Please enter a value for the coin radius that is ' \
                       'greater than 0. '
        if rows <= 0:
            message += 'Please enter a value for the number of rows that is ' \
                       'greater than 0. '
        if cols <= 0:
            message += 'Please enter a value for the number of columns that ' \
                       'is greater than 0. '
        super().__init__(message)


class Coin:
    """A coin in a Connect 4 game.

    Attributes:
        row: The row that this coin has been placed in the board.
        col: The column that this coin has been placed in the board.
        x_pos: The x-coordinate of this coin on the board visualization.
            This x-coordinate corresponds to the center of the coin.
        y_pos: The y-coordinate of this coin on the board visualization.
            This y-coordinate corresponds to the center of the coin.
        colour: The colour of this coin. If a player has not played this coin,
            it is a gray coin by default.

    Representation Invariants:
        0 <= row < ROWS
        0 <= col < COLUMNS
        x_pos is a valid coordinate of the visualization.
        y_pos is a valid coordinate of the visualization.
        colour is a valid tuple representing an RGB colour, i.e. each integer
            is between 0 and 255 inclusive.
        colour != (0, 0, 0) (colour is not black)
    """
    row: int
    col: int
    x_pos: int
    y_pos: int
    colour: tuple[int, int, int]
    placed: bool

    def __init__(self, row: int, column: int, x: int, y: int) -> None:
        """Create a new Coin on a Connect 4 board situated at the given row and
        column, and located at (x, y) in the board visualization. By default,
        this coin has not been placed.

        Preconditions:
            0 <= row < ROWS
            0 <= column < COLUMNS
            x is a valid coordinate of the visualization.
            y is a valid coordinate of the visualization.
        """
        self.row = row
        self.col = column
        self.x_pos = x
        self.y_pos = y
        self.colour = GRAY
        self.placed = False

    def place(self, colour: tuple[int, int, int]) -> None:
        """Record that this coin has been placed.
        """
        self.placed = True
        self.colour = colour


class Player:
    """A player in the Connect 4 game.

    Attributes:
        name: The name of this player.
        colour: The colour of this player's coins.
        _moves: All coin moves made by this player.

    Representation Invariants:
        colour is a valid tuple representing an RGB colour, i.e. each integer
            is between 0 and 255 inclusive.
        colour != (0, 0, 0) (colour is not black)
        colour != (128, 128, 128) (colour is not gray)
        For every list in _moves, len(_moves) <= 8.
        Every tuple in moves (including both keys and values) is a valid
        (col, row) configuration of the Connect4 board.

    """
    name: str
    colour: tuple[int, int, int]
    _moves: dict[tuple[int, int], list[tuple[int, int]]]

    def __init__(self, player_name: str, colour: str) -> None:
        """Create a new player in a Connect 4 game. This player has initially
        made no moves.

        Preconditions:
            colour is a key in the COLOURS dict.
        """
        self.name = player_name
        self.colour = COLOURS[colour]
        self._moves = {}

    def place_coin(self, coin: Coin) -> None:
        """Record that self has placed this coin in the board.
        """
        cx, cy = coin.col, coin.row
        coin_moves = []
        for x, y in self._moves:
            if x in (cx - 1, cx, cx + 1) and y in (cy - 1, cy, cy + 1):
                self._moves[(x, y)].append((cx, cy))
                coin_moves.append((x, y))
        self._moves[(cx, cy)] = coin_moves

    def has_win(self, coin: Coin) -> bool:
        """Return True iff placing this coin is a win for self. A win means that
        this coin successfully connects at least 4 of player's coins.

        Preconditions:
            coin has already been updated in this player's moves.
        """
        cx, cy = coin.col, coin.row
        connected_moves = self._moves[(cx, cy)]
        for x, y in connected_moves:
            x_diff, y_diff = x - cx, y - cy
            length = 2
            move = (x, y)
            while (move[0] + x_diff, move[1] + y_diff) in self._moves[move]:
                length += 1
                move = (move[0] + x_diff, move[1] + y_diff)
            move = (cx, cy)
            while (move[0] - x_diff, move[1] - y_diff) in self._moves[move]:
                length += 1
                move = (move[0] - x_diff, move[1] - y_diff)
            if length >= 53:
                return True
        return False


class Board:
    """A board for a Connect4 game.

    Attributes:
        coins: All coins that are in this board.
        col_ranges: The pixel ranges of each column in the visualization of this
            board.

    Representation Invariants:
        There are COLUMNS lists in coins, with ROWS coins in each of these
            lists. A coin is accessed using coins[col][row], where
            0 <= col <= COLUMNS and 0 <= row < ROWS.
        Every range in col_ranges is equal. There are exactly COLUMNS ranges,
            each corresponding to their ordered column in coins.
    """
    coins: list[list[Coin]]
    col_ranges: list[range]

    def __init__(self) -> None:
        """Initialize a new Connect4 board with no placed coins.
        """
        self.coins = []
        self.col_ranges = []
        square = (COIN_RADIUS + 1) * 2
        for col in range(COLUMNS):
            col_range = range((col + 1) * square, (col + 2) * square)
            self.col_ranges.append(col_range)
            column = []
            x = (col + 1) * square + (square // 2)
            for row in range(ROWS):
                y = (row + 1) * square + (square // 2)
                column.append(Coin(row, col, x, y))
            self.coins.append(column)

    def place_coin(self, player: Player, pos: tuple[int, int]) -> \
            Optional[Coin]:
        """Place a coin by player in the column corresponding to pos iff pos
        belongs to a column, and the column is not already full (a column is
        full when all possible places to place coins have been filled). If a
        coin has been successfully placed, return the coin. Else, do nothing.

        Preconditions:
            There are spaces available to place a coin.
        """
        col = 0
        while col < COLUMNS and pos[0] not in self.col_ranges[col]:
            col += 1
        if col == COLUMNS:
            return
        column = self.coins[col]
        row = ROWS - 1
        coin = column[row]
        while row > -1 and coin.placed:
            row -= 1
            coin = column[row]
        if row == -1:
            return
        coin.place(player.colour)
        player.place_coin(coin)
        return coin


class Connect4:
    """A Connect4 game.

    Attributes:
        board: The board on which the game is played.
        players: The two players playing this game of Connect4.
        screen: The pygame screen on which the board is visualized.

    Representation Invariants:
        screen.get_width() / screen.get_height()
            == (COLUMNS + 2) / (ROWS + 2)
        len(players) == 2
    """
    board: Board
    players: tuple[Player, Player]
    screen: pygame.Surface

    def __init__(self, board: Board, players: tuple[Player, Player],
                 screen: pygame.Surface) -> None:
        """Create a new game of Connect4.

        Preconditions:
            screen.get_width() / screen.get_height()
                == (COLUMNS + 2) / (ROWS + 2)
            pygame has been initialized.
        """
        self.board = board
        self.players = players
        self.screen = screen

    def play(self) -> None:
        """Play a game of Connect4.
        """
        self._update_board()
        self._event_loop()

    def _update_board(self, coin: Coin = None) -> None:
        """Update this board after coin has been placed. If a coin is not
        specified, update the entire board.
        """
        if coin:
            pygame.draw.circle(self.screen, coin.colour,
                               (coin.x_pos, coin.y_pos), COIN_RADIUS)
        else:
            pygame.draw.rect(self.screen, BLACK,
                             (0, 0, self.screen.get_width(),
                              self.screen.get_height()))
            for col in self.board.coins:
                for coin in col:
                    pygame.draw.circle(self.screen, coin.colour,
                                       (coin.x_pos, coin.y_pos), COIN_RADIUS)
        pygame.display.flip()

    def _event_loop(self) -> None:
        """Begin an event loop for player moves in this game of Connect4.
        """
        cur_player = 0
        moves_made = 0
        while True:
            player = self.players[cur_player]
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                end_message = 'The game has been closed!'
                break
            if event.type == pygame.MOUSEBUTTONUP:
                coin = self.board.place_coin(player, event.pos)
                if coin:
                    self._update_board(coin)
                    if player.has_win(coin):
                        end_message = f'Player {player.name} wins the game!'
                        break
                    moves_made += 1
                    if moves_made == COLUMNS * ROWS:
                        end_message = 'The game ends in a tragic tie!'
                        break
                    cur_player = not cur_player
                else:
                    print('Please place your coin in a valid column!')
        print(end_message)


def get_player(id_num: int, colours: list[str]) -> Player:
    """Receive input from the user about their player name and colour and return
    a Player object with the user's input information, removing their chosen
    colour from colours.
    """
    name = input(f'Player {id_num} - Please type your name: ')
    colour = input(f'Choose a colour from \n{colours}: ')
    while colour not in colours:
        colour = input(f'Please choose a valid colour from '
                       f'\n{colours}: ')
    colours.remove(colour)
    return Player(name, colour)


if __name__ == '__main__':
    print('~~~~~~ WELCOME TO CONNECT4! ~~~~~~~')
    if not (COIN_RADIUS > 0 and ROWS > 0 and COLUMNS > 0):
        raise InvalidValueError(COIN_RADIUS, ROWS, COLUMNS)
    available_colours = list(COLOURS.keys())
    game_players = (get_player(1, available_colours),
                    get_player(2, available_colours))
    print('The game has opened...')

    pygame.init()
    game_screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    game_board = Board()
    game = Connect4(game_board, game_players, game_screen)
    game.play()
