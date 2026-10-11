"""Apply frozen pair-search endpoint frame changes after the 57-gate A retime.
The witness changes 112 B frames; every ordered scalar ADD is identical.
Prepared by eumemic with OpenAI Codex assistance; Apache-2.0.
"""
import copy,json,hashlib

def content(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def apply(src,selection):
 assert content(src)==selection['input_sha256']=='bae58f0692326f180ba49642360fd55557f59a93a96a8fa62bf7babd55d2384e'
 out=copy.deepcopy(src);frames={tuple(sorted(f)):i for i,f in enumerate(src['frames'])};seen=set()
 for ph,i,old,new in selection['gates']:
  assert ph=='B' and (ph,i) not in seen;seen.add((ph,i))
  gate=out[ph][i];assert tuple(sorted(out['frames'][gate[0]]))==tuple(sorted(old))
  assert tuple(sorted(new)) in frames;gate[0]=frames[tuple(sorted(new))]
 assert len(seen)==112
 for ph in ('D','A','B','C'):
  assert len(out[ph])==len(src[ph]) and all(g[1:]==h[1:] for g,h in zip(out[ph],src[ph]))
 assert content(out)==selection['output_sha256']=='fc4d045fd68ba47e21d69b840a51128ff52739dca3c0f7b9255bd757e31737e7'
 return out

