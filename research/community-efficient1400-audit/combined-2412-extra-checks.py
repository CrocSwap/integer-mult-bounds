import ast,hashlib,importlib.util,json,pathlib,subprocess,unittest
P=pathlib.Path('/tmp/pr-efficient1400');R=P/'sources/2412';D=json.load(open(P/'packets/2412.json'))
prod=R/'research/complex-k492-owner-repair/code/hpe_audit_and_transport.py';fast=R/'research/hpe-audit-fast-seed93/hpe_audit_fast.py'
def nodoc(p):
 t=ast.parse(p.read_text());t.body=t.body[1:];return ast.dump(t,include_attributes=False)
assert nodoc(prod)==nodoc(fast),'Production differs from reviewed opt-in executable AST'
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('existing_regressions',R/'research/hpe-audit-fast-seed93/test_package.py');m.F=load('production',prod)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c)for c in (m.RowArithmetic,m.Copies));result=unittest.TextTestRunner(verbosity=2).run(suite);assert result.wasSuccessful()
oldpath='research/complex-k492-owner-repair/code/hpe_audit_and_transport.py';newpath='research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
assert hashlib.sha256((R/newpath).read_bytes()).hexdigest()=='c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3'
# Every modified old manifest is solely a path relocation plus the two corrected vendor-file digests.
replacements={oldpath:newpath}
for rel in ['research/coded-helper-early-end8/vendor/pr855/SOURCE-PINS.json','research/coded-helper-early-end8/vendor/pr855/verify.py']:
 old=subprocess.check_output(['git','show',D['merge_base']+':'+rel],cwd=R);replacements[hashlib.sha256(old).hexdigest()]=hashlib.sha256((R/rel).read_bytes()).hexdigest()
count=0
for f in D['files']:
 rel=f['path']
 if not rel.endswith(('SOURCES.json','SOURCE-PINS.json')) or '/hpe-transport-integer-production/' in rel:continue
 text=subprocess.check_output(['git','show',D['merge_base']+':'+rel],cwd=R,text=True)
 for old,new in replacements.items():text=text.replace(old,new)
 assert json.loads(text)==json.loads((R/rel).read_text()),rel
 count+=1
print('PASS_2412_PRODUCTION_DEPENDENCIES executable_ast_equal=True row_copy_tests=5 manifests=',count)
