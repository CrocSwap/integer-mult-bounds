# LEANTHIN lt2: dump float duals (from lt1 colgen LP) as dyadic integers y_int/2^S (clamped >= 0) to certs/cert_k{k}.json.
import sys,json,os
import lt1
S=110
os.makedirs('certs',exist_ok=True)
for k in map(int,sys.argv[1:]):
    v,sup,y,rows=lt1.solve(k)
    yi=[max(0,int(round(float(t)*2**40)))*2**(S-40) for t in y]   # exact dyadics from a 40-bit rounding of the float dual
    json.dump({'k':k,'S':S,'y':[str(t) for t in yi],'float_chat':v},open(f'certs/cert_k{k}.json','w'))
    print('dumped',k,v,flush=True)
