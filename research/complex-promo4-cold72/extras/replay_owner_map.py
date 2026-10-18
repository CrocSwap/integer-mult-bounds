"""Rebuild the literal owner map from an integer pattern-flow witness; standard library only."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,copy,gzip,hashlib,json
P=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def need(value,message):
 if not value:raise ValueError(message)
def construct(plan,certificate):
 need(certificate['schema']=='integer-pattern-flow/1','certificate schema')
 keys=[g['key']for g in certificate['windows']]
 need(len(keys)==len(set(keys)) and set(keys)==set(plan['windows']),'complete unique windows')
 pools=defaultdict(list);rows=[];idle=Counter();families=defaultdict(set)
 calls={c['time']:c for c in plan['provider_calls']}
 need(set(calls)==set(range(72)),'complete calls')
 for t,c in calls.items():
  for h,w in enumerate(plan['provider_registry'][c['provider']]['widths']):pools[t,w].append(h)
 for group in certificate['windows']:
  key=group['key'];rep,child=map(int,key.split(','));cap,times=plan['windows'][key];port=0
  for pattern in group['patterns']:
   widths=pattern['widths'];N=pattern['count'];slots=pattern['slots'];flows=pattern['flows']
   need(type(N)is int and 0<N<=112 and len(slots)==N,'pattern count')
   need(all(type(w)is int and w in(4,5,7,8,9)for w in widths) and widths==sorted(widths),'pattern widths')
   need(sum(widths)<=cap,'pattern capacity')
   declared={}
   for t,w,n in flows:
    need(type(t)is type(w)is type(n)is int and t in times and w in widths and n>0 and(t,w)not in declared,'flow shape')
    declared[t,w]=n
   actual=Counter()
   for slot in slots:
    need(port<112,'port count')
    need(all(type(t)is type(w)is int and t in times for t,w in slot),'slot window')
    need(len({t for t,w in slot})==len(slot),'unique time in a physical bin')
    need(Counter(w for t,w in slot)==Counter(widths),'slot width multiset')
    need(slot==sorted(slot),'canonical slot order')
    off=0;family=rep*896+(2*plan['pairs'][str(child)]+plan['sides'][str(child)])*112+port
    for t,w in slot:
     need(bool(pools[t,w]),'complete helper inventory')
     h=pools[t,w].pop();call=calls[t]
     need((call['stage'],call['replica'])==tuple(plan['order'][t]),'call chronology')
     need(family not in families[t],'unique physical family per call');families[t].add(family)
     rows.append(dict(child=child,copy=rep*112+port,family=family,helper=h,offset=off,owner_replica=rep,port=port,replica=call['replica'],stage=call['stage'],time=t,width=w));off+=w;actual[t,w]+=1
    need(off<=cap,'literal capacity')
    if off<cap:idle[cap-off]+=1
    port+=1
   need(actual==Counter(declared),'integer flow ledger')
   need(all(sum(n for(t,ww),n in declared.items()if ww==w)==N*count for w,count in Counter(widths).items()),'pattern width supply')
   need(all(sum(n for(tt,w),n in declared.items()if tt==t)<=N for t in times),'pattern time capacity')
  need(port==112,'complete window ports')
 need(len(rows)==36288 and not any(pools.values()),'all helper roles')
 paid=idle.copy()
 for c in calls.values():paid.update({int(k):v for k,v in plan['provider_registry'][c['provider']]['actual_paid_profile'].items()})
 need(dict(paid)=={int(k):v for k,v in plan['profile'].items()},'literal global profile')
 need(sum(k*n for k,n in paid.items())==520704,'rank mass')
 rows.sort(key=lambda z:(z['time'],z['helper']));raw=json.dumps(rows,sort_keys=True,separators=(',',':')).encode();packed=gzip.compress(raw,mtime=0);packed=packed[:9]+b'\xff'+packed[10:]
 need(hashlib.sha256(packed).hexdigest()==plan['assignment_sha256'],'literal assignment hash')
 return packed,dict(idle)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--controls',type=Path);args=ap.parse_args();plan=read(P/'data/PLAN.json');cert=read(P/'data/OWNER-CONSTRUCTION.json.gz');data,idle=construct(plan,cert)
 need(data==(P/'data/OWNERS.json.gz').read_bytes(),'exact committed owner bytes')
 if args.out:args.out.write_bytes(data)
 rejected=[]
 if args.controls:
  occupied=next((i,j)for i,g in enumerate(cert['windows'])for j,p in enumerate(g['patterns'])if p['widths'])
  i,j=occupied
  def reject(name,mutate,reason):
   bad=copy.deepcopy(cert);mutate(bad)
   try:construct(plan,bad)
   except ValueError as ex:
    need(str(ex)==reason,'wrong rejection reason: '+name+': '+str(ex));rejected.append(dict(name=name,reason=str(ex)));return
   raise ValueError('accepted mutation: '+name)
  reject('window removed',lambda z:z['windows'].pop(),'complete unique windows')
  reject('wrong pattern count',lambda z:z['windows'][i]['patterns'][j].__setitem__('count',113),'pattern count')
  reject('invalid pattern width',lambda z:z['windows'][i]['patterns'][j]['widths'].__setitem__(0,6),'pattern widths')
  reject('slot outside window',lambda z:z['windows'][i]['patterns'][j]['slots'][0][0].__setitem__(0,-1),'slot window')
  reject('wrong slot width',lambda z:z['windows'][i]['patterns'][j]['slots'][0][0].__setitem__(1,99),'slot width multiset')
  reject('wrong flow count',lambda z:z['windows'][i]['patterns'][j]['flows'][0].__setitem__(2,z['windows'][i]['patterns'][j]['flows'][0][2]+1),'integer flow ledger')
  ii,jj=next((ii,jj)for ii,g in enumerate(cert['windows'])for jj,p in enumerate(g['patterns'])if len(p['widths'])>=2)
  reject('duplicate time',lambda z:z['windows'][ii]['patterns'][jj]['slots'][0][1].__setitem__(0,z['windows'][ii]['patterns'][jj]['slots'][0][0][0]),'unique time in a physical bin')
  args.controls.write_text(json.dumps(dict(status='PASS_OWNER_RECONSTRUCTION_AND_MUTATIONS',positive=1,rejected=rejected,owners_sha256=hashlib.sha256(data).hexdigest(),idle=idle),indent=2)+'\n')
 print('PASS exact owner reconstruction',hashlib.sha256(data).hexdigest(),'idle',idle,flush=True)
if __name__=='__main__':main()
