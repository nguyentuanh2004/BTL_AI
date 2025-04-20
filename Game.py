class Game:

	def __init__(self):
		self.winner = None
		self.is_draw = False  # New flag to track draw state

	# checks if both colors still has a piece
	def check_piece(self, board):
		red_piece = 0
		black_piece = 0
		for y in range(board.board_size):
			for x in range(board.board_size):
				tile = board.get_tile_from_pos((x, y))
				if tile.occupying_piece != None:
					if tile.occupying_piece.color == "pink":
						red_piece += 1
					else:
						black_piece += 1
		return red_piece, black_piece

	def player_has_valid_moves(self, board, color):
		# Check if the player with the given color has any valid moves
		for tile in board.tile_list:
			if tile.occupying_piece is not None and tile.occupying_piece.color == color:
				# Check if the piece has any valid moves or jumps
				if len(tile.occupying_piece.valid_moves()) > 0 or len(tile.occupying_piece.valid_jumps()) > 0:
					return True
		return False

	def is_game_over(self, board):
		red_piece, black_piece = self.check_piece(board)
		
		# Check if a player has no pieces left
		if red_piece == 0 or black_piece == 0:
			self.winner = "pink" if red_piece > black_piece else "blue"
			self.is_draw = False
			return True
		
		# Check if current player has no valid moves
		current_color = board.turn
		opponent_color = "blue" if current_color == "pink" else "pink"
		
		current_has_moves = self.player_has_valid_moves(board, current_color)
		opponent_has_moves = self.player_has_valid_moves(board, opponent_color)
		
		# Check for draw - neither player has valid moves
		if not current_has_moves and not opponent_has_moves:
			self.is_draw = True
			self.winner = None
			return True
		
		# Current player has no valid moves but opponent does
		if not current_has_moves:
			# If current player has no valid moves, they lose
			self.winner = opponent_color
			self.is_draw = False
			return True
			
		return False

	def check_jump(self, board):
		piece = None
		for tile in board.tile_list:
			if tile.occupying_piece != None:
				piece = tile.occupying_piece
				if len(piece.valid_jumps()) != 0 and board.turn == piece.color:
					board.is_jump = True
					break
				else:
					board.is_jump = False
		if board.is_jump:
			board.selected_piece = piece
			board.handle_click(piece.pos)
		return board.is_jump

	def message(self):
		if self.is_draw:
			print("Game ended in a draw!")
		else:
			print(f"{self.winner} Wins!!")