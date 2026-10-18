"""Build the verifier-gap toy: the #799 X4 FULL-WORD plus a centre-free net-zero cut pair  add 112<-5 (+1) first, add 112<-5 (-1) last."""
import gzip, json, sys
w = json.load(gzip.open(sys.argv[1]))
w['cut'] = [['add', 112, 5, 1, 1, None]] + w['cut'] + [['add', 112, 5, -1, 1, None]]
with gzip.GzipFile(sys.argv[2], 'wb', mtime=0) as f: f.write(json.dumps(w).encode())
print('toy cut length', len(w['cut']))
