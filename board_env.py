import numpy as np
from board import *

class Othello(Board):
    def __init__(self):
        super().__init__()
        self.turn = BLACK                  # 手番
        self.player_color = None           # プレイヤーの色
        self.com_color = None              # コンピュータの色
        self.score = {BLACK: 2, WHITE: 2}  # 石の数
        self.pre_pos = None                # 前回の手
    
    def set_color(self, color):
        self.player_color = color
        self.com_color = color * -1
    
    def put(self, pos, rev):
        super().put(pos, rev)
        self.count()

    
    @staticmethod
    def to_bin(x, y):
        """
        ボードの座標をビットに直す
        """

        b = 0x8000000000000000
        b = b >> x                              # x方向へシフト
        b = b >> y * 8                          # y方向へのシフト
        return b

    def next_player(self):
        if self.legal_board(self.ob, self.pb):  # 相手がおける
            return self.turn * -1
        
        if self.legal_board(self.pb, self.ob):  # 相手がパス
            return self.turn
        
        return 0                                # 終局
    
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
    
    def count(self):
        self.score[self.turn] = self.pb.bit_count()
        self.score[self.turn * -1] = self.ob.bit_count()

    @staticmethod
    def to_array(board, shape=(8, 8)):
        """
        二次元配列に直す
        """
        return np.array(list(bin(board)[2:].zfill(64)), dtype=int).reshape(shape)

    def get_winner(self):
        if self.score[self.player_color] > self.score[self.com_color]:
            return self.player_color
        elif self.score[self.player_color] < self.score[self.com_color]:
            return self.com_color
        else:
            return 0
        
    def reward(self, next):
        if not next:
            return self.get_winner() * self.player_color
        else:
            return 0
    
    def disp(self):
        black = Othello.to_array(self.pb)
        white = Othello.to_array(self.ob)
        board = ((black - white) * self.turn)
        print(board)