"""Independent finite address maps and allocation, with no upstream imports."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib,time,sys
H=Path(__file__).resolve().parent; R=H.parents[1]
RAW=R/'research/coordinated-frames-and-entrance-banks'; sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(c,m):
    if not c:raise ValueError(m)
def chart(v,sign):
    # Same unimodular coordinate shear on both banks; inverse has sign -1.
    z=v[:]
    for offset in (0,72):z[offset]+=sign*z[offset+71]
    return z
def apply(v,width,block,weighted=False,ring=0):
    z=chart(v,-1) if weighted else v[:]
    for j in range(block*width,(block+1)*width):z[j],z[j+72]=z[j+72],z[j]
    if weighted:z=chart(z,1)
    return [x%ring for x in z] if ring else z
def run(v,width,indices,ring,charts):
    for p,b in enumerate(indices):v=apply(v,width,b,charts[p],ring)
    return v
def validate(width,indices,ring,charts,restore=False):
    for k in range(144):
        v=[int(j==k) for j in range(144)]
        got=run(v,width,indices,ring,charts)
        expected=v if restore else [int(j==(k+72)%144) for j in range(144)]
        need(got==expected,'restore column '+str(k) if restore else 'endpoint column '+str(k))
    return 144
def reject(f):
    try:f()
    except ValueError as e:return str(e)
    raise ValueError('negative control unexpectedly accepted')
def main():
    from source_binding import check_sources
    check_sources()
    start=time.monotonic(); checks=[]
    for width in (4,24):
        count=72//width; indices=list(range(count)); row={'width':width,'blocks':count,'rings':{}}
        for ring in (0,2):
            c={}
            for weighted in (False,True):
                charts=[weighted]*count
                c[str(weighted)]={'endpoint_columns':validate(width,indices,ring,charts),'inverse_columns':validate(width,indices+indices[::-1],ring,charts+charts[::-1],True)}
            c['controls']={'omit':reject(lambda:validate(width,indices[:-1],ring,[False]*(count-1))),
                'repeat':reject(lambda:validate(width,indices+[count-1],ring,[False]*(count+1))),
                'inconsistent_common_chart':reject(lambda:validate(width,indices,ring,[False]*(count-1)+[True]))}
            row['rings'][str(ring)]=c
        checks.append(row)
    source=json.loads((RAW/'SOURCE.json').read_bytes())['files']; paths=['references/paired-cube/bit-physical/word_p12.json.gz','research/paired-cube-bit/out/profile_p12.json']
    for p in paths:need(sha(R/p)==source[p],'pinned native byte '+p)
    w=json.loads(gzip.decompress((R/paths[0]).read_bytes())); original=json.loads((R/'research/precision-certificate/inputs/paired-cube-bit-physical-input.json').read_bytes()); prof=json.loads((R/paths[1]).read_bytes())
    gauges={z['role']:z for z in w['gauges']}; pairs=w['pairs']; donors={a for a,b in pairs}; recipients={b for a,b in pairs}
    need(len(gauges)==len(w['gauges']) and len(pairs)==len(donors)==len(recipients)==1760 and not donors&recipients,'one-to-one disjoint aliases')
    need(not donors&set(gauges) and not donors&set(w['rootroles']),'donors are ungauged nonroots')
    need(all(b in gauges and gauges[b]['dim']==21 for b in recipients),'all rank21 recipient gauges internal')
    starts={s:z for s,z in gauges.items() if s not in recipients}
    need(len(starts)==2200 and all(z['dim']==20 for z in starts.values()),'2200 physical rank20 entrances only')
    # Reconstruct the native actual chronological positions, without native code.
    phase=sorted(w['phase1']); phase_set=set(phase); order=phase+[i for i in range(len(w['ops'])) if i not in phase_set]
    first={};last={}
    for position,i in enumerate(order):
        for s in w['ops'][i][:2]:first.setdefault(s,position);last[s]=position
    reads={int(s):p for s,p in w['reads'].items()}
    need(all(last[a]<reads.get(b,len(phase))<=first[b] for a,b in pairs),'donor dead/read/first recipient deadline')
    physical={s:next((a for a,b in pairs if b==s),s) for s in range(prof['R'])}
    need(prof['R']==19788 and len(set(physical.values()))==18028,'physical chain count')
    rest=18028-len(starts);need(rest==15828,'all undeferred physical chains')
    bank=json.loads((RAW/'bit/banks.json').read_bytes()); Hbefore={int(k):n for k,n in original['child_histogram'].items()}; Hpaid={int(k):n for k,n in bank['profile']['child_multiplicities'].items()}
    removed=Hbefore.pop(60);need(removed==2200 and Hpaid==Hbefore,'only entrance exteriors removed')
    W=2*1760+3*(Q(2200,18)+Q(rest,3)); mass=sum(r*n for r,n in Hpaid.items()); count=sum(Hpaid.values())
    need(W==Q(59144,3) and mass==1417520 and 72*W-mass==1936 and max(Hpaid)==22 and count==296710,'normalized stock/rank/deficit')
    need(Q(bank['profile']['W_per_vertex'])==W and bank['profile']['rank_per_vertex']==mass and bank['profile']['edge_count']==count,'stored bank inventory')
    need(9*2200%18==0 and 9*rest%3==0,'nine replicas integral per stage')
    selected=9*2200//18; undeferred=9*rest//3;stock=3*(selected+undeferred)+2*9*1760
    need((selected,undeferred,stock)==(1100,47484,177432) and stock==9*W,'literal nine-copy stock')
    # Every coefficient of the characteristic and contaminated fallback is unchanged by uniform scale3.
    need(all(Q(3*n,3*W*72)==Q(n,W*72) for n in Hpaid.values()),'paid characteristic scale')
    fallback=32*72**2;bad=Q(1,10**16)
    need(Q(fallback*3*count,3*W*72)==Q(fallback*count,W*72),'fallback edge-count scale')
    need(Q(3*1936,3*W*72)==Q(1936,W*72),'deficit scale')
    controls={'eight_replicas_not_integral':reject(lambda:need(8*2200%18==0,'selected bank allocation nonintegral')),
      'rank21_as_new_entrances':reject(lambda:need(len(starts)+len(recipients)==2200,'recipient splice double counted')),
      'omit_rank21_children':reject(lambda:need({r:n for r,n in Hpaid.items() if r!=21}==Hbefore,'retained internal rank21 children deleted')),
      'fallback_count_unscaled':reject(lambda:need(Q(fallback*count,3*W*72)==Q(fallback*count,W*72),'fallback bill divided by3'))}
    result={'status':'finite_bank_endpoint_and_allocation_pass','optimized':bool(sys.flags.optimize),'address_maps':checks,'all_basis_columns_per_ring':144,'native_input_sha256':{p:sha(R/p) for p in paths},'bank_profile_sha256':sha(RAW/'bit/banks.json'),'original_histogram_sha256':sha(R/'research/precision-certificate/inputs/paired-cube-bit-physical-input.json'),'allocation':{'logical_roles':19788,'physical_roles':18028,'aliases':1760,'entrance_rank20':2200,'recipient_rank21_internal':1760,'undeferred_roles':rest,'replicas':9,'selected_banks_per_stage':selected,'undeferred_banks_per_stage':undeferred,'literal_stock':stock,'normalized_stock':str(W),'mass':mass,'deficit':1936,'removed_rank60':removed,'retained_child_histogram':Hpaid,'retained_rank21_children':Hpaid[21],'edge_count':count},'scale3':{'stock':int(3*W),'mass':3*mass,'deficit':3*1936,'edge_count':3*count,'fallback_children_per_edge':fallback,'bad_fraction':str(bad),'characteristic_and_fallback_coefficients_unchanged':True},'ledger_controls':controls,'seconds':time.monotonic()-start,'scope':'Exact finite address maps/inverses over Z and F2 and declared replica allocation; native word byte pins and physical entrance classes/deadlines only. No producer/native module imported; no weighted compiler, tensor/Clifford, common-chart existence, multibank paid routing/restoration, all-size or new moment acceptance.'}
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
