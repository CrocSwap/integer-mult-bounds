import sys,json,gzip
from collections import Counter
sys.path.insert(0,'.')
from emit_word import *
def main(canon,blocksf,witf,out,base_name):
    w=json.loads(gzip.decompress(Path(canon).read_bytes()))
    blocks=json.loads(Path(blocksf).read_text())['sources'][0]['blocks']
    wit=json.loads(Path(witf).read_text())
    S=build(w,blocks,wit);S=finish(S)
    word=assemble(S,base_name)
    ops=[x[5] for x in sorted(S['warps'],key=lambda x:x[5])];assert ops==list(range(1,len(ops)+1)),ops
    del word['warp_order']
    v=S['v'];n=S['n'];restored=set(S['restored']);full=frame_basis(S['full'])
    # explicit cleanup: inverse-reverse at FULL
    fw=[]
    byp={}
    for x in S['warps']:byp.setdefault(x[0],[]).append(x[5])
    for g in word['A']:fw.append(g)
    for p in range(len(word['B'])+1):
        for op in sorted(byp.get(p,[])):fw.append(['warp',S['warps'][[x[5] for x in S['warps']].index(op)][1],op])
        if p<len(word['B']):fw.append(word['B'][p])
    fw+=word['restore']
    rec=[g for g in fw if g[0]=='warp' or not(v<=g[1]<2*v)]
    buf=lambda r:r+n if r in restored else r
    cl=[]
    for g in reversed(rec):
        if g[0]=='warp':cl.append(['warp',buf(g[1]),-g[2],full])
        elif g[0]=='add':cl.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],full])
        else:cl.append(['scale',buf(g[1]),g[3],g[2],full])
    word['cleanup']=cl
    # claimed report: profile from Borrow's witness replay, inventory counted here
    word['report']['local_profile']=wit['replay']['local_profile']
    end_dim=lambda r:(len(word['helper_final'][str(r)]) if str(r) in word['helper_final'] else w['h'])
    st_dim=lambda r:len(word['start_extra'].get(str(r),[]))
    inv=Counter(end_dim(r)-st_dim(r) for r in range(2*v,n) if r not in S['removed'])
    word['report']['width_inventory']=dict(sorted(inv.items()))
    Path(out).write_bytes(gzip.compress(json.dumps(word,separators=(',',':')).encode()))
    print('wrote',out,len(word['B']),len(word['cleanup']),len(word['warps']),len(restored))
if __name__=='__main__':main(*sys.argv[1:])
