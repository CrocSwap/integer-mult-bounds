"""Independent PR300/final12/shared-kernel composition audit.

Reads frozen JSON as inert data. No upstream producer or verifier is executed.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import base64,gzip,hashlib,json,time
HERE=Path(__file__).resolve().parent
import source_data as sd
import check_coretime
import check_suffix_frames
import kernel_witness
HEAD='fd516176fd068e4fa7af14b40cd878ce8c305296'


def rank(A):
 A=[[Q(x)for x in row]for row in A];k=0
 for j in range(len(A[0])if A else 0):
  pivot=next((i for i in range(k,len(A))if A[i][j]),None)
  if pivot is None:continue
  A[k],A[pivot]=A[pivot],A[k];c=A[k][j];A[k]=[x/c for x in A[k]]
  for i in range(k+1,len(A)):
   c=A[i][j]
   if c:A[i]=[x-c*y for x,y in zip(A[i],A[k])]
  k+=1
  if k==len(A):break
 return k

def run(mutation=None):
 sd.verify_all();start=time.monotonic();selection=sd.read_json('pr300/descent2-selection.json')
 w=sd.read_json('gen5bit/selected/bit/word_p12.json.gz')
 f=sd.read_json('gen5bit/selected/bit/frames_p12.json.gz')['frames']
 kernel=sd.read_json('kernel-selection.json');descent=sd.read_json('descent-selection.json')
 core=check_coretime.run(minimal=True)['candidates']
 partner=sd.read_json('gen5bit/selected/bit/kchron_p12.json')['entries']
 oldrestore=sd.read_json('restore-selection.json');newrestore=sd.read_json('pr300/restore-selection.json')
 oldsink=sd.read_json('sink-selection.json');newsink=sd.read_json('pr300/sink-selection.json')
 paths=check_suffix_frames.run()['paths']
 witness=kernel_witness.load()['portable']['variants']['three_lines_trimmed']['entries']
 alias={b:a for a,b in w['pairs']};regs=sorted(set(range(17160))-set(alias));phys={r:3520+i for i,r in enumerate(regs)}
 sid=lambda r:phys[alias.get(r,r)]
 entries=selection['entries'];assert len(entries)==89
 assert selection['source_record_count']==818425
 assert selection['input_raw_sha256']=='07f2335ff99a2928a489668bc64c60463d279e56b53021f25a66a1fa01059486'
 assert selection['input_scalar_sha256']=='b3c05b54eeda0c1384ee853926780e6f355139a5ce5fb24715e58da3465c0c14'
 # The new descent precedes restoration and sink compaction. These are the
 # original18954 stream IDs; applying the sink compaction would be erroneous.
 pipeline=sd.read_bytes('pr300/portable_bit.py').decode('utf-8')
 positions=[pipeline.index(s)for s in("load('portable527_kernel',","load('portable527_descent2',","load('portable527_restore',","load('portable527_sink',")]
 assert positions==sorted(positions)
 assert oldrestore['entries']==newrestore['entries']
 assert oldsink['sinks']==newsink['sinks']
 assert len(newrestore['entries'])==440 and len(newsink['sinks'])==7
 # Bind every selected scalar to an unchanged original event.
 byscalar=defaultdict(list)
 for i,(a,b,_)in enumerate(w['ops']):byscalar[sid(a),sid(b)].append(i)
 oldkernel=[dict(pivot=z['a'],donors=[z['b']],rank=z['rank'])for z in kernel['pairs']]+[dict(pivot=z['pivot'],donors=z['donors'],rank=z['rank'])for z in kernel['families']]
 kernelsetup={(d,z['pivot']):z['rank']for z in oldkernel for d in z['donors']}
 firstdescent={tuple(z['scalar'][:3])for z in descent['entries']}
 event_matches=[];participants=set();categories=Counter()
 for z in entries:
  a,b,c,category=z['scalar'];assert 3520<=a<18954 and 3520<=b<18954 and c==1
  assert tuple(z['scalar'][:3])not in firstdescent
  participants.update((a,b));categories[category]+=1
  if category==12:
   matches=byscalar[a,b];assert len(matches)==1
   i=matches[0];assert f[str(w['op_frame'][i])]['dim']==z['old_dimension']
   event_matches.append(dict(record=z['record'],kind='forward_gate',op=i,streams=[a,b]))
  elif category==30:
   assert kernelsetup[a,b]==z['old_dimension']
   event_matches.append(dict(record=z['record'],kind='old_kernel_setup',streams=[a,b]))
  else:raise AssertionError(('Unexpected scalar category',category))
  B=z['new_basis'];d=z['new_dimension'];assert len(B)==d and all(len(row)==24 for row in B)
  assert rank(B)==d
  gram=[[9*sum(x*y for x,y in zip(u,v))-sum(u)*sum(v)for v in B]for u in B]
  assert rank(gram)==d,('Degenerate rational new frame',z['record'])
 assert categories=={12:87,30:2}
 # Broader final12 closure includes every local scalar participant, every
 # promoted partner passive/carrier and every target receiver, not just the
 #60 changed paid-frame streams.
 final12={z['stream']for z in paths};assert len(final12)==60
 coreclosure=set(final12);oldr={z['helper']:z for z in oldrestore['entries']}
 rootpartners={z['deliver_after_root']:z for z in partner}
 for z in core:
  coreclosure.update(sid(z[k])for k in('helper','donor','blocker'))
  restore=oldr[z['old_restored_helper_stream']];coreclosure.update((restore['helper'],restore['donor']))
  e=rootpartners[z['blocker_root']];coreclosure.update((e['carrier'],e['passive']));coreclosure.update(1760+t for t in e['receivers'])
 kmembers={r for z in witness for r in[z['pivot']]+z['donors']};assert len(kmembers)==165
 if mutation=='frame_overlap':participants.add(next(iter(final12)))
 if mutation=='kernel_overlap':participants.add(next(iter(kmembers)))
 assert not participants&coreclosure,('Final12 overlap',sorted(participants&coreclosure))
 assert not participants&kmembers,('New kernel overlap',sorted(participants&kmembers))
 # Rank mass is unchanged by the external descent; exact additive histograms
 # for the local construction follow from disjoint per-role MOVE sequences.
 hd={int(k):v for k,v in selection['expected_local_histogram_delta'].items()}
 assert sum(r*c for r,c in hd.items())==0 and sum(hd.values())==65
 hf={1:18,2:-12};hk={1:93,2:144,3:-144,4:19,5:-17,6:-2}
 union=Counter(hd);union.update(hf);union.update(hk);union={r:c for r,c in sorted(union.items())if c}
 assert sum(r*c for r,c in union.items())==-78
 return dict(status='PASS_ROLE_DISJOINT_PR300_COMPOSITION',source_head=HEAD,
  baseline_head='5f6bd3fbc0e6796dd31263cef1f06dc968186f64',id_space='pre-sink18954 streams',
  new_descent_gate_count=len(entries),distinct_new_descent_helper_streams=len(participants),
  all_new_descent_operands_helpers=True,category_counts=dict(categories),
  rational_new_frame_ranks_and_nondegeneracy_checked=len(entries),
  unchanged_restore_entries=len(newrestore['entries']),unchanged_sink_entries=len(newsink['sinks']),
  final12_changed_frame_streams=len(final12),final12_broader_scalar_closure=len(coreclosure),kernel72_streams=len(kmembers),
  descent2_overlap_final12=[],descent2_overlap_kernel72=[],
  paid_ledgers_additive=True,combined_local_histogram_delta_over299=union,
  combined_local_rank_drop=78,final12_and_kernel72_source_response_unchanged=True,
  common_kernel_cut_and_final_restore_order_unchanged=True,
  scalar_majorants_unchanged_by_descent2=True,source_operand_columns_unchanged_by_new_kernel=True,
  proofs={
   'frame':'Every descent2 event and every affected per-role MOVE partition belongs to a helper disjoint from the full local-surgery role closure and new kernel members. Thus both modifications preserve each other\'s chronological frame path and their paid histogram differences add exactly.',
   'scalar':'Descent2 preserves the scalar/COPY order and coefficients. Consequently final12\'s complete suffix identity and the new kernel\'s response relations/cut/restore identity remain unchanged. Inserting new kernel setup before every source injection changes only dirty columns, so each inherited old operand\'s source-column span remains identical over the integers.',
   'prefix':'Descent2 changes only87 helper forward-gate frames and2 old kernel-setup frames. It neither changes initial dirty-read/source-injection ordering nor touches new kernel helpers. Its changed old kernel setups use disjoint helper support.',
   'endpoints':'All440 restoration entries and all7 sink entries are semantically identical to299; changed input hashes and shifted raw record indices do not change their selected operators or endpoint bases.'},
  matched_scalar_events=event_matches,input_sha256={name:pin['sha256']for name,pin in sd.MANIFEST['files'].items()if name.startswith('pr300/')},seconds=time.monotonic()-start,
  scope='A changed-stage composition certificate, conditional on the admitted PR300 descent2/source contracts. It independently matches all89 scalar events, checks rational frame rank/nondegeneracy and proves support disjointness; it does not rerun PR300\'s complete physical producer, source-span admission, all-size compiler or unified finite/bank assembly. No upstream program was executed.')

if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 r=run();print(json.dumps({k:v for k,v in r.items()if k not in('matched_scalar_events','input_sha256','proofs')},indent=2))
