"""Declared relative filesystem adapters; all finite checks preserved."""
from pathlib import Path
import json,hashlib,sys
W=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();A=W/'experiments/architecture/bit-provider-portfolio-v4';I=W/'experiments/architecture/signed-provider-independent-v4';rows=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def patch(p,old,new):
 s=p.read_text();assert old in s,(p,old);before=sha(p);p.write_text(s.replace(old,new));rows.append({'path':str(p.relative_to(W)),'original_sha256':before,'adapted_sha256':sha(p),'old':old,'new':new,'purpose':'filesystem paths only; target producer preserved'})
patch(A/'emit_portfolio.py',"'directory':str(source)","'directory':str(source.relative_to(ROOT))")
patch(A/'emit_portfolio.py',",'target_address.py'","")
patch(A/'global/invoice.py',"src={pid:Path(z['directory'])for pid,z in reg.items()}","src={pid:ROOT/z['directory']for pid,z in reg.items()}")
patch(I/'portfolio_global.py',"s=Path(z['directory']);", "s=A.parents[3]/z['directory'];")
patch(I/'portfolio_prefix.py',"Path(z['directory'])", "S.parents[3]/z['directory']")
patch(I/'portfolio_old_complex_arithmetic.py',"src=Path(reg[ccall['provider']]['directory']);", "src=R/reg[ccall['provider']]['directory'];")
OUT.write_text(json.dumps({'status':'RELATIVE_PATH_REPLAY_SOURCE_ADAPTERS','adapters':rows},indent=2)+'\n')
