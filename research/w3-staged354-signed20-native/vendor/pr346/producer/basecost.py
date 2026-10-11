"""Fast proxy: base compile (graph + HK carrier arcs + extension + compile_closure + select) of the complex word."""
import sys, json, time, math
from pathlib import Path
root=Path('/home/claude/cx/tree')
sys.path.insert(0,str(root/'scripts')); sys.path.insert(0,'/home/claude/cx/pr233'); sys.path.insert(0,'/home/claude/cx')
from paired_cube.graph import Graph
from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from, merge_outputs
from paired_cube.closure import compile_closure
from paired_cube.gauges import select
from matching import carrier_matching
from extend_floor import extended_arcs
def base(P,tmod,pmod,qmod,T=None,PM=None,Q=None):
    local=json.loads((root/'references/paired-cube/sources/local_L1.json').read_text())
    local['G']={k:'s' for k in local['G']}; local['A']={k:'fd' for k in local['A']}
    b=Graph(P,local=local)
    g=b.finish(T or triple_module_from(tmod,P), PM or pair_module_from(pmod,P-1), Q or all_but_one_from(qmod,P-2))
    g=merge_outputs(g,b,'f8:00111100'); g['matching_frames']='coordinate'
    v=g['v']; newcut=v+g['counts']['local_channel_additions']
    arcs,stats=carrier_matching(g,'reverse'); arcs=[x for x in arcs if x[0]>newcut]; arcs=extended_arcs(g,arcs,min_donor=newcut+1)
    p,w=compile_closure(g,arcs); row,word=select(g,p,w)
    return p,row
if __name__=='__main__':
    M='/home/claude/cx/mods/'
    for tag,(t,pm,q) in dict(L10=('tmod_p10.json','pmod37_p10.json','qmod_p10.json'),L10b=('tmod_p10.json','bit_pm_p10.json','bit_qmod_p10.json'),
                            L10c=('tmod_p10.json','bit_pm_p10.json','qmod_p10.json'),L10d=('tmod_v2_p10.json','bit_pm_p10.json','bit_qmod_p10.json')).items():
        t0=time.time(); p,row=base(10,M+t,M+pm,M+q)
        flow=json.load(open('/home/claude/cx/%s/tree-mw/flow.json'%tag))
        print(tag,'base R',p['R'],'row keys',[k for k in row][:8],'| flow new_R',flow['new_R'],'| %.1fs'%(time.time()-t0),flush=True)

def proxy(p,row,h,v):
    """first-order five-stage proxy from the base profile: D/E with W=4v+R, using the base child histogram if present"""
    return p, row
