"""Strict exit-code wrapper for PR354's data-returning scalar replay.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import sys
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('Assertions required')
from pathlib import Path
import json,hashlib,importlib.util
code,word,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(code));s=importlib.util.spec_from_file_location('public354_f2',code/'f2.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r,residual=m.replay(str(word));assert r==dict(violations=0,first_bad=[],final_mismatch=0,copies=20,X_not_restored=0,H_not_restored=0,resid_sigma0=0,resid_other=0)and not residual
out.write_text(json.dumps(dict(status='PASS_STRICT_PR354_SCALAR_REPLAY',result=r,word_sha256=hashlib.sha256((word/'249-records.bin').read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n')
