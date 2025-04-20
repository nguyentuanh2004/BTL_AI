import pygame
import os
from Board import Board
from Game import Game
from King import King


class Minimax:
    def evaluate(self, board, player_color="pink"):
        """
        Evaluates the quality of the board position for the AI

        The evaluation considers 4 main criteria:
        1. Regular piece count: +10 for own pieces, -10 for opponent pieces
        2. King piece count: +20 for own kings, -20 for opponent kings
        3. Piece position: Bonus for pieces at advantageous positions (edges)
        4. Blocked piece count: -10 for own blocked pieces, +10 for opponent blocked pieces

        Parameters:
        board -- The current board state
        player_color -- The color of the player ("pink" or "blue")

        Returns:
        float -- Score of the board position
        """
        # Determine opponent color
        opponent_color = "blue" if player_color == "pink" else "pink"

        # Initialize score
        score = 0

        # Cell value table for position evaluation - edges are more valuable
        def cellValue(row, col):
            # Preference for edge positions
            if row == 0 or row == 7 or col == 0 or col == 7:
                return 2
            # Second preference for positions near edges
            elif row == 1 or row == 6 or col == 1 or col == 6:
                return 1
            # Neutral value for central positions
            else:
                return 0

        # Count pieces, kings, and evaluate positions
        for tile in board.tile_list:
            piece = tile.occupying_piece
            if piece is not None:
                position_value = cellValue(piece.y, piece.x)
                
                # Evaluate based on piece type and color
                if piece.color == player_color:
                    if piece.notation == 'p':  # Regular piece
                        score += 10
                    else:  # King
                        score += 20
                    
                    # Add position value
                    score += position_value
                    
                    # Check if piece is blocked/cannot move
                    if not piece.valid_moves() and not piece.valid_jumps():
                        score -= 10
                else:  # Opponent pieces
                    if piece.notation == 'p':  # Regular piece
                        score -= 10
                    else:  # King
                        score -= 20
                    
                    # Subtract position value
                    score -= position_value
                    
                    # Check if opponent piece is blocked/cannot move
                    if not piece.valid_moves() and not piece.valid_jumps():
                        score += 10

        return score

    def maxAB(self, board, depth, alpha, beta, player_color):
        """
        Performs the MAX part of the minimax algorithm with alpha-beta pruning

        Parameters:
        board -- Current board state
        depth -- Current depth in the search tree
        alpha -- Alpha value for pruning
        beta -- Beta value for pruning
        player_color -- Color of the player ("pink" or "blue")

        Returns:
        tuple -- (best score, best move, is multi-leg jump possible)
        """
        # Check terminal conditions
        if depth == 0 or self.is_game_over(board):
            return self.evaluate(board, player_color), None, False

        max_eval = float("-inf")
        best_move = None
        best_move_multi_leg = False

        # Get all possible moves
        moves = self.get_all_moves(board, player_color)

        for move, multi_leg in moves:
            # Get evaluation from minimizing player's perspective
            opponent_color = "blue" if player_color == "pink" else "pink"
            evaluation = self.minAB(move, depth - 1, alpha, beta, opponent_color)[0]

            # Update maximum evaluation
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
                best_move_multi_leg = multi_leg

            # Alpha-beta pruning
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break

        return max_eval, best_move, best_move_multi_leg

    def minAB(self, board, depth, alpha, beta, player_color):
        """
        Performs the MIN part of the minimax algorithm with alpha-beta pruning

        Parameters:
        board -- Current board state
        depth -- Current depth in the search tree
        alpha -- Alpha value for pruning
        beta -- Beta value for pruning
        player_color -- Color of the player ("pink" or "blue")

        Returns:
        tuple -- (best score, best move, is multi-leg jump possible)
        """
        # Check terminal conditions
        if depth == 0 or self.is_game_over(board):
            opponent_color = "blue" if player_color == "pink" else "pink"
            return self.evaluate(board, opponent_color), None, False

        min_eval = float("inf")
        best_move = None
        best_move_multi_leg = False

        # Get all possible moves
        moves = self.get_all_moves(board, player_color)

        for move, multi_leg in moves:
            # Get evaluation from maximizing player's perspective
            opponent_color = "blue" if player_color == "pink" else "pink"
            evaluation = self.maxAB(move, depth - 1, alpha, beta, opponent_color)[0]

            # Update minimum evaluation
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
                best_move_multi_leg = multi_leg

            # Alpha-beta pruning
            beta = min(beta, min_eval)
            if beta <= alpha:
                break

        return min_eval, best_move, best_move_multi_leg

    def is_game_over(self, board):
        """
        Checks if the game is over

        Parameters:
        board -- Current board state

        Returns:
        bool -- True if game is over, False otherwise
        """
        # Check if either player has no pieces left
        pink_pieces = 0
        blue_pieces = 0

        for tile in board.tile_list:
            piece = tile.occupying_piece
            if piece is not None:
                if piece.color == "pink":
                    pink_pieces += 1
                else:
                    blue_pieces += 1

        return pink_pieces == 0 or blue_pieces == 0

    def get_all_moves(self, board, player_color):
        """
        Gets all possible moves for a player

        Parameters:
        board -- Current board state
        player_color -- Color of the player ("pink" or "blue")

        Returns:
        list -- List of tuples (board after move, is multi-leg jump possible)
        """
        from copy import deepcopy

        moves = []

        # Check if there are jump moves available (which are mandatory)
        has_jumps = False
        for tile in board.tile_list:
            piece = tile.occupying_piece
            if piece is not None and piece.color == player_color:
                jumps = piece.valid_jumps()
                if jumps:
                    has_jumps = True
                    break

        # Process all pieces of the current player
        for tile in board.tile_list:
            piece = tile.occupying_piece
            if piece is not None and piece.color == player_color:
                # If jumps are available, only consider jump moves
                if has_jumps:
                    jumps = piece.valid_jumps()
                    for jump in jumps:
                        # Create a deep copy of the board to simulate the move
                        temp_board = deepcopy(board)
                        # Get the corresponding piece in the temporary board
                        temp_piece = temp_board.get_tile_from_pos((piece.x, piece.y)).occupying_piece
                        # Get the corresponding destination tile in the temporary board
                        dest_tile = temp_board.get_tile_from_pos((jump[0].x, jump[0].y))
                        # Get the corresponding jumped tile in the temporary board
                        jumped_tile = temp_board.get_tile_from_pos((jump[1].x, jump[1].y))

                        # Simulate the jump
                        new_board, multi_leg = self.simulate_move(temp_piece, dest_tile, jumped_tile, temp_board)
                        moves.append((new_board, multi_leg))
                else:
                    # Consider regular moves if no jumps are available
                    valid_moves = piece.valid_moves()
                    for move in valid_moves:
                        # Create a deep copy of the board to simulate the move
                        temp_board = deepcopy(board)
                        # Get the corresponding piece in the temporary board
                        temp_piece = temp_board.get_tile_from_pos((piece.x, piece.y)).occupying_piece
                        # Get the corresponding destination tile in the temporary board
                        dest_tile = temp_board.get_tile_from_pos((move.x, move.y))

                        # Simulate the move
                        new_board, _ = self.simulate_move(temp_piece, dest_tile, None, temp_board)
                        moves.append((new_board, False))

        return moves

    def simulate_move(self, piece, dest_tile, jumped_tile, board):
        """
        Simulates a move on the board

        Parameters:
        piece -- Piece to move
        dest_tile -- Destination tile
        jumped_tile -- Jumped tile (if it's a jump move)
        board -- Current board state

        Returns:
        tuple -- (board after move, is multi-leg jump possible)
        """
        # Get the source tile
        source_tile = board.get_tile_from_pos((piece.x, piece.y))

        # Update piece position
        piece.x, piece.y = dest_tile.x, dest_tile.y
        piece.pos = (dest_tile.x, dest_tile.y)

        # Update tile occupancy
        source_tile.occupying_piece = None
        dest_tile.occupying_piece = piece

        # Handle jump moves
        multi_leg = False
        if jumped_tile is not None:
            jumped_tile.occupying_piece = None

            # Check if multi-leg jumps are possible
            jumps = piece.valid_jumps()
            if jumps:
                multi_leg = True

        # Handle promotion for pawns
        if piece.notation == 'p':
            if (piece.color == "pink" and piece.y == 0) or (piece.color == "blue" and piece.y == 7):
                # Promote to king
                dest_tile.occupying_piece = King(piece.x, piece.y, piece.color, board)

        return board, multi_leg

if __name__ == '__main__':
    import pygame
    from Board import Board
    from King import King
    
    # Initialize pygame
    pygame.init()
    
    # Constants
    BOARD_SIZE = 8
    ORIGINAL_BOARD_WIDTH = 640  # The original board width
    TOTAL_PIECES = 12  # Each player starts with 12 pieces
    
    # Screen setup
    width, height = ORIGINAL_BOARD_WIDTH, ORIGINAL_BOARD_WIDTH
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Checkers AI Test")
    
    # Board setup
    tile_width, tile_height = ORIGINAL_BOARD_WIDTH // BOARD_SIZE, ORIGINAL_BOARD_WIDTH // BOARD_SIZE
    
    # Create a basic board
    board = Board(tile_width, tile_height, BOARD_SIZE, 0, 0, "pink")
    
    # Create and run the minimax algorithm
    
    for i in range(10):
        minimax = Minimax()
        result = minimax.maxAB(board, 2, float("-inf"), float("inf"), "pink")
        print('1')