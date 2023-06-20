import pandas as pd
import numpy as np
import tensorflow as tf
import torch
import torch.nn.functional as F
import os as od
def pandas_lib_check():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

    # eseguiamo alcune operazioni con il DataFrame
    df_sum = df.sum()
    df_mean = df.mean()

    # eseguiamo un'altra operazione che non coinvolge il DataFrame
    x = 10

    # eseguiamo un'altra operazione con il DataFrame
    df_square = df.applymap(lambda x: x ** 2)

    # stampiamo i risultati
    print(df_sum)
    print(df_mean)
    print(x)
    print(df_square)


