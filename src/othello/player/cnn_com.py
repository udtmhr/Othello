import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.utils import CustomObjectScope
from keras.initializers import glorot_uniform

class Bias(keras.layers.Layer):
    def __init__(self, input_shape):
        super(Bias, self).__init__()
        self.w = tf.Variable(initial_value=tf.zeros(input_shape[1:]), trainable=True)

    def call(self, inputs):
        return inputs + self.w


class CNNCom:
    def __init__(self, board, path='models/model-05.h5'):
        self.board = board
        self.path = path
        self.model = self.load_model(path)

    def load_model(self, path):
        with CustomObjectScope({'Bias': Bias((1, 64))}):
            model = tf.keras.models.load_model(path)
            return model
    
    def make_input(self):
        return np.array([[self.board.to_array(self.board.pb), self.board.to_array(self.board.ob)]])
    
    def search(self):
        plb = self.board.legal_board(self.board.pb, self.board.ob)
        plb = self.board.to_array(plb).reshape(64)
        input_data = self.make_input()
        prob = self.model(input_data)[0]
        return 0x8000000000000000 >> int(np.argmax(plb * prob))


if __name__ == "__main__":
    from othello.core.board import Board

    env = Board()
    cnn = CNNCom(env)
    input = cnn.make_input()
    print(cnn.model(input)[0].max())
