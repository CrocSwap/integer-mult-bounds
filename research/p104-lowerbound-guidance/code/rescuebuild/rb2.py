from rb1 import *
H=F({0,1,2,3})
K4_4=[(H,[]),(H,[])]+[(F(p),[F(p)]) for p in [(0,1),(0,2),(1,3),(2,3)]]
K4_3=[(H,[]),(H,[])]+[(F(p),[F(p)]) for p in [(0,1),(0,2),(0,3),(1,2)]]
if __name__=="__main__":run('K4#4 (dead ctl)',4,K4_4,seeds=2,tries=6)
if __name__=="__main__":run('K4#3 (dead ctl)',4,K4_3,seeds=2,tries=6)
