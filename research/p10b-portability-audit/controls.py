"""Independent gzip-content binding adversarial audit; OpenAI Codex assisted. Apache-2.0."""
from pathlib import Path
import argparse,ast,copy,gzip,hashlib,importlib.util,io,json,sys,tempfile
ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--regeneration',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
assert not args.output.exists();D=args.output.resolve().parent;D.mkdir(parents=True,exist_ok=True)
P=args.package.resolve()
finish=P/'code/finish.py';initial=finish.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('reviewed_finish',finish);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
f=mod.verify_regenerated_files
names=['graph_p10.json','kchron_p10.json','profile_p10.json','word_p10.json.gz','frames_p10.json.gz']
helper=next(n for n in ast.parse(initial).body if isinstance(n,ast.FunctionDef) and n.name=='verify_regenerated_files')
helper_hash=sha(ast.dump(helper,include_attributes=False).encode())
results=[]
with tempfile.TemporaryDirectory(prefix='cases-',dir=D) as tmp:
 root=Path(tmp);src=root/'source';work=root/'regeneration';pd=src/'bitword/selected/bit';rd=work/'final1';pd.mkdir(parents=True);rd.mkdir(parents=True)
 files={};payloads={}
 for i,name in enumerate(names):
  payload=json.dumps({'name':name,'index':i,'value':[1,2,3]},separators=(',',':')).encode()+b'\n';payloads[name]=payload
  a=gzip.compress(payload,compresslevel=9,mtime=0) if name.endswith('.gz') else payload
  if name.endswith('.gz'):
   bbuf=io.BytesIO()
   with gzip.GzipFile(filename='different-platform-name',mode='wb',fileobj=bbuf,mtime=123456,compresslevel=1) as z:z.write(payload)
   b=bbuf.getvalue();assert a!=b and gzip.decompress(a)==gzip.decompress(b)==payload
  else:b=a
  (pd/name).write_bytes(a);(rd/name).write_bytes(b);files[name]={'pinned':sha(a),'rebuilt':sha(b),'expanded':sha(payload)}
 f(src,work,files);results.append({'case':'baseline_distinct_payloads_changed_gzip_header_and_compression','status':'ACCEPT'})
 def reject(label,report,expected_type=AssertionError,expected_message=None):
  try:f(src,work,report)
  except expected_type as e:
   if expected_message is not None:assert expected_message in str(e),(label,type(e),str(e))
   results.append({'case':label,'status':'REJECT','exception':type(e).__name__,'message':str(e)})
  else:raise AssertionError('Accepted invalid control '+label)
 bad=copy.deepcopy(files);bad['wrong_p10.json']=bad.pop(names[0]);assert len(bad)==5
 reject('wrong_key_same_cardinality',bad,expected_message='Exactly five')
 for side,directory in [('pinned',pd),('rebuilt',rd)]:
  for name in names:
   p=directory/name;raw=p.read_bytes();p.unlink();reject('actual_missing_'+side+'_'+name,files,FileNotFoundError);p.write_bytes(raw)
 for name in names:
  p=rd/name;raw=p.read_bytes();semantic=json.loads(payloads[name]);wrong=json.dumps(semantic,indent=2,sort_keys=True).encode()+b'\n'
  assert wrong!=payloads[name] and json.loads(wrong)==semantic
  replacement=gzip.compress(wrong,mtime=0) if name.endswith('.gz') else wrong
  p.write_bytes(replacement);bad=copy.deepcopy(files);bad[name]['rebuilt']=sha(replacement);bad[name]['expanded']=sha(wrong)
  reject('json_equivalent_format_change_'+name,bad,expected_message='complete expanded bytes');p.write_bytes(raw)
 for name in names[-2:]:
  p=rd/name;raw=p.read_bytes();new=gzip.compress(payloads[name],mtime=987654);assert new!=raw;p.write_bytes(new)
  reject('stale_container_hash_after_equal_content_recompression_'+name,files,expected_message='rebuilt container hash')
  good=copy.deepcopy(files);good[name]['rebuilt']=sha(new);f(src,work,good);results.append({'case':'fresh_container_hash_after_equal_content_recompression_'+name,'status':'ACCEPT'});p.write_bytes(raw)
 for name in names[-2:]:
  p=rd/name;raw=p.read_bytes();badbytes=bytearray(raw);badbytes[-8]^=1;p.write_bytes(badbytes);bad=copy.deepcopy(files);bad[name]['rebuilt']=sha(badbytes)
  reject('invalid_gzip_crc_'+name,bad,gzip.BadGzipFile);p.write_bytes(raw)
 f(src,work,files)
# Exercise the production helper against an existing actual 5-file regenerated word, read-only.
actual=args.regeneration.resolve();record=json.loads((actual/'REGENERATION.json').read_text());f(P/'vendor/predecessor',actual,record['files']);results.append({'case':'actual_five_file_producer_receipt','status':'ACCEPT'})
assert finish.read_bytes()==initial,'Reviewed finish.py changed during audit'
manifest=P/'MANIFEST.json';assert sha(manifest.read_bytes())=='79d3b69411b748568205fb4176d43b457d7ef6863ab5e6af1cbc7abe8bded3f1'
report={'status':'PASS_INDEPENDENT_PRODUCER_BINDING_ADVERSARIAL_REVIEW','package':str(P),'manifest_sha256':sha(manifest.read_bytes()),'finish_sha256':sha(initial),'helper_ast_sha256':helper_hash,'controls_script_sha256':sha(Path(__file__).read_bytes()),'cases':results,'accepted':sum(r['status']=='ACCEPT' for r in results),'rejected':sum(r['status']=='REJECT' for r in results),'scope':'Imported the exact frozen production helper. Writes limited to ephemeral audit fixtures. Valid gzip container representation changes accepted; complete expanded bytes remain exact.'}
out=args.output.resolve();out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('PASS',report['accepted'],'accepted',report['rejected'],'rejected',sha(out.read_bytes()))
