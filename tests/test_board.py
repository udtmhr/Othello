import sys
import os
import pytest

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from othello.core.board import Board, SIZE, BLACK, WHITE

def test_board_initialization():
    board = Board()
    assert board.pb == 0x0000000810000000
    assert board.ob == 0x0000001008000000

def test_legal_moves_initial():
    board = Board()
    legal = board.legal_board(board.pb, board.ob)
    # Initial legal moves for black: (2,3), (3,2), (4,5), (5,4) -> indices 19, 26, 37, 44
    # 0x0000102004080000
    expected_legal = 0x0000102004080000
    assert legal == expected_legal
