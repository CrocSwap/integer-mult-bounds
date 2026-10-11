"""Restore exact public PR410 and PR409 native bytes from four ASCII carriers.

All193 PR410 files and all221 files in PR409's five native package trees
are included. Complete source restoration is separate from claims about
which default verifiers the wrapper executes. Original notices remain.
Transport prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path,PurePosixPath
from hashlib import sha256,sha1
import base64,json,lzma,struct

if not __debug__:
    raise RuntimeError('Native source restoration requires assertions enabled')

MAGIC=b'PR410409NATIVE1\n'
COMMITS=('95ad14d5359d62a89e7bb06eb59b68029e77fb6f','212e03d7665d08fc6a037d3e33612cb7fc60874d')
INDEX_SHA='d729eb40f0aff1ac0415c4cb386f61afc7d9fe7a8fb9e578ed22db8496874e0c'
FILES_SHA='2fba535bd32fa6c5f572d9b64ca65bc03b923ce41f83d7ac0a97cab4e4e91be0'
MANIFESTS={
    'pr410':('4c4f0cadf2c292d393fdad8bbd4fe72f66328dff92e6f384ae63ebc746734b89',192),
    'pr409/research/e8-response-bank64':('a80c80f7c181f8ae7d7fc4c6e48688da16c69048ea184ec192fff54787a93b2b',17),
    'pr409/research/e8-response-resynth-bank64':('817fd9a12a9269a1ab5f1cbb24c409cc9f33ff9753ccb4061797b3410edb3bc0',22),
    'pr409/research/e8-sequential-gauges':('6b413975d40af48fc15ef2a554b3e1f442f8affaafd9da86bdd57d12478b2b19',15),
    'pr409/research/e8-shared-donor-chains':('19c8820253e1ed55e0cdbd48e255aff489c5681017a8a2041178e64155295b24',153),
    'pr409/research/e8-shared-donor-resynth':('3461e4db1905f76b08de76dbaafbe48fd0f953010bb72badb37d9fcff448470f',9),
}
digest=lambda b:sha256(b).hexdigest()

def unique(pairs):
    result={}
    for key,value in pairs:
        assert key not in result,'duplicate JSON key'
        result[key]=value
    return result

def read_json(raw):return json.loads(raw,object_pairs_hook=unique)

def safe_path(name):
    assert isinstance(name,str) and name and '\\' not in name and ':' not in name and '\x00' not in name
    p=PurePosixPath(name)
    assert not p.is_absolute() and str(p)==name and all(x not in ('','.','..') for x in p.parts)
    return name

def parse_archive(raw,meta):
    assert len(raw)==meta['archive_bytes']<=9_000_000 and digest(raw)==meta['archive_sha256']
    assert raw.startswith(MAGIC) and len(raw)>=len(MAGIC)+8
    position=len(MAGIC);length=struct.unpack('<Q',raw[position:position+8])[0];position+=8
    assert 0<length<=100_000 and position+length<=len(raw)
    head=raw[position:position+length];position+=length;index=read_json(head)
    assert set(index)=={'files','blobs'} and json.dumps(index,sort_keys=True,separators=(',',':')).encode()==head
    expected=meta['files'];assert len(expected)==meta['file_count']==414
    assert digest(json.dumps(expected,sort_keys=True,separators=(',',':')).encode())==FILES_SHA
    assert len(index['files'])==414 and set(index['files'])==set(expected)
    for name,value in index['files'].items():
        safe_path(name);assert value==expected[name]['sha256']
    blobs={};previous='';assert len(index['blobs'])==meta['unique_blobs']<=414
    for entry in index['blobs']:
        assert set(entry)=={'sha256','size'}
        key,size=entry['sha256'],entry['size']
        assert isinstance(key,str) and len(key)==64 and key>previous
        assert isinstance(size,int) and not isinstance(size,bool) and 0<=size<=9_000_000
        assert position+size<=len(raw)
        data=raw[position:position+size];position+=size;assert digest(data)==key
        blobs[key]=data;previous=key
    assert position==len(raw) and set(blobs)==set(index['files'].values())
    files={name:blobs[key] for name,key in index['files'].items()}
    assert sum(map(len,files.values()))==meta['native_bytes']<=20_000_000
    for name,data in files.items():
        pin=expected[name];assert len(data)==pin['bytes'] and digest(data)==pin['sha256']
        assert sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob']
        assert pin['source_commit'] in COMMITS;safe_path(pin['source_path'])
    for prefix,(pin,count) in MANIFESTS.items():
        name=prefix+'/MANIFEST.json';assert digest(files[name])==pin
        manifest=read_json(files[name])['files'];assert len(manifest)==count
        assert manifest=={n.removeprefix(prefix+'/'):digest(b) for n,b in files.items() if n.startswith(prefix+'/') and n!=name}
    return files

def decode_carriers(package,meta):
    package=Path(package)
    assert tuple(s['commit'] for s in meta['sources'])==(COMMITS[0],)+(COMMITS[1],)*5
    assert len(meta['carrier_parts'])==4
    assert isinstance(meta['archive_bytes'],int) and not isinstance(meta['archive_bytes'],bool)
    assert 0<meta['archive_bytes']<=9_000_000
    encoded=[]
    for i,part in enumerate(meta['carrier_parts'],1):
        assert part['name']=='native-sources-%02d.b64'%i
        data=(package/part['name']).read_bytes()
        assert len(data)==part['bytes']<=266000 and digest(data)==part['sha256']
        assert data.endswith(b'\n') and b'\r' not in data
        lines=data[:-1].split(b'\n');assert lines and all(len(x)==76 for x in lines[:-1])
        assert 1<=len(lines[-1])<=76
        text=b''.join(lines);assert len(text)==part['base64_characters'];encoded.append(text)
    text=b''.join(encoded);packed=base64.b64decode(text,validate=True)
    assert base64.b64encode(packed)==text
    assert len(packed)==meta['compressed_bytes']<=2_000_000 and digest(packed)==meta['compressed_sha256']
    decoder=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=64*1024*1024)
    raw=decoder.decompress(packed,max_length=meta['archive_bytes']+1)
    assert decoder.eof and not decoder.unused_data,'truncated or concatenated XZ stream'
    return parse_archive(raw,meta)

def restore(package,output):
    """Return {'pr410': complete native package, 'pr409': sequential package}."""
    package,output=Path(package).resolve(),Path(output).resolve()
    assert package.is_dir() and not output.exists(),'source restore needs a fresh output directory'
    assert not output.is_relative_to(package),'native sources must be outside the carrier package'
    raw=(package/'native-source-index.json').read_bytes();assert digest(raw)==INDEX_SHA
    meta=read_json(raw);files=decode_carriers(package,meta)
    output.mkdir(parents=True)
    for name,data in sorted(files.items()):
        path=output/safe_path(name);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    check(package,output)
    return {'pr410':output/'pr410','pr409':output/'pr409/research/e8-sequential-gauges'}

def check(package,output):
    """Verify the complete restored inventory before and after scientific replay."""
    package,output=Path(package).resolve(),Path(output).resolve()
    raw=(package/'native-source-index.json').read_bytes();assert digest(raw)==INDEX_SHA
    meta=read_json(raw);assert output.is_dir()
    assert not any(p.is_symlink() for p in output.rglob('*'))
    actual={p.relative_to(output).as_posix():digest(p.read_bytes()) for p in output.rglob('*') if p.is_file()}
    assert actual=={name:pin['sha256'] for name,pin in meta['files'].items()} and len(actual)==414
    return dict(status='PASS_EXACT_414_NATIVE_SOURCE_INVENTORY',file_count=414,index_sha256=INDEX_SHA)

if __name__=='__main__':
    import sys
    assert len(sys.argv)==3
    print(json.dumps({k:str(v) for k,v in restore(*sys.argv[1:]).items()},sort_keys=True))
