"""Targeted rejection controls. @woklerx with OpenAI Codex, Apache-2.0."""
import copy,gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from engine import HERE,check_sources,load,replay,require,transform,invoice,price,Q,canonical,digest,search

def main():
    w,programs,_,_=load();cert=json.loads((HERE/'CERTIFICATE.json').read_bytes())
    candidate=json.loads(gzip.decompress((HERE/'CANDIDATE-PROGRAMS.json.gz').read_bytes()))
    names=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError):names.append(name)
        else:raise ValueError('control accepted: '+name)
    base=programs['forward'];good=candidate['forward']
    bad=copy.deepcopy(good);bad.pop(1)
    reject('missing_entry_scale',lambda:replay(bad,'forward'))
    bad2=copy.deepcopy(good);bad2.pop(-2)
    reject('missing_exit_scale',lambda:replay(bad2,'forward'))
    bad3=copy.deepcopy(good);bad3[1][1][2:4]=[4,1]
    reject('wrong_conjugation_boundary_direction',lambda:replay(bad3,'forward'))
    bad4=copy.deepcopy(good)
    for e in bad4:
        if e[0]=='scalar' and e[1][0]=='add' and ['L',427] in e[1][1:3]:
            e[1][3]*=2;break
    reject('one_unretuned_incident_coefficient',lambda:replay(bad4,'forward'))
    reject('data_register_outside_class',lambda:transform(base,w,199,2))
    reject('center_copy_helper_outside_class',lambda:transform(base,w,224,-2))
    reject('unit_discount_omitted',lambda:require(price(Q(1))==3,'actual unit cost is2'))
    before=invoice(base,'copy-init')['real_primitives'];after=invoice(good,'copy-init')['real_primitives']
    reject('boundary_scales_free',lambda:require(before-after==170,'must charge4 boundary primitives'))
    m=json.loads((HERE/'SOURCES.json').read_bytes());del m['files'][next(iter(m['files']))]
    reject('source_pin_omitted',lambda:check_sources(m))
    m2=json.loads((HERE/'SOURCES.json').read_bytes());m2['files'][next(iter(m2['files']))]='0'*64
    reject('source_pin_corrupted',lambda:check_sources(m2))
    m3=json.loads((HERE/'SOURCES.json').read_bytes());m3['selected_snapshot_sha256']='0'*64
    reject('selected_snapshot_corrupted',lambda:check_sources(m3))
    m4=json.loads((HERE/'SOURCES.json').read_bytes());del m4['archive_members'][next(iter(m4['archive_members']))]
    reject('archive_member_pin_omitted',lambda:check_sources(m4))
    reject('candidate_program_corrupted',lambda:require(digest(canonical(bad4))==cert['orientations']['forward']['candidate_sha256'],'program hash'))
    # Regression: a unit discount can defeat the lower weighted median of the
    # continuous absolute-value objective; the integer-breakpoint search wins.
    synthetic=[['scalar',['add',['L',427],['L',0],1,2],0],['scalar',['add',['L',427],['L',1],1,2],0]]
    row=search(synthetic,[427])[0]
    require(row['best_k']==1 and row['delta']==-2,'point-discount regression')
    print(json.dumps(dict(status='PASS_REJECTION_CONTROLS',rejected=names,point_discount_regression=True),sort_keys=True))
if __name__=='__main__':main()
