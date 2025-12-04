import numpy as np
import random
from copy import deepcopy


class MCS:
    def __init__(self, env, sim_num):
        self.env = env
        self.sim_num = sim_num
    
    def random_action(self):
        plb = self.env.legal_board(self.env.pb, self.env.ob)
        legal_actions = []
        for _ in range(plb.bit_count()):
            pos = -plb & plb
            legal_actions.append(pos)
            plb ^= pos
        return random.choice(legal_actions)
    
    def playout(self):      
        action = self.random_action()
        rev = self.env.reverse(action)
        self.env.put(action, rev)
        next_plaeyr = self.env.next_player()
        if next_plaeyr == 0:
            score = self.env.get_winner()
        elif next_plaeyr == self.env.turn:
            score = self.playout()
        else:
            self.env.change_turn()
            score = -self.playout()
            self.env.change_turn()
        self.env.put(action, rev)
        return score
    
    def search(self):
        plb = self.env.legal_board(self.env.pb, self.env.ob)
        pos_num = plb.bit_count()
        scores = np.zeros(pos_num)
        legal_actions = []
        for i in range(pos_num):
            pos = -plb & plb
            legal_actions.append(pos)
            for _ in range(self.sim_num):
                rev = self.env.reverse(pos)
                self.env.put(pos, rev)
                next_player = self.env.next_player()
                if not next_player:
                    scores[i] += self.env.get_winner()
                elif next_player == self.env.turn:
                    scores[i] += self.playout()
                else:
                    self.env.change_turn()
                    scores[i] += -self.playout()
                    self.env.change_turn()
                self.env.put(pos, rev)
            plb ^= pos
        return int(legal_actions[np.argmax(scores)])

class MCTS(MCS):
    def __init__(self, env, sim_num, expand_num):
        super().__init__(env, sim_num)
        self.expand_num = expand_num
        self.w = 0
        self.n = 0
        self.child_nodes = []

    def expand(self):
        plb = self.env.legal_board(self.env.pb, self.env.ob)
        for _ in range(plb.bit_count()):
            pos = -plb & plb
            rev = self.env.reverse(pos)
            self.env.put(pos, rev)
            if (next_player := self.env.next_player()) == self.env.turn * -1:
                self.env.change_turn()
                self.child_nodes.append(MCTS(deepcopy(self.env), self.sim_num, self.expand_num))
                self.env.change_turn()
            else:
                self.child_nodes.append(MCTS(deepcopy(self.env), self.sim_num, self.expand_num))
            self.env.put(pos, rev)
            plb ^= pos
    
    @staticmethod
    def calc_value(w, n, t):
        return w / n + (2 * np.log1p(t - 1) / n) ** 0.5
    
    def get_max_child(self):
        t = 0
        for child in self.child_nodes:
            if child.n == 0:
                return child
            t += child.n
        
        values = []
        for child in self.child_nodes:
            values.append(MCTS.calc_value(child.w, child.n, t))
        return self.child_nodes[np.argmax(values)]
    
    def evaluate(self):
        if  self.env.next_player() == 0:
            value = self.env.get_winner()
            self.w += value
            self.n += 1
            return value
        
        if self.child_nodes:
            value = -self.get_max_child().evaluate()
            self.w += value
            self.n += 1
            return value
        
        else:
            value = self.playout()
            self.w += value
            self.n += 1

            if self.n == self.expand_num:
                self.expand()
            return value
        
    def search(self):
        self.expand()
        for _ in range(self.sim_num):
            self.evaluate()
        
        plb = self.env.legal_board(self.env.pb, self.env.ob)
        legal_actions = []
        n_lst = []
        for child in self.child_nodes:
            pos = -plb & plb
            legal_actions.append(pos)
            n_lst.append(child.n)
            plb ^= pos
        self.w = 0
        self.n = 0
        self.child_nodes = []
        return legal_actions[np.argmax(n_lst)]
