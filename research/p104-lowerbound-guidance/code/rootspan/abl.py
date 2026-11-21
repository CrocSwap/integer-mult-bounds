from rootspan import *
def mind(**kw):
    for D in range(8,60):
        if solve(D,**kw) is not None: return D
print('full',mind())
print('no hall',mind(hall=False))
print('no gen (A only)',mind(gen=False))
print('no gen no hall',mind(gen=False,hall=False))
