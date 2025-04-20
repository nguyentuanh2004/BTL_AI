import pygame

class Piece:
	def __init__(self, x, y, color, board):
		self.x = x
		self.y = y
		self.pos = (x, y)
		self.board = board
		self.color = color

	def __deepcopy__(self, memo):
		"""Create a deep copy of the Piece object."""
		id_self = id(self)
		if id_self in memo:
			return memo[id_self]
			
		# Create a new instance without initializing
		result = type(self).__new__(type(self))
		memo[id_self] = result
		
		# Copy attributes manually
		result.x = self.x
		result.y = self.y
		result.pos = self.pos
		# board reference will be updated by the caller
		result.board = None  
		result.color = self.color
		
		# For subclasses that have an image
		if hasattr(self, 'img'):
			result.img = self.img  # Pygame surfaces don't need deep copying
		if hasattr(self, 'notation'):
			result.notation = self.notation
		if hasattr(self, 'has_moved'):
			result.has_moved = self.has_moved
			
		return result

	def _move(self, tile):
		for i in self.board.tile_list:
			i.highlight = False

		if tile in self.valid_moves() and not self.board.is_jump:
			prev_tile = self.board.get_tile_from_pos(self.pos)
			self.pos, self.x, self.y = tile.pos, tile.x, tile.y

			prev_tile.occupying_piece = None
			tile.occupying_piece = self
			self.board.selected_piece = None
			self.has_moved = True

			# Pawn promotion
			if self.notation == 'p':
				if self.y == 0 or self.y == 7:
					from King import King
					tile.occupying_piece = King(
						self.x, self.y, self.color, self.board
					)
			return True

		elif self.board.is_jump:
			for move in self.valid_jumps():
				if tile in move:
					prev_tile = self.board.get_tile_from_pos(self.pos)
					jumped_piece = move[-1]
					self.pos, self.x, self.y = tile.pos, tile.x, tile.y

					prev_tile.occupying_piece = None
					jumped_piece.occupying_piece = None
					tile.occupying_piece = self
					self.board.selected_piece = None
					self.has_moved = True

					# Pawn promotion
					if self.notation == 'p':
						if self.y == 0 or self.y == 7:
							from King import King
							tile.occupying_piece = King(
								self.x, self.y, self.color, self.board
							)
					return True
		else:
			self.board.selected_piece = None
			return False