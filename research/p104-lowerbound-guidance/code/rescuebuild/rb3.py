from rb1 import *
A6=F(range(6))
CS6=[(A6,[F({3,4}),F({0,5})]),(A6,[F({0,3}),F({2,4})])]+[(F(p),[F(p)]) for p in [(1,2),(1,3),(1,4),(2,5)]]+[(F(p),[]) for p in [(0,3),(0,5),(2,4),(3,4)]]
if __name__=="__main__":run('CS k6 137.557',6,CS6,seeds=3,tries=8)
