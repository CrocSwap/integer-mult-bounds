"""Restore byte-identical pinned PR401 sources in a fresh output directory.

The four ASCII carriers preserve original binary files, CRLFs and terminal
newline state. All scientific sources and notices are upstream originals.
This transport is prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path,PurePosixPath
from hashlib import sha256,sha1
import base64,json,lzma,struct

if not __debug__:
    raise RuntimeError('PR401 source restoration requires assertions enabled')

HERE=Path(__file__).resolve().parent
COMMIT='7844f72c6051a4408284c3092490687061675c1a'
MANIFEST_SHA='5ff08a6c7b051d227fcd516542b56718ae65bca93615acfe09cb8785d8e3f43c'
MAGIC=b'PR401NATIVE1\n'
digest=lambda b:sha256(b).hexdigest()

def unique(pairs):
    result={}
    for key,value in pairs:
        assert key not in result,'duplicate JSON key'
        result[key]=value
    return result

def read_json(raw):return json.loads(raw,object_pairs_hook=unique)

def safe_path(name):
    assert isinstance(name,str)and name and '\\'not in name and ':'not in name and '\x00'not in name
    p=PurePosixPath(name)
    assert not p.is_absolute()and str(p)==name and all(x not in ('','.','..')for x in p.parts)
    return name

def parse_archive(raw,meta):
    assert len(raw)==meta['archive_bytes']<=8_000_000
    assert digest(raw)==meta['archive_sha256']
    assert raw.startswith(MAGIC)and len(raw)>=len(MAGIC)+8
    position=len(MAGIC);length=struct.unpack('<Q',raw[position:position+8])[0];position+=8
    assert 0<length<=100_000 and position+length<=len(raw)
    head=raw[position:position+length];position+=length;index=read_json(head)
    assert set(index)=={'files','blobs'}
    assert json.dumps(index,sort_keys=True,separators=(',',':')).encode()==head
    expected=meta['files'];assert len(expected)==meta['file_count']==136
    assert len(index['files'])==136 and set(index['files'])==set(expected)
    for name,value in index['files'].items():
        safe_path(name);assert value==expected[name]['sha256']
    blobs={};previous=''
    assert len(index['blobs'])==meta['unique_blobs']<=136
    for entry in index['blobs']:
        assert set(entry)=={'sha256','size'}
        key,size=entry['sha256'],entry['size']
        assert isinstance(key,str)and len(key)==64 and key>previous
        assert isinstance(size,int)and not isinstance(size,bool)and 0<=size<=8_000_000
        assert position+size<=len(raw)
        data=raw[position:position+size];position+=size
        assert digest(data)==key
        blobs[key]=data;previous=key
    assert position==len(raw)and set(blobs)==set(index['files'].values())
    files={name:blobs[key]for name,key in index['files'].items()}
    assert sum(map(len,files.values()))==meta['native_bytes']<=8_000_000
    for name,data in files.items():
        pin=expected[name];assert len(data)==pin['bytes']and digest(data)==pin['sha256']
        assert sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob']
    assert digest(files['MANIFEST.json'])==MANIFEST_SHA==meta['manifest_sha256']
    manifest=read_json(files['MANIFEST.json'])['files']
    assert len(manifest)==meta['manifest_members']==135
    assert manifest=={name:digest(data)for name,data in files.items()if name!='MANIFEST.json'}
    return files

def decode_carriers(meta):
    assert meta['source']['commit']==COMMIT
    assert len(meta['carrier_parts'])==4
    assert isinstance(meta['archive_bytes'],int) and not isinstance(meta['archive_bytes'],bool)
    assert 0<meta['archive_bytes']<=8_000_000
    encoded=[]
    for i,part in enumerate(meta['carrier_parts'],1):
        assert part['name']=='pr401-native-%02d.b64'%i
        data=(HERE/part['name']).read_bytes()
        assert len(data)==part['bytes']<=266000 and digest(data)==part['sha256']
        assert data.endswith(b'\n')and b'\r'not in data
        lines=data[:-1].split(b'\n');assert lines and all(len(x)==76 for x in lines[:-1])
        assert 1<=len(lines[-1])<=76
        text=b''.join(lines);assert len(text)==part['base64_characters']
        encoded.append(text)
    text=b''.join(encoded);packed=base64.b64decode(text,validate=True)
    assert base64.b64encode(packed)==text
    assert len(packed)==meta['compressed_bytes']<=2_000_000 and digest(packed)==meta['compressed_sha256']
    decoder=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=64*1024*1024)
    raw=decoder.decompress(packed,max_length=meta['archive_bytes']+1)
    assert decoder.eof and not decoder.unused_data,'truncated or concatenated XZ stream'
    return parse_archive(raw,meta)

def restore(output):
    """Return native package Path; reject every existing output path."""
    output=Path(output).resolve()
    assert not output.exists(),'source restore needs a fresh output directory'
    assert not output.is_relative_to(HERE),'native sources must be outside the carrier package'
    meta=read_json((HERE/'pr401-source.json').read_bytes())
    files=decode_carriers(meta)
    output.mkdir(parents=True)
    for name,data in sorted(files.items()):
        path=output/safe_path(name);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    actual={p.relative_to(output).as_posix():digest(p.read_bytes())for p in output.rglob('*')if p.is_file()}
    assert actual=={name:pin['sha256']for name,pin in meta['files'].items()}
    assert len(actual)==136
    return output

if __name__=='__main__':
    import sys
    assert __debug__ and len(sys.argv)==2
    print(restore(sys.argv[1]))
