import numpy as np


SIZE = 8
WHITE = -1
BLACK = 1
INIT_BLACK_BOARD = 0x0000000810000000
INIT_WHITE_BOARD = 0x0000001008000000

class Board:
    def __init__(self):
        self.pb = INIT_BLACK_BOARD            # 打ちての盤面
        self.ob = INIT_WHITE_BOARD            # 相手の盤面

    def blank(self):
        """
        空いているマスを１としたビットボードを返す
        """
        return ~(self.pb | self.ob)
    
    @staticmethod
    def rshift(b, n):
        """
        ビット列を右方向にnシフトする
        """
        return b >> n
    
    @staticmethod
    def lshift(b, n):
        """
        ビット列を左方向にnシフトする
        """
        return b << n
    
    @staticmethod
    def check_line(pb, mask, shift, n):
        """
        一直線に連続する石を求める
        """
        res = mask & shift(pb, n)
        res |= mask & shift(res, n)
        res |= mask & shift(res, n)
        res |= mask & shift(res, n)
        res |= mask & shift(res, n)
        res |= mask & shift(res, n)
        return res
    
    def legal_board(self, pb, ob):
        """
        pb側の合法手を生成する
        """

        blank_board = self.blank()   # 空きマスが１のボード
        
        mask = 0x7e7e7e7e7e7e7e7e & ob  # 左右のつながりを絶つ

        #左に連続する場所を求める
        res = Board.check_line(pb, mask, Board.lshift, 1)
        legal_board = Board.lshift(res, 1)

        #に連続する場所を求める
        res = Board.check_line(pb, mask, Board.rshift, 1)
        legal_board |=  Board.rshift(res, 1)  

        mask = 0x00FFFFFFFFFFFF00 & ob    # 上下のつながりを絶つ

        #下に連続する場所を求める
        res = Board.check_line(pb, mask, Board.rshift, 8)
        legal_board |= Board.rshift(res, 8)

        #上に連続する場所を求める
        res = Board.check_line(pb, mask, Board.lshift, 8)
        legal_board |= Board.lshift(res, 8)

        mask = ob & 0x007e7e7e7e7e7e00    #  全辺のつながりを絶つ

        #左上に連続する場所を求める
        res = Board.check_line(pb, mask, Board.lshift, 9)
        legal_board |=  Board.lshift(res, 9)

        #左下に連続する場所を求める
        res = Board.check_line(pb, mask, Board.rshift, 7)
        legal_board |=  Board.rshift(res, 7)

        #右上に連続する場所を求める
        res = Board.check_line(pb, mask, Board.lshift, 7)
        legal_board |= Board.lshift(res, 7)

        #右下に連続する場所を求める
        res = Board.check_line(pb, mask, Board.rshift, 9)
        legal_board |=  Board.rshift(res, 9)

        return legal_board & blank_board

    def reverse(self, pos):
        """
        反転する場所を取得する
        """
        blank_board = self.blank()
        ob = 0x7e7e7e7e7e7e7e7e & self.ob

        #左に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.rshift, 1)
        legal = blank_board & Board.rshift(legal, 1)
        res = Board.check_line(pos & legal, ob, Board.lshift, 1)
        

        #右に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.lshift, 1)
        legal = blank_board& Board.lshift(legal, 1)
        res |= Board.check_line(pos & legal, ob, Board.rshift, 1)
        
        ob = 0x00FFFFFFFFFFFF00 & self.ob

        #上に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.rshift, 8)
        legal = blank_board & Board.rshift(legal, 8)
        res |= Board.check_line(pos & legal, ob, Board.lshift, 8)
        
        #下に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.lshift, 8)
        legal = blank_board & Board.lshift(legal, 8)
        res |= Board.check_line(pos & legal, ob, Board.rshift, 8)

        ob = 0x007e7e7e7e7e7e00 & self.ob
        
        #左上に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.rshift, 9)
        legal = blank_board & Board.rshift(legal, 9)
        res |= Board.check_line(pos & legal, ob, Board.lshift, 9)

        #左上に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.lshift, 7)
        legal = blank_board & Board.lshift(legal, 7)
        res |= Board.check_line(pos & legal, ob, Board.rshift, 7)

        #右上に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.rshift, 7)
        legal = blank_board & Board.rshift(legal, 7)
        res |= Board.check_line(pos & legal, ob, Board.lshift, 7)
        
        #右下に返る石を求める
        legal = Board.check_line(self.pb, ob, Board.lshift, 9)
        legal = blank_board & Board.lshift(legal, 9)
        res |= Board.check_line(pos & legal, ob, Board.rshift, 9)
        
        return res
    
    def check_put(self, pos):
        """
        おける場所か判断する関数
        おけるならtrue
        """
        
        return pos & self.legal_board(self.pb, self.ob)
    
    def put(self, pos, rev):
        """
        石をおいてひっくり返す関数
        """
        
        self.pb ^= rev | pos
        self.ob ^= rev

if __name__ == "__main__":
    import time

    board = Board()
    start = time.perf_counter()
    for _ in range(100):
        board.legal_board(board.pb, board.ob)
    end = time.perf_counter()
    print(end - start)
0.0011095000081695616
0.001786