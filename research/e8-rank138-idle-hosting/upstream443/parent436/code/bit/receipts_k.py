"""Assemble the finite-bill input for the E8 bit word from this run's receipts (no pinned numbers are trusted:
every value is read from a receipt written earlier in verify.sh, and cross-checked).
Bridged word B_K (DaysSky, assisted with Claude): K and the literal replica count T are read from kappa.json; S = 2K+1.
usage: receipts_k.py WORD.json.gz RECORDDIR legality.json columns.json kappa.json OUT.json"""
import sys, json, gzip, struct
from collections import Counter
w=json.load(gzip.open(sys.argv[1],'rt')); rd=sys.argv[2]; leg=json.load(open(sys.argv[3])); col=json.load(open(sys.argv[4])); kap=json.load(open(sys.argv[5]))
v,R,h=w['v'],w['R'],w['h']; KP=kap.get('K',2); S=2*KP+1; m=S*h; T=kap['T']; assert kap['m']==m and kap['h']==h and (T*R)%S==0
rec=open(rd+'/249-records.bin','rb').read(); n=len(rec)//24
adds=sum(1 for i in range(n) if struct.unpack_from('<6i',rec,24*i)[0]==1)
assert adds==leg['common_frame_ADDs']==col['local_scalar_additions'] and col['local_odd_scalar_additions']==adds   # every coefficient is 1
ncopy=len(w['ret']); assert ncopy==leg['copies']==leg['erasures']==col['fresh_center_copies']//S==9
fwd=int(col['signed_lift_prefix'][0]['cancellation_free_signed_row_l1_upper']); inv=int(col['signed_lift_prefix'][1]['cancellation_free_signed_row_l1_upper'])
assert col['signed_lift_prefix'][0]['reverse'] is False and col['signed_lift_prefix'][1]['reverse'] is True
stock=kap['W']; maxops=0     # W and the histogram of kappa.json already carry the T literal replicas; identity chart only
factors=maxops+(m-1)+m; K=2*S*T*((stock-1)+R*m*factors)
deficit=2*KP*v-S*ncopy*h
out=dict(Kpairs=KP,h=h,m=m,v=v,R=R,T=T,stock=stock,literal=dict(kap['normalized_histogram']),ncopy=ncopy,deficit=deficit,
         weighted=adds,unit=adds,fwd_row=fwd,inv_row=inv,K=K,coarse=kap['bit_coarse'],qstar=w['lines'][0],word=sys.argv[1],
         provenance=dict(adds='ADD records of the exported word = legality common_frame_ADDs = columns local_scalar_additions',
                         rows='columns_h signed_lift_prefix', K='2*S*T*((stock-1)+R*m*(maxops+(m-1)+m)), S = 2K+1, identity chart maxops 0',
                         ncopy='retained totals of the word = COPY = ERASE count'))
json.dump(out,open(sys.argv[6],'w'),indent=1)
print('finite-bill input: K %d, m %d, v %d, R %d, T %d, stock %d, NCOPY %d, unit additions %d, rows %d/%d, K %d'%(KP,m,v,R,T,stock,ncopy,adds,fwd,inv,K))
