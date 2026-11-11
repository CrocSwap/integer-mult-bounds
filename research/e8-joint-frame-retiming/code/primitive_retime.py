"""Apply the pinned joint A/B primitive retiming to the V2 kernel word.
Selection and output hashes are exact; scalar gate operands remain unchanged.
OpenAI Codex integration, using the finite candidate found by search_r740_quad.
"""
import copy,hashlib,json
from pathlib import Path

def content(w): return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def apply(src,sel):
 w=copy.deepcopy(src); frame_map={tuple(sorted(x)):i for i,x in enumerate(w['frames'])}
 assert sel['input_sha256']==content(w)
 for ph in ('D','A','B','C'):w[ph]=[[f,d,[x]] for f,d,ss in w[ph] for x in ss]
 assert content(w)==sel['primitive_input_sha256']
 prepared=copy.deepcopy(w)
 changed=0
 seen=set()
 for ph,i,old_lines,new_lines in sel['gates']:
  assert ph in ('A','B') and (ph,i) not in seen; seen.add((ph,i))
  gate=w[ph][i]; old=tuple(sorted(w['frames'][gate[0]])); assert old==tuple(sorted(old_lines)),(ph,i,old,old_lines)
  nf=tuple(sorted(new_lines)); assert nf in frame_map
  gate[0]=frame_map[nf]; changed+=1
 assert changed==len(sel['gates']) and all(g[1:]==prepared[ph][i][1:] for ph in ('D','A','B','C') for i,g in enumerate(w[ph]))
 assert content(w)==sel['output_sha256']
 return w
if __name__=='__main__':
 import sys
 src=json.load(open(sys.argv[1])); sel=json.load(open(sys.argv[2])); out=apply(src,sel);json.dump(out,open(sys.argv[3],'w'),sort_keys=True,separators=(',',':')); print('PASS primitive retime',sel['gates'].__len__(),'moves',sel['output_sha256'])
