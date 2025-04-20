import pygame
from Tile import Tile
from Pawn import Pawn
import copy

class Board:
	def __init__(self, tile_width, tile_height, board_size, offset_x=0, offset_y=0, starting_color="pink"):
		self.tile_width = tile_width
		self.tile_height = tile_height
		self.board_size = board_size
		self.offset_x = offset_x
		self.offset_y = offset_y
		self.selected_piece = None

		self.turn = starting_color  # Set initial turn to the specified starting color
		self.is_jump = False

		self.config = [
			['', 'bp', '', 'bp', '', 'bp', '', 'bp'],
			['bp', '', 'bp', '', 'bp', '', 'bp', ''],
			['', 'bp', '', 'bp', '', 'bp', '', 'bp'],
			['', '', '', '', '', '', '', ''],
			['', '', '', '', '', '', '', ''],
			['rp', '', 'rp', '', 'rp', '', 'rp', ''],
			['', 'rp', '', 'rp', '', 'rp', '', 'rp'],
			['rp', '', 'rp', '', 'rp', '', 'rp', '']
		]

		self.tile_list = self._generate_tiles()
		self._setup()

	def __deepcopy__(self, memo):
		"""Create a deep copy of the Board object."""
		id_self = id(self)
		if id_self in memo:
			return memo[id_self]
		
		# Create a new board with the same parameters
		result = type(self)(
			self.tile_width,
			self.tile_height,
			self.board_size,
			self.offset_x,
			self.offset_y,
			self.turn
		)
		memo[id_self] = result
		
		# Clear the auto-generated tile list and pieces
		result.tile_list = []
		
		# Deep copy each tile
		for tile in self.tile_list:
			tile_copy = copy.deepcopy(tile, memo)
			result.tile_list.append(tile_copy)
		
		# Copy pieces and update references
		for i, tile in enumerate(self.tile_list):
			if tile.occupying_piece is not None:
				# Create deep copy of the piece
				piece_copy = copy.deepcopy(tile.occupying_piece, memo)
				# Update board reference in the piece
				piece_copy.board = result
				# Set the piece in the corresponding tile
				result.tile_list[i].occupying_piece = piece_copy
		
		# Copy selected piece reference if any
		if self.selected_piece is not None:
			# Find the corresponding piece in the new board
			for tile in result.tile_list:
				piece = tile.occupying_piece
				if (piece is not None and 
					piece.x == self.selected_piece.x and 
					piece.y == self.selected_piece.y and
					piece.color == self.selected_piece.color):
					result.selected_piece = piece
					break
		
		# Copy other attributes
		result.is_jump = self.is_jump
		
		return result

	def _generate_tiles(self):
		output = []
		for y in range(self.board_size):
			for x in range(self.board_size):
				output.append(
					Tile(x, y, self.tile_width, self.tile_height, self.offset_x, self.offset_y)
				)
		return output

	def get_tile_from_pos(self, pos):
		for tile in self.tile_list:
			if (tile.x, tile.y) == (pos[0], pos[1]):
				return tile

	def _setup(self):
		for y_ind, row in enumerate(self.config):
			for x_ind, x in enumerate(row):
				tile = self.get_tile_from_pos((x_ind, y_ind))
				if x != '':
					if x[-1] == 'p':
						color = 'pink' if x[0] == 'r' else 'blue'
						tile.occupying_piece = Pawn(x_ind, y_ind, color, self)

	def handle_click(self, pos):
		x, y = pos[0], pos[-1]
		#if x >= self.board_size or y >= self.board_size:
		# Adjust for offsets
		x = (x - self.offset_x) // self.tile_width
		y = (y - self.offset_y) // self.tile_height
		
		# Make sure the click is within the board
		if 0 <= x < self.board_size and 0 <= y < self.board_size:
			clicked_tile = self.get_tile_from_pos((x, y))

			if self.selected_piece is None:
				if clicked_tile.occupying_piece is not None:
					if clicked_tile.occupying_piece.color == self.turn:
						self.selected_piece = clicked_tile.occupying_piece
			elif self.selected_piece._move(clicked_tile):
				if not self.is_jump:
					self.turn = 'pink' if self.turn == 'blue' else 'blue'
				else:
					if len(clicked_tile.occupying_piece.valid_jumps()) == 0:
						self.turn = 'pink' if self.turn == 'blue' else 'blue'
			elif clicked_tile.occupying_piece is not None:
				if clicked_tile.occupying_piece.color == self.turn:
					self.selected_piece = clicked_tile.occupying_piece

	def draw(self, display):
		if self.selected_piece is not None:
			self.get_tile_from_pos(self.selected_piece.pos).highlight = True
			if not self.is_jump:
				for tile in self.selected_piece.valid_moves():
					tile.highlight = True
			else:
				for tile in self.selected_piece.valid_jumps():
					tile[0].highlight = True

		for tile in self.tile_list:
			tile.draw(display)