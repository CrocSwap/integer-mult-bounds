from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
import contextlib,io,hashlib,json
with contextlib.redirect_stdout(io.StringIO()):exec(open(HERE/'groups.py').read())
classes=[]
for key,cs in groups.items():
 classes.append(dict(normalized_held_row=[[r,str(q)]for r,q in key],members=[dict(role=c['role'],first=c['first'],second=c['second'],normalization=str(c['norm']),E=c['E'],F=c['F'],G=c['G'],exports=c['exports'],paid_ranks_before=c['paid_ranks_before'])for c in cs]))
record=dict(source_sha256=hashlib.sha256((base/'inputs/PR6702-WORD.json.gz').read_bytes()).hexdigest(),intervals=len(intervals),projective_classes=len(groups),class_size_counts=dict(Counter(len(cs)for cs in groups.values())),pair_counts=st,classes=classes,pairs=[dict(role=a['role'],first=a['first'],middle_left=a['second'],middle_right=b['first'],last=b['second'],shared_move=a['second']==b['first'],all_intervening_helper_writes=[e[0]for i,e in writes[a['role']]if a['first']<i<b['second']],paid_ranks_before=a['paid_ranks_before']+([b['paid_ranks_before'][1]]if a['second']==b['first']else b['paid_ranks_before']),paid_ranks_after=[sum(a['paid_ranks_before'])+b['paid_ranks_before'][1]]if a['second']==b['first']else[sum(a['paid_ranks_before']),sum(b['paid_ranks_before'])])for a,b in pairs])
Path(sys.argv[1]).write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print('CENSUS',len(record['pairs']),'pairs',Path(sys.argv[1]).stat().st_size,'bytes')
