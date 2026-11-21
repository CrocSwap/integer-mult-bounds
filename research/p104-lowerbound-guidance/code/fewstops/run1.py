from check import *
from reassign import build
print(check(W,'t7669'))
W2=build(W)
print(check(W2,'U-assign'))
import pickle; pickle.dump(W2,open('W_U.pkl','wb'))
