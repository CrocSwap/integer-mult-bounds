from e8net import *
import sys
for n in (96,104):
    for name,N in (('LR',lr_net(n)),('E8',e8_net(n))):
        bad=N.legal(); ok,Mm=N.check()
        print(n,name,'legal-bad',bad[:3],'decoder-ok',ok,N.report(name),flush=True)
