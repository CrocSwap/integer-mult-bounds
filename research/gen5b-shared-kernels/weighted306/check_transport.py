"""Independent changed-stage transport. Upstream programs remain inert text.

The pinned PR306 raw crossing/full-word admission is an inherited contract.
We prove its preservation, not an independent regeneration of every raw record.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import ast,bisect,copy,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent
from context306 import INPUTS,OUTPUT,read_new as load,verify_new,oldsource
import check_bridge as oldbridge
import check_scalar_bounds as oldnorm
from transport_witness import build
CAND=OUTPUT/'candidate156.json'
HEAD='0314371983b8837f01723f5af2c70217f75b01cc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hist(ds):return Counter(b-a for a,b in zip(ds,ds[1:])if b>a)
def verify():
 verify_new();oldbridge.configure('156');build()
 oldbridge.verify_sources();manifest=load('MANIFEST.json')['files']
 pins=oldsource.pins()['files']
 # All data defining the initial word, common cut, old kernels, and alias paths.
 same=['gen5bit/selected/bit/word_p12.json.gz','gen5bit/selected/bit/frames_p12.json.gz','gen5bit/selected/bit/graph_p12.json','gen5bit/selected/bit/kchron_p12.json','kernel-selection.json','descent-selection.json','descent2-selection.json','target-selection.json','restore-selection.json','sink-selection.json','kernel_transform.py','restore_transform.py','sink_transform.py','scalar_check.py']
 for n in same:assert manifest[n]==pins[n]['sha256'],('Inherited source changed',n)
 assert sha(CAND)=='fc38ee603065d80c84ac5fa3d699126b2b124fbc1b5cbb180666d3d8137b73c4'
 c=json.loads(CAND.read_text());assert c['source_head']==HEAD
 assert c['entries']==json.loads(oldbridge.CAND.read_text())['entries']
 return same

def run(prior_bridge=None,prior_norm=None):
 start=time.monotonic();same=verify();base=prior_bridge if prior_bridge is not None else oldbridge.run();norm=prior_norm if prior_norm is not None else oldnorm.run()
 w=oldbridge.read('gen5bit/selected/bit/word_p12.json.gz');g=oldbridge.read('graph.json');f={int(k):v for k,v in oldbridge.read('frames.json')['frames'].items()}
 sink=oldbridge.read('sink-selection.json');removed=sorted(z['stream']for z in sink['sinks']);compact=lambda s:s-bisect.bisect_left(removed,s)
 selected={compact(z['stream']):z for z in base['selected_paths']};assert len(selected)==353 and not set(selected)&set(removed)
 rounds=[load('reorder-selection.json'),load('reorder2-selection.json')]
 assert [x['selected']for x in rounds]==[237,2] and all(x['n']==18944 and x['v']==1760 for x in rounds)
 oldpins=oldbridge.read('expected/kernel-pins.json');newpins=load('expected/kernel-pins.json')
 assert rounds[0]['input_scalar_sha256']==oldpins['scalar_event_sha256']
 assert (newpins['forward_max_row_l1'],newpins['inverse_max_row_l1'])==(oldpins['forward_max_row_l1'],oldpins['inverse_max_row_l1'])==(86453,2766560)
 # Static source-placement binding. The retained scalar program performs all
 # initial ungauged reads before its first source injection or copied centre.
 textpath=INPUTS/'scalar__word.py.txt'
 text=textpath.read_text();assert sha(textpath)==load('MANIFEST.json')['files']['scalar/word.py'];ast.parse(text)
 plain=text.index('for s in range(W.R):');inject=text.index('for n,s in W.source.items():assign(s,add(value(s),1,x[n]))')
 assert plain<inject and 'read(s)'in text[plain:inject]
 assert 'if s not in W.gauge' in text[plain:inject]
 # Other prefix transformations insert no scalar events before this boundary;
 # kernel setups are the sole exception. A setup ADD emits at most two MOVEs.
 ks=oldbridge.read('kernel-selection.json');setups=len(ks['pairs'])+sum(len(e['donors'])for e in ks['families']);assert setups==2931
 raw_prefix_upper=base['literal_prefix_plain_reads']+3*setups;assert raw_prefix_upper==656881
 targets=oldbridge.read('target-selection.json');assert targets['cut_record']>base['literal_prefix_plain_reads']
 # Sink entry is defined after the last copied-centre block, hence after the cut.
 sinktext=(oldbridge.P/'sink_transform.py.txt').read_text()
 assert 'entry=max(k//6 for k in range(0,len(old),6)if old[k]==3)'in sinktext
 separation=[];overlaps=[];newpaths=copy.deepcopy(base['selected_paths']);by_stream={z['stream']:z for z in newpaths};anncache={}
 def ann(k):
  if k not in anncache:anncache[k]=f[k]['a']if'a'in f[k]else oldbridge.null(f[k]['b'])
  return anncache[k]
 def contains_basis(k,B):return all(sum(Q(x)*Q(y)for x,y in zip(a,b))==0 for a in ann(k)for b in B)
 for rnd,sel in enumerate(rounds,1):
  occupied=set()
  for e in sel['moves']:
   a,b,c=e['incidence'];assert a!=b and b!=sel['n'] and not({a,b}&occupied);occupied|={a,b}
   i,t=e['record'],e['anchor'];assert (e['side']=='before'and t>i)or(e['side']=='after'and t<i)
   lo,hi=min(i,t),max(i,t);assert lo>raw_prefix_upper
   hits={a,b}&set(selected)
   if not hits:continue
   assert rnd==1 and e['category']=='side_root' and hits=={b} and a<3520<=b
   z=selected[b];assert z['aliased_recipient'] is None and e['old_frame_rank']==21 and e['frame_rank']==22
   r=z['role'];j=w['rootroles'].index(r);root=g['roots'][j]
   assert root['kind']=='side' and a==1760+root['targets'][0]
   assert z['dimensions'][-2:]==[21,24] and z['frames'][-2]==w['root_frame'][j]
   # The new rank22 frame is the next side-root incidence of this exact target.
   nxt=next(k for k in range(j+1,len(g['roots']))if g['roots'][k]['kind']=='side'and a-1760 in g['roots'][k]['targets'])
   F=w['root_frame'][nxt];B=e['frame_basis'];assert f[F]['dim']==22 and len(oldbridge.rr(B)[0])==22 and contains_basis(F,B)
   R=z['frames'][-2];basisR=oldbridge.null(ann(R));assert contains_basis(F,basisR),'old terminal21 not inside new22'
   assert contains_basis(F,z['entrance_basis'])
   olddim=[0]+z['dimensions'];newdim=olddim[:-1]+[22,24]
   basechange=hist(newdim);basechange.subtract(hist(olddim));basechange={k:v for k,v in basechange.items()if v}
   assert basechange=={1:1,2:1,3:-1}
   def kernel_delta(ds):
    x=hist([1]+ds[1:]);x.subtract(hist(ds))
    if z['kernel_kind']=='donor':x[1]+=1
    return {k:v for k,v in x.items()if v}
   assert kernel_delta(olddim)==kernel_delta(newdim)
   changed=by_stream[z['stream']];changed['frames']=z['frames'][:-1]+[F,z['frames'][-1]];changed['dimensions']=z['dimensions'][:-1]+[22,24]
   changed['reorder_extra_frame']=F
   overlaps.append(dict(round=rnd,record=i,anchor=t,stream=z['stream'],compact_stream=b,role=r,kernel_kind=z['kernel_kind'],old_terminal_frame=R,new_frame=F,next_root=nxt,first_frame_unchanged=True,kernel_delta_unchanged=True,source_span_unchanged_by_dirty_only_setup=True))
  separation.append(dict(round=rnd,moves=len(sel['moves']),minimum_interval_start=min(min(e['record'],e['anchor'])for e in sel['moves']),maximum_interval_end=max(max(e['record'],e['anchor'])for e in sel['moves']),raw_prefix_upper=raw_prefix_upper,all_scalar_setup_and_deleted_reads_before_entire_intervals=True,appended_inverse_after_entire_old_word=True))
 assert len(overlaps)==18 and Counter(z['kernel_kind']for z in overlaps)=={'pivot':12,'donor':6}
 assert all(z['first_frame']==next(x for x in base['selected_paths']if x['stream']==z['stream'])['first_frame']for z in newpaths)
 # Both stages preserve complete signed AND unsigned operator products under
 # their inherited crossed-interval contract. Our edits add no scalar gate to
 # those intervals, so the same commutations remain valid in the156 word.
 out=copy.deepcopy(base);out.update(status='PASS_PR306_CONDITIONAL_REORDER_TRANSPORT156',head=HEAD,candidate_sha256=sha(CAND),checker_sha256=sha(__file__),inherited305_bridge_checker_sha256=base['checker_sha256'],selected_paths=newpaths,
  unchanged_source_files=same,physical_streams_post_sink=18944,sink_compaction_removed_streams=removed,reorder_overlaps=overlaps,raw_prefix_upper=raw_prefix_upper,interval_separation=separation,
  unsigned_norm_transport=dict(forward=438151,inverse=14104135,payload=norm['payload_bound'],payload_bits=norm['payload_bits'],legacy104=False,explicit112=True,inherited_actual305_candidate_bound=True,unsigned_add_and_copy_commutation=True,augmented_majorant_word_not_reordered=True),
  inherited_reorder_contract=dict(head=HEAD,rounds=[237,2],raw_crossing_admission_inherited=True,all239_raw_crossings_independently_replayed=False,required_rule='Every crossed ADD neither reads moved destination nor writes moved source; no crossed COPY/ERASE copies moved destination; moved source is not temporary.'),
  scalar_change_boundary='All added/deleted156 ADDs are before the whole crossed interval or after the entire baseline word. Paid MOVE replacements are separate frame bookkeeping and may be inside an interval; complete affected-role paths remain admitted.',
  scope='Changed156 composition only, conditional on pinned PR306 raw crossing/full-word admission and inherited compiler/all-size interfaces. No full raw306 regeneration or239-crossing replay is claimed.',seconds=time.monotonic()-start)
 return out
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 r=run();(OUTPUT/'bridge-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['status','selected_pivots','selected_distinct_donors','local_histogram_delta','raw_prefix_upper','unsigned_norm_transport','interval_separation']},indent=2))
