#!/usr/bin/env python3
"""Exact portable derivative of the prior independently written event checker."""
import argparse,hashlib,json,pathlib,pprint,subprocess
p=argparse.ArgumentParser();p.add_argument('--source',type=pathlib.Path,required=True);p.add_argument('--repo',type=pathlib.Path,required=True);p.add_argument('--here',type=pathlib.Path,required=True);a=p.parse_args();S=a.source;R=a.here
OLD_SHA='73c9a7243c6dec623ced189ed3a82b16835f5935153799b9c5a1824d46b0f7f9';HEAD='d01045dfb67428679618027dff552f1d032fa999';PKG='research/gmx-t74-borrow43-handoff/'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(x,m):
 if not x:raise RuntimeError(m)
old=(R/'reference/previous_independent_events.py').read_bytes();need(sha(old)==OLD_SHA,'previous exact checker');text=old.decode();patches=[]
def patch(old,new):
 global text
 need(text.count(old)==1,'unique preimage: '+old[:100]);text=text.replace(old,new);patches.append({'old':old,'new':new})
pins={}
for name,path in {'NOTICE':'NOTICE','source-readme.md':'README.md','old-claim.json':'outer/OUTER-CLAIM.json','old-order.json':'new/borrow-fill/ORDER.json','old-dispatch.json':'new/borrow-fill/DISPATCH.json','old-fill.json.gz':'new/borrow-fill/FILL.json.gz','old-profile.json':'new/PROFILE.json','plan.json':'new/PLAN.json','providers.json':'new/BORROW-PROVIDERS.json','template.json.gz':'inputs/GLOBAL-TEMPLATE.json.gz','word-base.json.gz':'new/borrow/words/BORROW-WORD-43base.json.gz','word-extra.json.gz':'new/borrow/words/BORROW-WORD-43extra.json.gz'}.items():
 b=(S/path).read_bytes();g=subprocess.check_output(['git','show',HEAD+':'+PKG+path],cwd=a.repo);need(b==g,'exact P53 source '+path);pins[name]={'root':'predecessor','path':path,'head':HEAD,'sha256':sha(b),'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()}
ref=subprocess.check_output(['git','show','c50d12e4720cd1fef2b5a65e337e37de9731879a:research/t248-dirtentry-residue/independent_moment.py'],cwd=a.repo);(R/'reference/PR2848-independent_moment.py').write_bytes(ref);pins['reference-moment.py']={'root':'bundle','path':'reference/PR2848-independent_moment.py','head':'c50d12e4720cd1fef2b5a65e337e37de9731879a','sha256':sha(ref),'git_blob':hashlib.sha1(b'blob '+str(len(ref)).encode()+b'\0'+ref).hexdigest()}
start=text.index('SOURCE_HEAD = ');end=text.index('\n\n\nclass Rejected',start);patch(text[start:end],"SOURCE_HEAD = "+repr(HEAD)+"\nSOURCE_FILES = "+pprint.pformat(pins,sort_dicts=True,width=110))
patch('Source-bound independent audit of the T248 three-bin residue exchange.','Source-bound independent audit of a literal PR2853 replica allocation.')
patch("        path = predecessor / pin['path']","        root = HERE if pin.get('root') == 'bundle' else predecessor\n        path = root / pin['path']")
patch('    N = 248','    need(len(order) > 0 and len(order) % 9 == 0, \'CALL_DOMAIN\')\n    need(all(isinstance(x, list) and len(x) == 2 and all(type(v) is int for v in x) for x in order), \'CALL_INTEGER_SCHEMA\')\n    N = len(order) // 9')
patch('    bin_rows = defaultdict(list)\n','')
patch("        if key in CHANGED_BINS:\n            bin_rows[key].append({'row': row, 'width': width, 'event_position': clock['calls'][time]})\n",'')
start=text.index('    bins = []\n',text.index('def geometry('));end=text.index("    return {'roles':",start);patch(text[start:end],'')
patch("            'profile': dict(sorted(profile.items())), 'bins': bins,","            'profile': dict(sorted(profile.items())),")
start=text.index('def verify(predecessor, candidate):');end=text.index('\n\ndef main():',start);patch(text[start:end],(R/'new_verify.fragment').read_text().rstrip())
insert=text.index('def verify(predecessor, candidate):');patch('def verify(predecessor, candidate):',(R/'word_frames.fragment').read_text().rstrip()+'\n\n\ndef verify(predecessor, candidate):')
compile(text,'independent_events.py','exec');(R/'independent_events.py').write_text(text)
derivation={'status':'EXACT_DERIVATIVE_READY_NOT_CANDIDATE_VERIFIED','source_checker_sha256':OLD_SHA,'source_checker_path':'reference/previous_independent_events.py','target_sha256':sha(text.encode()),'target_path':'independent_events.py','changes':patches,'scope':'Event-clock/family/capacity/coverage and rational arithmetic kernels retained. H23 fixedT/five-row/bin/delta specialization replaced with generic candidate schema and source P53 authentication, literal word frame/width recount, dynamically chosen same-predicate controls, exact root/comparator. No producer/inherited checker import or execution.','upstream_source_head':HEAD}
(R/'DERIVATION.json').write_text(json.dumps(derivation,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':derivation['status'],'target_sha256':derivation['target_sha256'],'exact_replacement_count':len(patches)}))
