import hashlib, os, sys
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); bad=0; n=0
for line in open(os.path.join(root,'MANIFEST.sha256')):
    h,p=line.rstrip('\n').split('  ',1); n+=1
    f=os.path.join(root,p)
    if not os.path.exists(f) or hashlib.sha256(open(f,'rb').read()).hexdigest()!=h: print('FAIL manifest',p); bad+=1
print('FAIL' if bad else 'PASS','manifest: %d files'%n); sys.exit(1 if bad else 0)
