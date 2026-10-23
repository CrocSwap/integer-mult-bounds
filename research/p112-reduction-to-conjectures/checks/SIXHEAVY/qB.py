import json, subprocess, sys, time
D=json.load(open('../SIXHEAVY/B.json'))
def qB(t, dims, timeout=1200):
    O=D['types'][t]
    inp=' '.join(map(str,D['labels']))+'\n%d %s\n%d %s\n'%(len(O),' '.join(map(str,O)),len(dims),' '.join(map(str,dims)))
    r=subprocess.run(['../SIXHEAVY/covB'],input=inp,capture_output=True,text=True,timeout=timeout)
    return r.stdout.strip()
if __name__=='__main__':
    for a in sys.argv[1:]:
        t,ds=a.split(':'); t0=time.time(); out=qB(t,[int(x) for x in ds.split(',')])
        print(a, out[:60], round(time.time()-t0,1), flush=True)
