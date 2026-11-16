import sys,pickle,random; sys.path.insert(0,'.')
exec(open('plant.py').read().split("with open('jobs_ctl_plant'")[0])
random.seed(11); dec=random.sample(M,20); sm=Ms+dec
with open('base_small.txt','w') as f:
    f.write(' '.join(map(str,lab))+'\n%d\n'%len(sm)); [f.write('%d %d\n'%(m&((1<<64)-1),m>>64)) for m in sm]
with open('jobs_ctl_plant','w') as fo:
    fo.write('6 0 4\n'); [fo.write('%d %d\n'%(m&((1<<64)-1),m>>64)) for m in T]
# negative twin: same targets but drop planted M3 from the base
with open('base_small_neg.txt','w') as f:
    s2=Ms[:3]+dec; f.write(' '.join(map(str,lab))+'\n%d\n'%len(s2)); [f.write('%d %d\n'%(m&((1<<64)-1),m>>64)) for m in s2]
