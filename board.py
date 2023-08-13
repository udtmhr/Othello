from numba.experimental import jitclass
from globalvar import *

SIZE = 8
WHITE = -1
BLACK = 1
INIT_BLACK_BOARD = 0x0000000810000000
INIT_WHITE_BOARD = 0x0000001008000000

class Board:
    def __init__(self):
        self.pb = INIT_BLACK_BOARD            # 打ちての盤面
        self.ob = INIT_WHITE_BOARD            # 相手の盤面
        self.turn = BLACK                     # 手番
        self.player_score = 2                 # プレイヤーの石の数
        self.com_score = 2                    # コンピュータの石の数
        self.player_color = 0                 # プレイヤーの色
        self.com_color = 0                    # コンピュータの色
        self.pre_pos = 0                      # 前回の手
   
    def init(self):
        self.pb = INIT_BLACK_BOARD
        self.ob = INIT_WHITE_BOARD
        self.turn = BLACK
        self.player_score = 2
        self.com_score = 2
        self.player_color = 0
        self.com_color = 0       

    def blank(self):
        """
        空いているマスを１としたビットボードを返す
        """
        return ~(self.pb | self.ob)
    
    def rshift(self, b, n):
        """
        ビット列を右方向にnシフトする
        """
        return b >> n
    
    def lshift(self, b, n):
        """
        ビット列を左方向にnシフトする
        """
        return b << n
    
    def check_line(self, pb, mask, shift, n):
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
        res = self.check_line(pb, mask, self.lshift, 1)
        legal_board = self.lshift(res, 1)

        #に連続する場所を求める
        res = self.check_line(pb, mask, self.rshift, 1)
        legal_board |=  self.rshift(res, 1)  

        mask = 0x00FFFFFFFFFFFF00 & ob    # 上下のつながりを絶つ

        #下に連続する場所を求める
        res = self.check_line(pb, mask, self.rshift, 8)
        legal_board |= self.rshift(res, 8)

        #上に連続する場所を求める
        res = self.check_line(pb, mask, self.lshift, 8)
        legal_board |= self.lshift(res, 8)

        mask = ob & 0x007e7e7e7e7e7e00    #  全辺のつながりを絶つ

        #左上に連続する場所を求める
        res = self.check_line(pb, mask, self.lshift, 9)
        legal_board |=  self.lshift(res, 9)

        #左下に連続する場所を求める
        res = self.check_line(pb, mask, self.rshift, 7)
        legal_board |=  self.rshift(res, 7)

        #右上に連続する場所を求める
        res = self.check_line(pb, mask, self.lshift, 7)
        legal_board |= self.lshift(res, 7)

        #右下に連続する場所を求める
        res = self.check_line(pb, mask, self.rshift, 9)
        legal_board |=  self.rshift(res, 9)

        return legal_board & blank_board

    def reverse(self, pos):
        """
        反転する場所を取得する
        """
        blank_board = self.blank()
        ob = 0x7e7e7e7e7e7e7e7e & self.ob

        #左に返る石を求める
        legal = self.check_line(self.pb, ob, self.rshift, 1)
        legal = blank_board & self.rshift(legal, 1)
        res = self.check_line(pos & legal, ob, self.lshift, 1)
        

        #右に返る石を求める
        legal = self.check_line(self.pb, ob, self.lshift, 1)
        legal = blank_board& self.lshift(legal, 1)
        res |= self.check_line(pos & legal, ob, self.rshift, 1)
        
        ob = 0x00FFFFFFFFFFFF00 & self.ob

        #上に返る石を求める
        legal = self.check_line(self.pb, ob, self.rshift, 8)
        legal = blank_board & self.rshift(legal, 8)
        res |= self.check_line(pos & legal, ob, self.lshift, 8)
        
        #下に返る石を求める
        legal = self.check_line(self.pb, ob, self.lshift, 8)
        legal = blank_board & self.lshift(legal, 8)
        res |= self.check_line(pos & legal, ob, self.rshift, 8)

        ob = 0x007e7e7e7e7e7e00 & self.ob
        
        #左上に返る石を求める
        legal = self.check_line(self.pb, ob, self.rshift, 9)
        legal = blank_board & self.rshift(legal, 9)
        res |= self.check_line(pos & legal, ob, self.lshift, 9)

        #左上に返る石を求める
        legal = self.check_line(self.pb, ob, self.lshift, 7)
        legal = blank_board & self.lshift(legal, 7)
        res |= self.check_line(pos & legal, ob, self.rshift, 7)

        #右上に返る石を求める
        legal = self.check_line(self.pb, ob, self.rshift, 7)
        legal = blank_board & self.rshift(legal, 7)
        res |= self.check_line(pos & legal, ob, self.lshift, 7)
        
        #右下に返る石を求める
        legal = self.check_line(self.pb, ob, self.lshift, 9)
        legal = blank_board & self.lshift(legal, 9)
        res |= self.check_line(pos & legal, ob, self.rshift, 9)
        
        return res
    
    def check_put(self, pos):
        """
        おける場所か判断する関数
        おけるならtrue
        """
        
        return (pos & self.legal_board(self.pb, self.ob) == pos)
    
    def put(self, pos, rev):
        """
        石をおいてひっくり返す関数
        """

        self.pb ^= rev | pos
        self.ob ^= rev
    
    def to_bin(self, x, y):
        """
        ボードの座標をビットに直す
        """

        b = 0x8000000000000000
        b = b >> x      # x方向へシフト
        b = b >> y * 8  # y方向へのシフト
        return b

    def next_player(self):
        if (olb := self.legal_board(self.ob, self.pb)):  # 相手がおける
            self.change_turn()
            return 2
        
        if (plb := self.legal_board(self.pb, self.ob)):  # 相手がパス
            return 1
        
        return 0                                         # 終局
    
    def change_turn(self):
        """
        手番を交代する関数
        """
        # 手番の色の入れ替え
        self.turn *= -1

        #ボードの入れ替え
        self.pb ^= self.ob
        self.ob ^= self.pb
        self.pb ^= self.ob
