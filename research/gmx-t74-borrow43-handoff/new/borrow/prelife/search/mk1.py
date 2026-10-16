import json,sys,copy,gzip
import prelife2 as P, repair2
w=P.load(sys.argv[1]);P.TRACE,_=repair2.run(copy.deepcopy(w),None)
ok={(h,L):E for h,L,E,*_ in json.load(open(sys.argv[2]))}
for spec in sys.argv[4:]:
    h,L=map(int,spec.split(':'));w=P.build(w,L,h,ok[(h,L)]);P.TRACE,_=repair2.run(copy.deepcopy(w),None)
print(w['report'])
open(sys.argv[3],'wb').write(gzip.compress(json.dumps(w,separators=(',',':')).encode()))
