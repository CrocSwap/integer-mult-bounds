# full regen for the FP word: producer(ham2fp) -> reuse -> retime ; writes raw/reused/final
import os,sys,json
os.environ['E8COORD']='ham'
import runfp as RF, fullword, compile2 as C2, reuse as RU, retime as RT, ham2fp as H
b0=int(sys.argv[2]); ch=int(sys.argv[3]); a6=sys.argv[4]=='1'; tag=sys.argv[5]
RF.run(True,b0,ch,a6,doreuse=False)  # sets H.FP
h=H.build(0,True); W=C2.compile2(h); raw=fullword.build(W); fullword.save(raw,'fp_%s_raw.json.gz'%tag)
re,n=RU.reuse(raw); fullword.save(re,'fp_%s_reused.json.gz'%tag)
fin,moved=RT.retime(re,sweeps=6,M=64); fullword.save(fin,'fp_%s_final.json.gz'%tag)
print(tag,'raw R',raw['R'],'reused',re['R'],'reuse',n['helpers'],n['totals'],'retime moves',moved,'final R',fin['R'])
