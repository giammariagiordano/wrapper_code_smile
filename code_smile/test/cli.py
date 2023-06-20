#generate a program that uses pandas dataframe and access to data by matrix
import tensorflow as tf
import pandas as pd
import numpy as np
import torch.optim as optim
def test():
    df = pd.DataFrame(np.random.randn(5, 3), columns=list('ABC'),dtype=np.float64)
    df = pd.read_csv("test.csv")
    df = pd.read_csv("test.csv")
    df = pd.DataFrame(np.random.randn(5, 3), columns=list('ABC'))
    optim
    df['new_col_int'] = 0
    df['new_col_str'] = ''

    print(df.values)
    df_print = df[0][0]
    print(df_print)

def fibonacci(n):
    a = tf.constant(1)
    b = tf.constant(1)
    c = tf.constant([1, 1])
    c = tf.constant([])
    c = tf.TensorArray(tf.int32, n)
    c = c.write(0, a)
    c = c.write(1, b)

if __name__ == '__main__':
    test()
