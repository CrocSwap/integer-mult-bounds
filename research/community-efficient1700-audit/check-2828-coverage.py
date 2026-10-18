from pathlib import Path
import hashlib,json
p=Path('research/ut4-fifteen-call-five-b/census.py')
s=p.read_text()
assert hashlib.sha256(p.read_bytes()).hexdigest() == 'a20eeb35aee5dff8788e798d68a237c9c1adf6fdcb35626c34be2b3af058d972'
s=s.replace("if key == '5,5,5':", "if key == '5,5,5':\n                        for profile in (pa,pc):\n                            ranks=[srank[x] for x in profile_gaps(profile)]\n                            assert sum(ranks)>=4\n                            assert 5-sum(ranks)+max(ranks)<=3")
s=s.replace("st3['dirty_profile_pairs'] += 1", "st3['dirty_profile_pairs'] += 1\n                                    if not any(da_prof) or not any(dc_prof):\n                                        audit['zero_prefix_pairs']+=1\n                                        audit.setdefault('example', [list(middle),list(pa),list(pc),list(da_prof),list(dc_prof)])")
s=s.replace("for kc_tup in kc_tups:\n                                            g_lists", "for kc_tup in kc_tups:\n                                            assert max(a+c for a,c in zip(ka_tup,kc_tup))<=4\n                                            g_lists")
ns={'__file__':str(p.resolve()),'audit':{'zero_prefix_pairs':0}}
exec(compile(s,str(p),'exec'),ns)
P,_=ns['load']();result=ns['run'](P)
original=json.loads(p.with_name('RESULT.json').read_text())
assert result['domains']==original['domains']
assert result['three_role_555']==original['three_role_555']
print('PASS full original results retained; every admitted active profile has rankmass>=4; per-labelgap<=3; jointgap<=4')
print(json.dumps(ns['audit']))
