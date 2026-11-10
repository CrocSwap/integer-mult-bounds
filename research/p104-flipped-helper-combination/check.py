"""Regenerate and audit the exact composition of #6916's method with #6917.

The search supplies witnesses, not accepted identities. Every cut is checked
by forward prefix propagation and the retained reverse-functional checker.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
import argparse, json
from linear import HERE, canonical, digest, load, need, read, replay
from construct import construct
from pricing import caller_invoice, root_invoice, ordinary_bound


def pins():
    manifest=read(HERE/'SOURCE-PINS.json')['files']
    declared=[r['local'] for r in manifest]
    actual={str(p.relative_to(HERE)) for p in (HERE/'retained').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(len(declared)==len(set(declared)) and set(declared)==actual,'Complete unique retained source pins')
    for row in manifest:
        b=(HERE/row['local']).read_bytes()
        need(sha256(b).hexdigest()==row['sha256'],'Retained SHA256 '+row['local'])
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'Retained Git blob '+row['local'])


def height(word,caller):
    def ceil_log(q):
        k=0
        while (1<<k)*q.denominator<q.numerator:k+=1
        return k
    from fractions import Fraction as Q
    native=0
    for e in word['program']:
        if e[0] in ('ADD','COPY','SCALE'):
            q=Q(e[-2]);a=abs(q)
            native+=ceil_log(max(Q(1),a) if e[0]=='SCALE' else 1+a)+q.denominator.bit_length()-1
    per_type={ty:0 for ty in caller['types']}
    for e in caller['events']:
        if e[0]=='J':continue
        ty,op=e[:2]
        if op=='LAMBDA':per_type[ty]+=8
        elif op=='QUERY':per_type[ty]+=16
        elif op=='SWAP':per_type[ty]+=4
        elif op in ('ADD','SCALE'):
            q=Q(e[-1]);per_type[ty]+=ceil_log(max(Q(1),abs(q)) if op=='SCALE' else 1+abs(q))+q.denominator.bit_length()-1
    return dict(native=native,caller_per_port=per_type,complete=18*native+sum(len(caller['types'][ty]['ports'])*v for ty,v in per_type.items()))


def receipt(word):
    source=read(HERE/'retained/data/word.json.gz');caller=read(HERE/'retained/data/caller.json')
    native=replay(word,source)
    from fractions import Fraction as Q
    need(caller['types']['A']['ports']==word['hosted']['Dports'],'Exact ordered A-port binding')
    need(Q(caller['types']['A']['alpha2'])==Q(word['hosted']['alpha2']) and Q(caller['types']['A']['beta2'])==0,'Same second-plane native coefficients')
    joints=[e for e in caller['events'] if e[0]=='J']
    need([e[1] for e in joints]==list(range(1,19)),'Ordered joint stages')
    for e in joints:
        need(len(e[2])==len(set(e[2]))==4 and all(0<=r<40 for r in e[2]),'Four distinct type-A roles')
        need(len(set(e[3][:2]))==2 and all(40<=r<78 for r in e[3][:2]),'Two distinct type-B roles')
        need(tuple(map(Q,e[3][2:]))==(Q(word['hosted']['alpha']),Q(word['hosted']['beta'])),'Every joint has the checked hosted native coefficients')
    t,p=caller_invoice(word,caller)
    rt,rp=root_invoice(word,[(read(HERE/'retained/data/root_A.json'),96),(read(HERE/'retained/data/root_B.json'),8)])
    need(+t==+rt and +p==+rp,'Literal caller and separate root invoices agree')
    edges=lambda w:Counter(tuple(e[2:]) for e in w['program'] if e[0]=='MOVE')
    need(edges(word)==edges(source),'All source paid operators retain multiplicity')
    need(native['owned_fields']==51 and native['owned_lifetimes']==54 and native['peak_owned_fields']==30 and native['dirty_owned_clears']==53,'Inherited owned storage and dirty erasure census')
    need(sum(native['owned_ascent'].values())==23 and sum(int(r)*n for r,n in native['owned_ascent'].items())==56,'All inherited owned rises remain paid')
    mass=sum(r*(t[r]-p[r]) for r in set(t)|set(p))
    need(mass==1520,'Complete rank surplus')
    cost=ordinary_bound(word,caller,native)
    need(cost['full_ordinary_upper']<10**9,'Complete ordinary allowance including LAMBDA')
    from compress_caller import construct as compress
    compressed=compress()
    need(compressed==read(HERE/'CALLER-COMPRESSED.json'),'Exact compressed mixed caller regenerated')
    ct,cp=caller_invoice(word,compressed)
    need(+ct==+t and +cp==+p,'Compressed caller has the same complete recursive invoice')
    compressed_cost=ordinary_bound(word,compressed,native)
    need(cost['full_ordinary_upper']-compressed_cost['full_ordinary_upper']==159498240,'Full ordinary saving of the source-bound A block replacement')
    return dict(word_payload_sha256=digest(word),native=native,T=t,P=p,
                productive_fields=sum(t.values()),paid_jobs=sum(p.values()),rank_surplus=mass,
                paid_rank_mass=sum(r*n for r,n in p.items()),ordinary=cost,log_height=height(word,caller),
                compressed_ordinary=compressed_cost,compressed_log_height=height(word,compressed))


def rejects(fn):
    try:fn()
    except (ValueError,KeyError):return True
    return False


def controls():
    d=load(HERE/'retained/6916/independent_directional.py','composition_cut_controls')
    source=read(HERE/'retained/data/word.json.gz');first=read(HERE/'WITNESSES.json')[0]
    altered=deepcopy(first);key=next(iter(altered['witness']['a']));altered['witness']['a'][key]='999'
    bad=deepcopy(first);bad['source_payload_sha256']='0'*64
    wrong_owner=deepcopy(first);wrong_owner['witness']['paths'][0]['role']+=1
    across_contact=deepcopy(first);across_contact['witness']['paths'][0]['hi']+=1
    word=read(HERE/'WORD.json.gz');caller=read(HERE/'retained/data/caller.json')
    inv=receipt(word);missing=deepcopy(word)
    del missing['program'][next(i for i,e in enumerate(missing['program']) if e[0]=='MOVE')]
    swap=deepcopy(caller);swap['types']['A']['ports'][0],swap['types']['B']['ports'][0]=swap['types']['B']['ports'][0],swap['types']['A']['ports'][0]
    result={'wrong_cut_functional':rejects(lambda:construct(source,altered['witness'])),
            'wrong_source_hash':rejects(lambda:d.check_cut(source,bad)),
            'wrong_retiming_owner':rejects(lambda:d.prepare(source,wrong_owner)),
            'retiming_across_contact':rejects(lambda:d.prepare(source,across_contact)),
            'wrong_port_assignment':rejects(lambda:ordinary_bound(word,swap,inv['native'])),
            'omitted_paid_MOVE':rejects(lambda:replay(missing,source))}
    need(all(result.values()),'All composition controls reject')
    print(json.dumps(result,sort_keys=True));print('PASS_COMPOSITION_CONTROLS')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');a=ap.parse_args()
    pins()
    if a.controls_only:controls();return
    source=read(HERE/'retained/data/word.json.gz');word=source
    d=load(HERE/'retained/6916/independent_directional.py','composition_cut_audit')
    audits=[]
    for i,entry in enumerate(read(HERE/'WITNESSES.json'),1):
        need(digest(word)==entry['source_payload_sha256'],'Witness input identity')
        audits.append(d.check_cut(word,entry))
        word,prepared=construct(word,entry['witness'])
        need(prepared==entry['prepared_split'] and digest(word)==entry['payload_sha256'],'Witness output identity')
        if i%10==0:print('CHECKED_CUTS',i,flush=True)
    need(word==read(HERE/'WORD.json.gz'),'Complete reconstructed word')
    result=receipt(word);expected=read(HERE/'RESULT.json')
    need(json.loads(json.dumps(result))==expected['construction'],'Complete source-bound result reproduced')
    need(json.loads(json.dumps(audits))==read(HERE/'CUT-AUDIT.json'),'Separate reverse-functional/COPY-guard receipts')
    print(json.dumps(dict(cuts=len(audits),retimed_moves=sum(a['retimed_MOVEs'] for a in audits),copy_guards=sum(a['future_COPY_zero_guards'] for a in audits),full_ordinary_upper=result['ordinary']['full_ordinary_upper']),sort_keys=True))
    print('PASS_FLIPPED_HELPER_COMBINATION')


if __name__=='__main__':main()
