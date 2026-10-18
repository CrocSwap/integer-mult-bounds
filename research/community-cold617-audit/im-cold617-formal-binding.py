import pathlib,json,gzip,ast,re,hashlib,subprocess
from fractions import Fraction
root=pathlib.Path('/tmp/integer-mult-family588'); audit=root/'research/community-cold617-audit'
def lit(text,name):
 m=re.search(r'^def '+name+r'\s[^\n]*?:=\s*\[',text,re.M);assert m,name
 start=m.end()-1;depth=0
 for i in range(start,len(text)):
  if text[i]=='[':depth+=1
  elif text[i]==']':
   depth-=1
   if not depth:return ast.literal_eval(text[start:i+1])
 raise ValueError(name)
p=root/'research/lean-current-r420-boundary-interfaces'; body=(p/'CurrentR420BoundaryData.lean').read_text();old=pathlib.Path('/tmp/im-cold617-replay/lean612-macos/SelectedBitCarrierBoundaryData.lean').read_text();oldB=pathlib.Path('/tmp/im-cold617-replay/lean612-macos/SelectedBitCarrierPhaseBData.lean').read_text()
raw=(root/'research/e8-bit-r420/data/bitE8mut-r420.json.gz').read_bytes(); d=json.loads(gzip.decompress(raw));pin=json.load(open(p/'SOURCE_BINDING.json'))['input'];assert hashlib.sha256(raw).hexdigest()==pin['compressed_sha256'];assert hashlib.sha256(gzip.decompress(raw)).hexdigest()==pin['decoded_sha256']
orderline=next(s for s in body.splitlines() if s.startswith('def frameOrder'))
order=list(map(int,re.findall('⟨([0-9]+), by decide⟩',orderline)));oldframes=lit(old,'frames')
assert [oldframes[i] for i in order]==d['frames'];assert lit(old,'lines')==d['lines'];assert lit(old,'final')[:660]==d['final'];assert list(range(2,122))+[0]*540==d['start'];assert lit(body,'ret')==d['ret']
b=lit(body,'firstTargets')+lit(body,'sourceMiddle')+lit(body,'lastTargets');assert json.loads(json.dumps(b))==d['B'];assert json.loads(json.dumps(lit(oldB,'scatter')))==d['scatter']
(audit/'pr612/lean/SOURCE-CORRESPONDENCE.json').write_text(json.dumps({'status':'PASS_LITERAL_R420_SOURCE_CORRESPONDENCE','input_sha256':pin['compressed_sha256'],'fields':['frames (ordered permutation)','lines','final','start','ret','B (ordered operands)','scatter'],'B_gates':len(b)},indent=2)+'\n')
p=root/'research/lean-current588-native-moment';d=json.load(open(p/'SOURCE_BINDING.json'));commit=d['context']['source_commit']
for pin in d['source_pins']:
 raw=subprocess.check_output(['git','show',commit+':'+pin['repository_path']],cwd=root);assert hashlib.sha256(raw).hexdigest()==pin['sha256']
a=json.loads(subprocess.check_output(['git','show',commit+':'+d['context']['certificate']],cwd=root))
text=(p/'Current588NativeRealEnclosure.lean').read_text();real=text.split('private noncomputable def ordinaryRealMoment : ℝ :=')[1].split('/--')[0]
pairs=re.findall(r'\(\(\((\d+) \* (\d+) : Nat\)',real);assert len(pairs)==9
assert {int(k):int(v) for k,v in pairs}=={int(k):v for k,v in a['complex_profile'].items()}
b=(p/'Current588NativeUpperAggregate.lean').read_text();m=re.search(r'def bCurrent : Rat := \(\((\d+) : Rat\) / (\d+)\)',b);assert m and Fraction(int(m[1]),int(m[2]))==Fraction(a['complex_lower'])
(audit/'pr605/lean/SOURCE-CORRESPONDENCE.json').write_text(json.dumps({'status':'PASS_PINNED_PR588_REAL_PROFILE_AND_SAVING','source_commit':commit,'profile':a['complex_profile'],'complex_lower':a['complex_lower'],'source_pins_checked':len(d['source_pins'])},indent=2)+'\n')
print('PASS both literal source correspondences')
