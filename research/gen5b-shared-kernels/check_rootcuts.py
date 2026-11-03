"""Original exact rational cut screen. Upstream inputs are JSON data only."""
from fractions import Fraction
from pathlib import Path
import base64, gzip, hashlib, json
import source_data as sd
HEAD='5f6bd3fbc0e6796dd31263cef1f06dc968186f64'

def rank(rows, width=24):
    a=[[Fraction(x) for x in row] for row in rows]
    if any(len(row)!=width for row in a): raise ValueError('Wrong row width')
    result=0
    for col in range(width):
        pivot=next((i for i in range(result,len(a)) if a[i][col]),None)
        if pivot is None: continue
        a[result],a[pivot]=a[pivot],a[result]
        scale=a[result][col];a[result]=[x/scale for x in a[result]]
        for i in range(result+1,len(a)):
            scale=a[i][col]
            if scale:a[i]=[x-scale*y for x,y in zip(a[i],a[result])]
        result+=1
    return result

def read(name):
    return sd.read_json(name.replace('__','/').removesuffix('.base64'))

def valid_witness(row):
    A,B,C=row['helper_annihilator'],row['donor_annihilator'],row['write_annihilator']
    return (row['donor_root_index']<row['helper_root_index'] and
            rank(A)==rank(B)==1 and rank(A+B)==2 and rank(C)==2 and
            rank(A+B+C)==2)

def run():
    w=read('gen5bit__selected__bit__word_p12.json.gz.base64')
    f={int(k):v for k,v in read('gen5bit__selected__bit__frames_p12.json.gz.base64')['frames'].items()}
    removed={b for a,b in w['pairs']}
    roles=sorted(g['role'] for g in w['gauges'] if g['dim']==21 and g['role'] not in removed)
    roots={}
    for index,(s,frame) in enumerate(zip(w['rootroles'],w['root_frame'])):
        roots.setdefault(s,[]).append((index,frame))
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops'])) if i not in phase]
    last={}
    for index in order:
        for s in w['ops'][index][:2]:last[s]=w['op_frame'][index]
    out=[]
    for a in roles:
        incidences=[(i,o) for i,o in enumerate(w['ops']) if a in o[:2]]
        assert len(incidences)==1
        opindex,op=incidences[0];assert op[0]==a;b=op[1]
        assert len(roots[a])==len(roots[b])==1
        ai,af=roots[a][0];bi,bf=roots[b][0]
        helper_write=w['op_frame'][opindex]
        # Donor's last forward-operation frame is the same 22-space.
        assert f[helper_write]['dim']==f[last[b]]['dim']==22
        assert rank(f[helper_write]['a']+f[last[b]]['a'])==2
        row=dict(helper_role=a,donor_role=b,write_operation=opindex,
                 helper_root_index=ai,donor_root_index=bi,
                 helper_frame_id=af,donor_frame_id=bf,write_frame_id=helper_write,
                 helper_annihilator=f[af]['a'],donor_annihilator=f[bf]['a'],write_annihilator=f[helper_write]['a'])
        assert f[af]['dim']==f[bf]['dim']==23 and valid_witness(row)
        out.append(row)
    assert len(out)==34 and len({r['helper_role'] for r in out})==34
    # A changed equal hyperplane must be rejected; no mere dimension check.
    bad=dict(out[0]);bad['donor_annihilator']=bad['helper_annihilator']
    assert not valid_witness(bad)
    return dict(status='PASS_EXACT_BASE_ROOT_CUT_SCREEN',head=HEAD,count=len(out),
       all_donors_deliver_before_helper=True,all_fixed_cut_joins_full=True,
       all_intersections_equal_common_write_frame=True,
       changed_equal_hyperplane_control_rejected=True,
       scope='Pinned base word, fixed root delivery order, monotone common-frame restoration. This does not replay the postkernel scalar word or exclude reordered/corrected/new-frame programs.',
       sources=[dict(path=n,sha256=sd.MANIFEST['files'][n]['sha256']) for n in ('gen5bit/selected/bit/word_p12.json.gz','gen5bit/selected/bit/frames_p12.json.gz')],witnesses=out)

if __name__=='__main__':
    result=run();(Path(__file__).parent/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['count'],'full joins; changed-hyperplane control rejected')
