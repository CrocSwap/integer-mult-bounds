"""Recheck PR448's complex supplier from a fully verified PR447 parent; retain independent audit and controls."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,sys
root=Path(__file__).resolve().parents[1];full=Path(sys.argv[1]).resolve();up=Path(sys.argv[2]).resolve()
read=lambda p:json.loads(p.read_text());template=lambda p:json.loads(gzip.decompress(p.read_bytes()))
receipt=read(full/'RECEIPT.json');assert receipt['status']=='PASS_FULL_ELEVEN_HOSTING_SELECTED'
parent=full/'parent';assert read(parent/'RECEIPT.json')['status']=='PASS_FULL_HOSTING_SELECTED_KERNEL'
par=parent/'changed';cd=up/'complex';ch=read(cd/'HOSTED.json');pct=template(par/'split-centres/GLOBAL-TEMPLATE.json.gz');ct=template(cd/'GLOBAL-TEMPLATE.json.gz');lc=read(par/'split-centres/LOCAL-CHECKS.json')
sha=hashlib.sha256(gzip.decompress((cd/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest();expected=read(root/'vendor448/EXPECTED.json');assert sha==ch['template_sha256']==expected['complex_template_sha256']
sp=importlib.util.spec_from_file_location('independent448',root/'vendor448/audit_split.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
p,host,split=mod.audit_complex(ct,pct,lc);assert dict(p)=={int(k):v for k,v in ch['global_profile'].items()}
controls=[]
def reject(name,change):
 q=copy.deepcopy(ct);change(q)
 try:mod.audit_complex(q,pct,lc)
 except (AssertionError,KeyError,IndexError,StopIteration,ValueError):controls.append(name)
 else:raise AssertionError('mutation accepted: '+name)
def outside(q):
 pc=q['hosting']['pieces'][0];pc[0]=next(s for s in range(9) if s not in q['hosting']['windows'][str(pc[2])][2])
def badwidth(q):
 pc=next(pc for pc in q['hosting']['pieces'] if len(pc[3])==2);pc[3][0][2]+=1
reject('outside window',outside);reject('split width',badwidth)
reject('understate remainder',lambda q:q['idle_children'][0].__setitem__('rank',q['idle_children'][0]['rank']-1))
reject('understate live',lambda q:q.__setitem__('live',q['live']-1))
reject('duplicate residual',lambda q:q['hosting']['pieces'].append(copy.deepcopy(q['hosting']['pieces'][0])))
a=dict(status='PASS_INDEPENDENT_COMPLEX_CROSS_COPY_AUDIT',complex_template_sha256=sha,complex_profile=dict(p),complex_live=ct['live'],complex_hosted_residuals=host,complex_split_residuals=split,mutations_rejected=controls)
(up/'AUDIT.json').write_text(json.dumps(a,indent=2)+'\n');(up/'RESULT.json').write_text(json.dumps(expected,indent=2)+'\n')
if not (up/'parent').exists():(up/'parent').symlink_to(parent,target_is_directory=True)
(up/'RECEIPT.json').write_text(json.dumps(dict(status='PASS_VERIFIED_COMPLEX_COMPONENT_REUSE',parent_receipt_sha256=hashlib.sha256((full/'RECEIPT.json').read_bytes()).hexdigest(),complex_template_sha256=sha,scope='Parent PR447 full supplier evidence plus regenerated PR448 complex template and independent owner/window audit. Not a complete PR448 wrapper replay.'),indent=2)+'\n')
print(a['status'],host,split,len(controls))
