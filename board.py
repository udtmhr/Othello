from globalvar import SIZE, EMPTY, WHITE, BLACK

class Board:
    def __init__(self):
        self.pb = 0x0000000810000000          # 打ちての盤面
        self.ob = 0x0000001008000000          # 相手の盤面
        self.turn = BLACK                     # 手番
        self.black = 2                        # 黒の石の数
        self.white = 2                        # 白の石の数
        self.vertical = 0x00FFFFFFFFFFFF00    # 上下の壁
        self.horizontal = 0x7e7e7e7e7e7e7e7e  # 左右の壁
        self.diagonal = 0x007e7e7e7e7e7e00    # 全辺の壁
    
    def init_board(self):
        self.pb = 0x0000000810000000          # 打ちての盤面
        self.ob = 0x0000001008000000          # 相手の盤面
        self.turn = BLACK                     # 手番
        self.black = 2                        # 黒の石の数
        self.white = 2                        # 白の石の数

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
        
        mask = self.horizontal & ob  # 左右の番人

        #左
        res = self.check_line(pb, mask, self.lshift, 1)
        legal_board = self.lshift(res, 1)

        #右
        res = self.check_line(pb, mask, self.rshift, 1)
        legal_board |=  self.rshift(res, 1)  

        mask = self.vertical & ob    # 上下の番人

        #下
        res = self.check_line(pb, mask, self.rshift, 8)
        legal_board |= self.rshift(res, 8)

        #上
        res = self.check_line(pb, mask, self.lshift, 8)
        legal_board |= self.lshift(res, 8)

        mask = self.diagonal & ob    # 全辺の番人

        #左上
        res = self.check_line(pb, mask, self.lshift, 9)
        legal_board |=  self.lshift(res, 9)

        #左下
        res = self.check_line(pb, mask, self.rshift, 7)
        legal_board |=  self.rshift(res, 7)

        #右上
        res = self.check_line(pb, mask, self.lshift, 7)
        legal_board |= self.lshift(res, 7)

        #右下
        res = self.check_line(pb, mask, self.rshift, 9)
        legal_board |=  self.rshift(res, 9)

        return legal_board & blank_board

    def reverse(self, pos):
        """
        反転する場所を取得する
        """
        
        ob = self.horizontal & self.ob

        #左に返る石を求める
        res = self.check_line(pos, ob, self.lshift, 1)
        

        #右に返る石を求める
        res |= self.check_line(pos, ob, self.rshift, 1)
        
        ob = self.vertical & self.ob

        #上に返る石を求める
        res |= self.check_line(pos, ob, self.lshift, 8)
        
        #下に返る石を求める
        res |= self.check_line(pos, ob, self.rshift, 8)

        ob= self.diagonal & self.ob

        #左上に返る石を求める
        res |= self.check_line(pos, ob, self.lshift, 9)

        #左下に返る石を求める
        res |= self.check_line(pos, ob, self.rshift, 7)

        #右上に返る石を求める
        res |= self.check_line(pos, ob, self.lshift, 7)
        
        #右下に返る石を求める
        res |= self.check_line(pos, ob, self.rshift, 9)
        
        return res
    
    def check_put(self, pos):
        """
        おける場所か判断する関数
        おけるならtrue
        """
        legal = self.legal_board(self.pb, self.ob)
        return (pos & legal == pos)
    
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
        olb = self.legal_board(self.ob, self.pb)  # 相手の合法手
        if olb:                                   # 相手がおける
            self.change_turn()
            return 0
        
        plb = self.legal_board(self.pb, self.ob)  # 自分の合法手
        if plb:                                   # 相手がパス
            return 1
        
        return 2                                  # 終局
    
    def change_turn(self):
        self.turn *= -1
        self.pb ^= self.ob
        self.ob ^= self.pb
        self.pb ^= self.ob
        
if __name__ == "__main__":

    def print_board(board):
        import numpy as np
        board = format(board, "064b")
        board = np.reshape(np.array(list(board), dtype=int), (8, 8))
        print(board)