import numpy as np
from board import SIZE, WHITE, BLACK

class Com:
    weight = [2, 5, 1]  # 位置による評価の重み, 確定石による評価の重み, 合法手による評価の重み

    # 評価用ボード
    eval_board = np.array([
        [45, -11, 4, -1, -1, 4, -11, 45],
        [-11, -26, -1, -3, -3, -1, -16, -11],
        [4, -1, 2, -1, -1, 2, -1, 4],
        [-1, -3, -1, 0, 0, -1, -3, -1],
        [-1, -3, -1, 0, 0, -1, -3, -1],
        [4, -1, 2, -1, -1, 2, -1, 4],
        [-11, -26, -1, -3, -3, -1, -16, -11],
        [45, -11, 4, -1, -1, 4, -11, 45],
        ],dtype=np.int64)
    
    def __init__(self, board, d):
        self.d = d
        self.board = board
    
    def board_point(self):
        """
        位置による評価の合計を返す
        """

        board_arr = np.array(list(bin(self.board.pb)[2:].zfill(64)), dtype=np.uint8)  # ビットボードを配列に直す
        board_arr = np.reshape(board_arr, (SIZE, SIZE))
        return np.sum(board_arr * Com.eval_board * 3)
    
    def get_right(self):
        """
        右辺の石を下位8ビットで返す
        """
        
        right = self.board.pb & 0x0000000000000001           # 8段目
        right |= (self.board.pb & 0x0000000000000100) >> 7   # 7段目
        right |= (self.board.pb & 0x0000000000010000) >> 14  # 6段目
        right |= (self.board.pb & 0x0000000001000000) >> 21  # 5段目
        right |= (self.board.pb & 0x0000000100000000) >> 28  # 4段目
        right |= (self.board.pb & 0x0000010000000000) >> 35  # 3段目
        right |= (self.board.pb & 0x0001000000000000) >> 42  # 2段目
        right |= (self.board.pb & 0x0100000000000000) >> 49  # 1段目
        return right

    def get_left(self):
        """
        左辺の石を下位8ビットで返す
        """
        left = self.board.pb & 0x0000000000000080 >> 7      # 8段目
        left |= (self.board.pb & 0x0000000000008000) >> 14  # 7段目
        left |= (self.board.pb & 0x0000000000800000) >> 21  # 6段目
        left |= (self.board.pb & 0x0000000080000000) >> 28  # 5段目
        left |= (self.board.pb & 0x0000008000000000) >> 35  # 4段目
        left |= (self.board.pb & 0x0000800000000000) >> 42  # 3段目
        left |= (self.board.pb & 0x0080000000000000) >> 49  # 2段目
        left |= (self.board.pb & 0x8000000000000000) >> 56  # 1段目
        return left
    
    @staticmethod
    def count_line(row):
        """
        ボードの1列(行）を受け取って端から連続する1をカウントする
        """

        #左から右
        mask = 0x80
        res = row & mask
        res |= row & (res >> 1)
        res |= row & (res >> 1)
        res |= row & (res >> 1)
        res |= row & (res >> 1)
        res |= row & (res >> 1)
        res |= row & (res >> 1)
        res |= row & (res >> 1)

        #右から左
        mask = 0x01
        res |= row & mask
        res |= row & (mask << 1)
        res |= row & (mask << 1)
        res |= row & (mask << 1)
        res |= row & (mask << 1)
        res |= row & (mask << 1)
        res |= row & (mask << 1)
        res |= row & (mask << 1)

        return res.bit_count()

    def stable_disc(self):
        """
        確定石の差を評価する
        角は重複して数える
        """
        up = self.board.pb >> 56                     # 上辺
        bottom = self.board.pb & 0x00000000000000ff  # 底辺
        left = self.get_left()                        # 左辺
        right = self.get_right()                      # 右辺
        
        return (Com.count_line(up) + Com.count_line(bottom) + Com.count_line(left) + Com.count_line(right)) * 11

    def candidate_num(self):
        """
        合法手の数で評価する
        """
        plb = self.board.legal_board(self.board.pb, self.board.ob)
        return plb.bit_count() * 10
    
    def mid_eval(self):
        """
        評価関数
        """
        bp = self.board_point()
        sd = self.stable_disc()
        cn = self.candidate_num()
        return Com.weight[0] * bp + Com.weight[1] * sd + Com.weight[2] * cn
    
    def final_eval(self):
        """
        決着がついた時の評価関数
        """
        return (self.board.pb.bit_count() - self.board.ob.bit_count()) * 100
    
    def nega_alpha(self, depth, alpha, beta):
        """
        ネガアルファ法
        """        
        olb = self.board.legal_board(self.board.ob, self.board.pb)
        plb = self.board.legal_board(self.board.pb, self.board.ob)

        if not (plb | olb):
            return self.final_eval()
        
        if depth == 0:
            return self.mid_eval()
        
        if plb:
            for _ in range(plb.bit_count()):
                pos = -plb & plb
                rev = self.board.reverse(pos)
                self.board.put(pos, rev)
                self.board.change_turn()
                alpha = max(alpha, -self.nega_alpha(depth - 1, -beta, -alpha))
                self.board.change_turn()
                self.board.put(pos, rev)
                plb ^= pos
                if alpha >= beta:
                    return alpha
        
        else:
            self.board.change_turn()
            alpha = max(alpha, -self.nega_alpha(depth - 1, -beta, -alpha))
            self.board.change_turn()
        
        return alpha

    def search(self):
        best_pos = None
        best_value = float("-inf")
        plb = self.board.legal_board(self.board.pb, self.board.ob)
        for _ in range(plb.bit_count()):
            pos = -plb & plb
            rev = self.board.reverse(pos)
            self.board.put(pos, rev)
            self.board.change_turn()
            value = -self.nega_alpha(self.d - 1, -float("inf"), -best_value)
            if value > best_value:
                best_value = value
                best_pos = pos
            self.board.change_turn()
            self.board.put(pos, rev)
            plb ^= pos
        return best_pos
