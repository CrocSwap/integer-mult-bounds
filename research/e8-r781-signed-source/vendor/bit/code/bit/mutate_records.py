"""Negative controls for the official checkers on the exported E8 records: every mutant must be rejected.
usage: mutate_records.py RECORDDIR COHORT_IN COHORT_OUT LEGALITY_BIN COLUMNS_BIN LEGALITY_NCOPY8_BIN"""
import sys, struct, shutil, subprocess, os
rd,cin,cout,leg,col,leg8=sys.argv[1:7]
rec=bytearray(open(rd+'/249-records.bin','rb').read()); n=len(rec)//24
get=lambda i: list(struct.unpack_from('<6i',rec,24*i))
def run(mut,which):
    tmp=cout+'-mut'; shutil.rmtree(tmp,ignore_errors=True); shutil.copytree(cout,tmp)
    open(tmp+'/COHORT249-RECORDS.bin','wb').write(bytes(mut))
    if which=='legality': r=subprocess.run([leg,cin,tmp,tmp+'/x.json'],capture_output=True,text=True)
    elif which=='legality8': r=subprocess.run([leg8,cin,tmp,tmp+'/x.json'],capture_output=True,text=True)
    else: r=subprocess.run([col,tmp+'/COHORT249-RECORDS.bin',tmp+'/x.json'],capture_output=True,text=True)
    shutil.rmtree(tmp,ignore_errors=True)
    return r.returncode!=0, (r.stderr.strip().splitlines() or ['?'])[-1][:70]
def mutate(pred,change):
    m=bytearray(rec)
    for i in range(n):
        e=get(i)
        if pred(e,i):
            change(e); struct.pack_into('<6i',m,24*i,*e); return m
    raise SystemExit('no mutation site')
B4=[i for i in range(n) if get(i)[0]==1 and get(i)[5]==4]
cases=[('drop a phase-B delivery ADD (columns: defining decoder)','columns',bytes(rec[:24*B4[len(B4)//2]]+rec[24*(B4[len(B4)//2]+1):])),
       ('ADD at a frame its registers do not stand at','legality',mutate(lambda e,i:e[0]==1 and e[5]==4,lambda e:e.__setitem__(4,0))),
       ('MOVE with a wrong rank','legality',mutate(lambda e,i:e[0]==0 and e[4]>1,lambda e:e.__setitem__(4,e[4]-1))),
       ('COPY with a cheaper rank','legality',mutate(lambda e,i:e[0]==2,lambda e:e.__setitem__(5,7))),
       ('drop a dirt-compensation ADD (columns)','columns',bytes(rec[:24*[i for i in range(n) if get(i)[0]==1 and get(i)[5]==1][0]]+rec[24*([i for i in range(n) if get(i)[0]==1 and get(i)[5]==1][0]+1):])),
       ('unchanged word with the copy count pinned to h = 8 (NCOPY unset)','legality8',bytes(rec))]
ok=True
for name,which,m in cases:
    rej,msg=run(m,which); ok&=rej
    print(('   REJECTED  ' if rej else '   ACCEPTED!! ')+name+'  ['+msg+']')
assert ok, 'a mutant was accepted'
print('PASS all %d record-level negative controls rejected'%len(cases))
