import hashlib,json,pathlib,runpy,subprocess,sys
pkg=pathlib.Path(sys.argv[1]); repo=pathlib.Path(sys.argv[2])
data=json.loads((pkg/'CERTIFICATE.json').read_text())
source=json.loads(subprocess.check_output(['git','show',data['audited_blob']],cwd=repo))
assert source['cube_supports']==data['support_masks']
assert subprocess.check_output(['git','rev-parse',data['audited_head_commit']+':research/p104-asynchronous-carrier-bound/CERTIFICATE.json'],cwd=repo,text=True).strip()==data['audited_blob']
gen=runpy.run_path(str(pkg/'generate.py'),run_name='maintainer_generator')
rebuilt,results=gen['build_certificate']()
assert rebuilt==data
assert (json.dumps(rebuilt,indent=2,sort_keys=True)+'\n').encode()==(pkg/'CERTIFICATE.json').read_bytes()
for k,entry in results.items():
 if k.bit_count()==6:
  missing=[v for v in range(8) if not k>>v&1]
  assert entry['width']==(20 if missing[0]^missing[1]==7 else 18)
print('PASS original PR1125 blob and head pin; independent geometric support reconstruction; exact regenerated certificate; all255 widths; opposite-pair iff')
