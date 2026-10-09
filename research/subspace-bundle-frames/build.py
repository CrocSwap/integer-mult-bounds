#!/usr/bin/env python3
"""Build a separate frame candidate using the pinned prerequisite archive."""
from pathlib import Path
from hashlib import sha256
import argparse,gzip,io,json,shutil,sys,tempfile,zipfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=ROOT/'research/coordinated-frames-and-entrance-banks'

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--frames',type=Path,default=HERE/'frames.json')
 ap.add_argument('--output',type=Path,required=True)
 args=ap.parse_args()
 if sys.flags.optimize:raise ValueError('Assertions must be enabled')
 assert sha256((BASE/'FILES.json').read_bytes()).hexdigest()=='99709b85d987556593f237b0aacf314b2d7982fb4f494378d6dbf03391228ede'
 for name,h in json.loads((BASE/'FILES.json').read_text())['files'].items():assert sha256((BASE/name).read_bytes()).hexdigest()==h,name
 record=json.loads(args.frames.read_text());frames=record.get('physical_frames',record.get('frames'))
 if frames is None:raise ValueError('Expected physical_frames or frames list')
 if args.output.exists():raise ValueError('Choose a new output directory')
 with tempfile.TemporaryDirectory(prefix='subspace-build-') as tmp:
  source=Path(tmp)/'source';source.mkdir()
  archive=json.loads((BASE/'BASELINE.json').read_text())
  blob=b''.join((BASE/p['file']).read_bytes() for p in archive['parts'])
  assert sha256(blob).hexdigest()==archive['archive_sha256']
  with zipfile.ZipFile(io.BytesIO(blob)) as z:
   for e in z.infolist():assert (source/e.filename).resolve().is_relative_to(source.resolve())
   z.extractall(source)
  sys.path.insert(0,str(source/'scripts'))
  from paired_cube_physical import physical
  selected=BASE/'selected/complex'
  def load(n):return json.loads(gzip.decompress((selected/(n+'.json.gz')).read_bytes()))
  g,fw,w,row,pairs=[load(n) for n in ['graph','frames','word','profile-before','physical-pairs']]
  profile=physical(g,fw,w,row,frames,pairs)
  args.output.mkdir(parents=True)
  for p in selected.iterdir():
   if p.is_file() and p.name!='sinks.json':shutil.copyfile(p,args.output/p.name)
  for name,value in [('physical-frames',frames),('profile',profile)]:
   data=gzip.compress(json.dumps(value,sort_keys=True,separators=(',',':')).encode(),mtime=0)
   (args.output/(name+'.json.gz')).write_bytes(data[:9]+b'\xff'+data[10:])
  pins={p.name:sha256(p.read_bytes()).hexdigest() for p in args.output.glob('*.json.gz')}
  (args.output/'result.json').write_text(json.dumps(dict(pins=pins,status='Discovery candidate; requires complete exact verification'),indent=2)+'\n')
 print('Candidate prepared:',args.output)
if __name__=='__main__':main()
