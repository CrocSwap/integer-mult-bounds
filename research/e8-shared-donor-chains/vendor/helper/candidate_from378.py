"""Two fixed helper substitutions on pinned PR378's far-retimed E8 word.
The PR378 far relocations are upstream work by Chafik Boukhalfa/chafreaky,
building on PR365/374. This composes exact helper equalities; it does not
transfer gate indices or claim those relocations as new work.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
import gzip,json,sys
from hashlib import sha256
from pathlib import Path
import two_alias
assert __debug__
SOURCE='f2664ee7bcdfb55893abe9f1be8ee6a394a602e8262e611de2a0328bbd508aa7'
FINAL='d14ea8bf581d9f5ea8f3261e614199386d71ea4cbc8bc48d6bec371954669daf'
def build(raw):
 assert sha256(raw).hexdigest()==SOURCE
 c=json.loads(gzip.decompress(raw));assert(c['h'],c['v'],c['R'],c['cst'])==(9,120,783,72)
 for drop,use,want in [(706,268,'c06e9570c9079737473e289d35d7cb9b7ed01d0d6f068637548e2d39f9a68767'),(707,323,FINAL)]:
  c,r=two_alias.build(c,drop,use);body=json.dumps(c,sort_keys=True,separators=(',',':')).encode();assert sha256(body).hexdigest()==want
 return body
if __name__=='__main__':
 src,out=map(Path,sys.argv[1:]);out.write_bytes(build(src.read_bytes()));print('PASS_SOURCE_BOUND_PR378_HELPER_COMPOSITION',FINAL)
