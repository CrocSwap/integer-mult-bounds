import sys,json,collections
sys.path.insert(0,'.')
from tails import *
fin=W['final']
def analyse(o,verbose=False):
    rows=o.get('dirty',[])
    mains=[d for d in rows if d['kind']=='pub' and d['G']!=127]
    v127=[d for d in rows if d['kind']=='pub' and d['G']==127]
    own=[d for d in rows if d['kind']!='pub']
    res=dict(nmain=len(mains),nv=len(v127),nown=len(own),need=collections.Counter(),pairs=set(),colsnonhelper=0)
    for d in mains:
        r,G=d['r'],d['G']; Tm=arrive(r,G)
        for c in d['cols']:
            if fin[c]!=127: res['colsnonhelper']+=1; st=('col-main',None)
            else: st=opt(c,G,Tm)
            res['need'][st[0]]+=1
            if st[0]=='ok': res['pairs'].add((c,G))
            if verbose: I=info(c); print('  main',r,'G',G,'dG',M.dim[G],'T',Tm,'| helper',c,'L',I['L'],'dL',I['dL'],'F',I['F'],'lastop',I['lastop'],'firstF',I['firstF'],'->',st)
    return res
if __name__=='__main__':
    for l in open(sys.argv[1]):
        o=json.loads(l); 
        if 'dirty' not in o: print(o['st'],o.get('err')); continue
        print(o['st'],'ok',o['ok']); a=analyse(o,verbose=len(sys.argv)>2)
        print('   mains',a['nmain'],'V127',a['nv'],'owned',a['nown'],dict(a['need']))
