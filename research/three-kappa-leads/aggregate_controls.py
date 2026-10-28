"""Challenge exact source windows, whole-helper inventories and invoice."""
import copy,json
from chronology_check import check,common,P
c=common.read(P/'CHRONOLOGY-CANDIDATE.json');check(c);controls=[]
def reject(name,mutate,reason):
 d=copy.deepcopy(c);mutate(d)
 try:check(d)
 except ValueError as e:
  if reason not in str(e):raise
  controls.append(name)
 else:raise ValueError('accepted '+name)
reject('wrong interface order',lambda d:d['order'].reverse(),'one actual adjacent join swap')
reject('source lower endpoint read',lambda d:d['z'][0].__setitem__(1,d['groups'][d['z'][0][0]][1]),'actual source window')
reject('one omitted helper flow',lambda d:d['z'][0].__setitem__(3,d['z'][0][3]-1),'exact width balance')
reject('over-capacity whole-helper pattern',lambda d:d['x'][0][1].__setitem__(0,100),'whole-helper pattern capacity')
reject('unpaid output histogram unit',lambda d:d['profile'].__setitem__('1',d['profile']['1']-1),'reconstructed complete paid profile')
print(json.dumps({'status':'PASS_AGGREGATE_CONTROLS','controls':controls}))
