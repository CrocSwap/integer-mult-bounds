import gzip,json,sys
GK=__import__('os').environ['EO_ROOT']+'/inputs/repo/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
G.V=C.V=112
w=json.loads(gzip.decompress(open(sys.argv[1],'rb').read()))
try: print(dict(sorted(G.profile(w).items())))
except AssertionError as e: print('FAIL',e)
