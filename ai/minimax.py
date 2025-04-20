from checkers.glob_misc import GREEN, TIME_DELAY, ROW_COL
from copy import deepcopy
import pygame


class Minimax:
    def maxAB(self, game_board, depth, alpha, beta, game, player, verbose):
        """
        maxAB operates the Max part of the Minimax algorithm with alpha beta pruning.
        :param game_board: the state of the game board
        :param depth: the depth the algorithm is searching too
        :param alpha: alpha for pruning
        :param beta: beta for pruning
        :param game: the game object being used
        :param player: whether the algorithm is playing as a player or computer
        :param verbose: whether the possible ai moves should be shown
        :return:
        """
        if depth == 0 or game_board.player_win() is not None:
            return self.evaluate(game_board, player), game_board, False
        else:
            max_eval = float("-inf")
            best_move = None
            best_move_multi_leg = None
            moves = self.get_all_moves(game_board, game, player, verbose)
            for move, multi_leg in moves:
                evaluation = self.minAB(
                    move, depth - 1, alpha, beta, game, not player, verbose
                )[0]

                if evaluation > max_eval:
                    best_move = move
                    best_move_multi_leg = multi_leg

                if max_eval >= beta:
                    return max_eval, best_move, best_move_multi_leg

                if max_eval > alpha:
                    alpha = max_eval

            return max_eval, best_move, best_move_multi_leg

    def minAB(self, game_board, depth, alpha, beta, game, player, verbose):
        """
        minAB operates the Min part of the Minimax algorithm with alpha beta pruning.
        :param game_board: the state of the game board
        :param depth: the depth the algorithm is searching too
        :param alpha: alpha for pruning
        :param beta: beta for pruning
        :param game: the game object being used
        :param player: whether the algorithm is playing as a player or computer
        :param verbose: whether the possible ai moves should be shown
        :return:
        """
        if depth == 0 or game_board.player_win() is not None:
            return self.evaluate(game_board, player), game_board, False
        else:
            min_eval = float("inf")
            best_move = None
            best_move_multi_leg = None
            moves = self.get_all_moves(game_board, game, player, verbose)
            for move, multi_leg in moves:
                evaluation = self.maxAB(
                    move, depth - 1, alpha, beta, game, not player, verbose
                )[0]

                if evaluation < min_eval:
                    best_move = move
                    best_move_multi_leg = multi_leg

                if min_eval <= alpha:
                    return min_eval, best_move, best_move_multi_leg

                if min_eval < beta:
                    beta = min_eval

            return min_eval, best_move, best_move_multi_leg

    def simulate_move(self, counter, row, col, board):
        """
        simulate_move simulates a given move providing the board for evaluation
        :param counter: counter being moved
        :param move: counters move
        :param board: the current state of the game board
        :return:
        """
        jump, new_king = board.move_counter(counter, row, col)
        new_counter = board.get_counter(row, col)
        return (board, jump and not new_king and len(board.jump_moves(new_counter)) > 0)

    def get_all_moves(self, game_board, game, player, verbose=True):
        """
        get_all_moves gets all the moves a player can make
        :param game_board: current state of the game board
        :param game: current state of the game
        :param player: player being interested
        :param verbose: whether all outputs should be output to the player
        :return:
        """
        moves = []
        counters = game_board.get_valid_counters(player)
        for counter in counters:
            valid_moves = game_board.get_valid_moves(counter)
            for row, col in valid_moves:
                temp_board = deepcopy(game_board)
                temp_counter = temp_board.get_counter(counter.row, counter.col)
                new_board, multi_leg = self.simulate_move(
                    temp_counter, row, col, temp_board
                )
                if verbose:
                    self.draw_moves(game, new_board, counter)
                moves.append((new_board, multi_leg))

        return moves

    def draw_moves(self, game, board, counter):
        """
        draw_moves draws all the moves the ai is calculating
        :param game: current state of the game
        :param board: current state of the game board
        :param counter: counter being moved
        :return:
        """
        valid_moves = board.get_valid_moves(counter)
        board.draw(game.surface)
        counter.draw(game.surface)
        pygame.draw.circle(game.surface, GREEN, (counter.x, counter.y), 50, 5)
        game.draw_moves(valid_moves)
        pygame.time.delay(TIME_DELAY // 4)
        pygame.display.update()

    def evaluate(self, board, player=False):
        """
        evaluate evaluates the quality of the ai move
        :param board: current board state
        :param player: playing being assessed
        :return:
        """
        eval = 0
        rows = 0
        counters = board.get_sides_counters(player)
        for counter in counters:
            if not counter.king:
                if player:
                    rows += (ROW_COL - 1) - counter.row
                else:
                    rows += counter.row
        if player:
            eval = (
                (board.player_remaining - board.comp_remaining)
                + ((board.player_kings - board.comp_kings) / 2)
                + (rows / 2)
            )
        else:
            eval = (
                (board.comp_remaining - board.player_remaining)
                + ((board.comp_kings - board.player_kings) / 2)
                + (rows / 2)
            )
        return eval
