from pathlib import Path
import subprocess
P=Path('/tmp/pr-efficient1800');E=P/'split-frame-consumer';R=Path('/tmp/integer-mult-efficient1100-20261015')
for rel in ['research/r420-two-sided-basis/SOURCES.json','certificates/selected-result.json','research/community-reconciliation92-audit/MANIFEST.json','Makefile']:
 f=E/rel
 if not f.exists():f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show','HEAD:'+rel],cwd=R))
f=E/'tests/test_historical_check.py';s=f.read_text();needle="'scripts/shared_point_circuit.py'})";assert needle in s;s=s.replace(needle,"'scripts/shared_point_circuit.py', 'scripts/audit_joint_frames.py'})")
needle='    def test_real_snapshots_match_unchanged_predecessor_pins(self):';assert needle in s
extra='''    def test_split_joint_successor_authenticates_all_three_inputs(self):
        config = next(c for c in checker.CONFIG['split-skip']['additional_inputs']
                      if c['path'] == 'scripts/audit_joint_frames.py')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for key in ('manifest', 'path', 'input'):
                path = root / config[key]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / config[key]).read_bytes())
            expected = (root / config['input']).read_bytes()
            self.assertEqual(checker.authenticated_input(root, config), expected)
            for key, message in [('path', 'Unrecognized live source update'),
                                 ('input', 'Changed historical input')]:
                path = root / config[key]
                before = path.read_bytes()
                path.write_bytes(before + b'\\n# unreviewed mutation\\n')
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, message):
                    checker.authenticated_input(root, config)
                path.write_bytes(before)
            path = root / config['manifest']
            pins = json.loads(path.read_bytes())
            pins[config['field']][config['path']] = '0' * 64
            path.write_text(json.dumps(pins))
            with self.assertRaisesRegex(ValueError, 'Missing or changed predecessor source pin'):
                checker.authenticated_input(root, config)

'''
s=s.replace(needle,extra+needle);f.write_text(s);subprocess.run(['git','add','.'],cwd=E,check=True)
s=(P/'run_shared_frame_consumers_v2.py').read_text().replace("D=P/'shared-frame-consumers'","D=P/'split-frame-consumer'")
a=s.index('q=[]');b=s.index('\nwith (P/',a)
s=s[:a]+'''q=[]
for flags in [[],['-O']]:
 q.append((D,[py,'-I',*flags,'-B','-m','unittest','discover','-s','tests','-p','test_historical_check.py','-v'],120,'Complete historical adapter unit suite, four exact dependency bindings and explicit successor/baseline/manifest rejection controls'))
q.append((D,[py,'-B','scripts/replay_historical_check.py','split-skip'],600,'Actual historical wrapper: unchanged witness, independent arithmetic and full split-skip tests in authenticated temporary snapshot'))
'''+s[b:]
s=s.replace('check-shared-frame-consumers-v2','check-split-frame-consumer').replace('number=1861','number=1922').replace("P/'1861.json'","P/'1922.json'").replace('Candidate live-consumer migration for disjoint union, cube replay, current ternary and PR1076 historical wrapper. Other legacy consumers remain separate obligations.','Candidate split-skip historical adapter extension. No production helper admission; remaining historical consumers need their own review.')
(P/'run_split_consumer.py').write_text(s)
print('Prepared exact four-input split-skip adapter and rejection controls; not run yet')
