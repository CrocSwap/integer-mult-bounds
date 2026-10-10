#!/usr/bin/env python3
"""Regenerate the selected functional architecture reference and its indexes.

No Graphviz is used. Diagrams are vector paths in deterministic ReportLab PDFs.
The source package is read-only. The default build writes only to a new --output.
--emit-json produces the same ASCII artifacts on stdout for managed write tools.
"""
from __future__ import annotations
import argparse, base64, hashlib, io, json, math, re, sys
import reportlab
from pathlib import Path
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, StreamObject
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import joint259_system_docs_hierarchy_views as hierarchy_views
import joint259_system_docs_previews as previews
import joint259_system_docs_sources as source_views
BASE=Path(__file__).resolve().parent
PREFIX="joint259_system_docs"
MODEL=BASE/(PREFIX+"_model.json")
W,H=1120,790
INK="#142D3A"; BLUE="#176B8B"; TEAL="#147D77"; GOLD="#B2761B"; PALE="#EAF4F7"; MUTED="#526873"; RED="#99432F"
FONT="Vera"
for name,file in [(FONT,"Vera.ttf"),(FONT+"-Bold","VeraBd.ttf")]:
    pdfmetrics.registerFont(TTFont(name,str(Path(reportlab.__file__).parent/"fonts"/file)))
def sha(b):return hashlib.sha256(b).hexdigest()
def stable(obj):return json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=True)+"\n"
def validate_model(model):
    blocks={b['id']:b for b in model['blocks']}
    if len(blocks)!=len(model['blocks']):raise ValueError('Duplicate block ID')
    req={r['id']for r in model['requirements']}
    if len(req)!=len(model['requirements']):raise ValueError('Duplicate requirement ID')
    ids=set();fed=set()
    for b in blocks.values():
        if not set(b['requirements'])<=req:raise ValueError('Unknown requirement '+b['id'])
    for edge in model['edges']:
        if edge['id'] in ids:raise ValueError('Duplicate edge ID')
        ids.add(edge['id'])
        if edge['from'] not in blocks or edge['to'] not in blocks:raise ValueError('Unknown edge endpoint')
        for direction,bid,field in [('outputs',edge['from'],'out'),('inputs',edge['to'],'in')]:
            ports={p.split(':',1)[0]for p in blocks[bid][direction]}
            if edge[field] not in ports:raise ValueError('Undeclared port '+edge['id']+' '+bid+'.'+edge[field])
        fed.add((edge['to'],edge['in']))
    for e in model.get('external_inputs',[]):
        if e['block'] not in blocks or e['port'] not in {p.split(':',1)[0]for p in blocks[e['block']]['inputs']}:raise ValueError('Unknown external port')
        fed.add((e['block'],e['port']))
    required={(b['id'],p.split(':',1)[0])for b in blocks.values()for p in b['inputs']}
    if required-fed:raise ValueError('Unbound input ports: '+str(sorted(required-fed)))
def source_index(root,model):
    refs={}
    for b in model["blocks"]:
        for token in b["sources"]:
            path,anchor=token.split("|",1)
            text=(root/path).read_text();lines=text.splitlines()
            found=[i for i,line in enumerate(lines) if anchor in line]
            if not found:raise ValueError("Missing source anchor: "+token)
            i=found[0];key="S%02d"%(len(refs)+1)
            if token in refs:continue
            refs[token]={"id":key,"path":path,"anchor":anchor,"line":i+1,"sha256":sha((root/path).read_bytes()),"excerpt":" ".join(lines[i:i+2]).strip()[:205]}
    return refs
class Doc:
    def __init__(self,kind,model,refs):
        self.kind,self.model,self.refs=kind,model,refs
        self.buf=io.BytesIO();self.c=canvas.Canvas(self.buf,pagesize=(W,H),pageCompression=0,invariant=1)
        self.c.setTitle(model["title"]);self.c.setAuthor("Henry Grant; prepared with OpenAI assistance")
        self.n=0;self.ids=set();self.links=[];self.used_blocks=set();self.pages=[];self.boxes=[]
    def text(self,x,y,text,size=12,color=INK,width=990,bold=False,leading=None):
        initial_y=y
        self.c.setFillColor(HexColor(color));self.c.setFont(FONT+("-Bold" if bold else ""),size)
        leading=leading or size*1.35
        for line in str(text).split("\n"):
            pieces=simpleSplit(line,FONT+("-Bold" if bold else ""),size,width) or [""]
            for p in pieces:self.c.drawString(x,y,p);y-=leading
        if initial_y>39 and y<39:raise ValueError("Text overflow page %s: %s"%(self.n,str(text)[:90]))
        return y
    def link(self,x,y,text,target,width=None,size=10):
        width=width or self.c.stringWidth(text,FONT,size)
        self.text(x,y,text,size,BLUE,width=width+8)
        self.c.linkRect("",target,(x,y-3,x+width,y+size+2),relative=0,thickness=0)
        self.links.append((self.n,target))
    def page(self,key,title,kicker):
        if self.n:self.c.showPage()
        self.n+=1;self.ids.add(key);self.pages.append({"id":key,"title":title,"page":self.n})
        self.c.bookmarkPage(key);self.c.addOutlineEntry(title,key,0,False)
        self.c.setFillColor(HexColor("#F7FAFB"));self.c.rect(0,0,W,H,fill=1,stroke=0)
        self.text(42,H-33,kicker.upper(),10,TEAL,bold=True)
        self.text(42,H-71,title,25,INK,bold=True)
        self.text(42,23,"SELECTED HYBRID | science archive 9f6d8637... | conditional construction",9,MUTED)
        self.text(W-95,23,str(self.n),10,MUTED)
        if key!="CONTENTS":self.link(W-160,H-33,"Contents","CONTENTS",100)
    def panel(self,x,y,w,h,title,text,color=BLUE,compact=False):
        self.c.setFillColor(white);self.c.setStrokeColor(HexColor("#C8D9DF"))
        self.c.roundRect(x,y,w,h,8,fill=1,stroke=1)
        self.c.setFillColor(HexColor(color));self.c.roundRect(x,y+h-6,w,6,2,fill=1,stroke=0)
        yy=self.text(x+15,y+h-28,title,11.5 if compact else 13,color,w-30,True)
        yy=self.text(x+15,yy-7,text,9.5 if compact else 11,INK,w-30,leading=12.5 if compact else 15)
        if yy<y+8:raise ValueError("Panel overflow: "+title)
    def node(self,bid,x,y,w=187,h=104):
        b=next(z for z in self.model["blocks"] if z["id"]==bid)
        self.used_blocks.add(bid)
        self.panel(x,y,w,h,bid+"  "+b["name"],b["brief"],BLUE,True)
        self.link(x+14,y+11,"Ports, proof and explanation","B_"+bid,w-25,9)
        return (x,y,w,h)
    def arrow(self,a,b,label="",color=TEAL):
        x1,y1,w1,h1=a;x2,y2,w2,h2=b
        if abs(y1-y2)<5:
            if x2>x1:p=(x1+w1,y1+h1/2);q=(x2,y2+h2/2)
            else:p=(x1,y1+h1/2);q=(x2+w2,y2+h2/2)
        else:
            p=(x1+w1/2,y1 if y2<y1 else y1+h1);q=(x2+w2/2,y2+h2 if y2<y1 else y2)
        self.c.setStrokeColor(HexColor(color));self.c.setFillColor(HexColor(color));self.c.setLineWidth(1.5)
        self.c.line(*p,*q)
        ang=math.atan2(q[1]-p[1],q[0]-p[0]);s=7
        path=self.c.beginPath();path.moveTo(*q)
        path.lineTo(q[0]-s*math.cos(ang-.45),q[1]-s*math.sin(ang-.45));path.lineTo(q[0]-s*math.cos(ang+.45),q[1]-s*math.sin(ang+.45));path.close()
        self.c.drawPath(path,fill=1,stroke=0)
        if label:self.text((p[0]+q[0])/2+5,(p[1]+q[1])/2+7,label,9,color,width=160)
    def bookmark(self,key):
        self.ids.add(key);self.c.bookmarkPage(key)
    def finish(self):
        missing=set(t for _,t in self.links)-self.ids
        if missing:raise ValueError("Broken internal links "+str(missing))
        self.c.save();raw=self.buf.getvalue()
        writer=PdfWriter();writer.clone_document_from_reader(PdfReader(io.BytesIO(raw)))
        for obj in writer._objects:
            if isinstance(obj,StreamObject):
                data=obj.get_data()
                obj._data=base64.a85encode(data)+b"~>"
                obj[NameObject("/Filter")]=NameObject("/ASCII85Decode")
                obj.pop(NameObject("/DecodeParms"),None)
                if hasattr(obj,"decoded_self"):obj.decoded_self=None
        buf=io.BytesIO();writer.write(buf);raw=buf.getvalue()
        # ReportLab's four high-bit header bytes are a binary-file marker only.
        # Replace with same-length ASCII so this PDF can be persisted losslessly
        # through a text patch. Streams use ASCII85; offsets stay unchanged.
        raw=raw.replace(b"%\x93\x8c\x8b\x9e",b"%ASCI",1).replace(b"%\xe2\xe3\xcf\xd3",b"%ASCI",1)
        raw.decode("ascii")
        r=PdfReader(io.BytesIO(raw));assert len(r.pages)==self.n
        for page in r.pages:assert (page.extract_text()or"").strip()
        return raw,{"pages":self.pages,"internal_links":len(self.links),"blocks":sorted(self.used_blocks),"sha256":sha(raw)}
def cover(d):
    d.page("CONTENTS","The selected construction, at three levels","Functional architecture and compiler workflow")
    d.text(42,673,d.model["title"],14,INK,width=1000,bold=True)
    d.panel(42,458,500,155,"THE NUMERICAL CONTRACT","513 retained PR259 cohorts + seven delayed-inverse intervals + the same 25 PR258/260 retimings applied once.\nConditional kappa: 0.000711045547624400.\nLiteral stock 867,045; 19,786,600 paid children.",TEAL)
    d.panel(566,458,512,155,"HOW TO READ THE CONNECTIONS",str(len(d.model['blocks']))+" current blocks and "+str(len(d.model['edges']))+" typed block dependencies. All 87 original hierarchy IDs are reconciled separately.\nArchitecture views show high-level process and compiler flow. Inherited all-size internals remain contracts.",GOLD)
    y=418
    d.link(46,y,"Full integer-product hierarchy and all 87 original blocks","H_SYSTEM",850,12);y-=27
    for key,t in [("FVIEW1","Functional: source-bound local supplier"),("FVIEW2","Functional: global assembly and exact closure")]:
        d.link(46,y,t,key,600,13);y-=29
    for key,t in [("CATALOG","Block catalog: what, why, ports, requirements and proof"),("REQUIREMENTS","Requirements and source traceability"),("SOURCES","Exact source anchors and hashes"),("SCOPE","Coverage, heritage and reproduction boundary")]:
        d.link(46,y,t,key,820,12);y-=27
    d.text(46,y-12,"Navigation: clickable blocks open the catalog; source IDs open exact proof anchors; every page returns here.",11,MUTED,width=1000)
def fviews(d):
    d.page("FVIEW1","Functional architecture | local supplier","Actual compiler flow; not experiment chronology")
    positions={}
    ids=["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10"]
    for i,b in enumerate(ids):
        row=i//5;col=i%5 if row==0 else 4-i%5
        positions[b]=d.node(b,42+col*210,496-row*181,190,113)
    for i in range(9):d.arrow(positions[ids[i]],positions[ids[i+1]])
    d.text(42,663,"Pinned source recipes -> literal records -> selected compatible transformations -> independently checked payload.",13,MUTED)
    d.panel(42,126,510,141,"ONE COMPOSITION","The kernel and interval transforms share the exact PR249 base. Five conflicting quartets are removed before the seven intervals enter. The interval helper prefix columns are checked against all retained cohort operands.",TEAL)
    d.panel(575,126,503,141,"STABLE IDENTITIES","F06 output: 2e0bc2a5... (exact PR249 base)\nF08 output: 6ab38175... (joint replacement)\nF09 output: acf510b1... (25 retimings once)\nFull digests are in the catalog and source index.",BLUE)
    d.text(44,82,"Cross-edges: F01 supplies all selections; F06 supplies the interval witness base. F09 also feeds F11/F15 on the next sheet.",11,MUTED)
    d.page("FVIEW2","Functional architecture | complete conditional closure","Independent evidence flows meet before admission")
    pos={}
    for bid,x,y in [("F11",42,509),("F12",253,509),("F13",464,509),("F14",675,509),("F15",886,509),("F16",42,327),("F17",253,327),("F18",464,327),("F19",675,327),("F20",886,327),("F21",675,142)]:
        pos[bid]=d.node(bid,x,y,190,118)
    for a,b in [("F11","F12"),("F12","F13"),("F13","F14"),("F16","F17"),("F17","F18"),("F18","F19"),("F15","F20"),("F19","F21"),("F20","F21")]:d.arrow(pos[a],pos[b])
    d.arrow(pos["F14"],pos["F17"],"literal profile")
    d.text(42,663,"The bit and complex suppliers remain distinct. Scalar, geometric, bank, moment and finite proof ports must all close.",13,MUTED)
    d.panel(42,128,589,135,"SIDE INPUTS AND BOUNDARIES","F10 semantics/prefix and F15 geometry/primes feed F20. F11 records feed F14; F16 guards also feed F19. The connection index names all declared block inputs.\nF21 requires raw, bit, scalar, primes, banks, complex, math and finite results, then rechecks the source manifest.",TEAL)
    d.text(42,77,"The arrows are compiler/proof dataflow. No local optimization or individual PR contributes an independent additive kappa gain.",11,MUTED)
def catalog(d):
    for i in range(0,len(d.model["blocks"]),2):
        bs=d.model["blocks"][i:i+2]
        d.page("CATALOG" if i==0 else "CATALOG%02d"%i,"Functional blocks | "+" + ".join(b["id"] for b in bs),"What / why / ports / invariants / heritage / proof")
        for n,b in enumerate(bs):
            d.bookmark("B_"+b["id"]);d.used_blocks.add(b["id"])
            x=43+n*530;y=669
            y=d.text(x,y,b["id"]+"  "+b["name"],20,INK,495,True)-6
            for title,value in [("WHAT",b["what"]),("WHY",b["why"]),("INPUT PORTS","; ".join(b["inputs"])),("OUTPUT PORTS","; ".join(b["outputs"])),("REQUIREMENTS"," ".join(b["requirements"])),("INVARIANTS"," ".join(b["invariants"])),("HERITAGE",b["heritage"])]:
                y=d.text(x,y,title,9,TEAL,495,True)-1
                y=d.text(x,y,value,11,INK,495,leading=14.2)-10
            y=d.text(x,y,"PROOF / IMPLEMENTATION",9,TEAL,495,True)-3
            for token in b["sources"]:
                r=d.refs[token];d.link(x,y,r["id"]+"  "+r["path"]+" : "+str(r["line"]),"SRC_"+r["id"],480,9);y-=18
            if y<58:raise ValueError("Block catalog overflow "+b["id"])
def requirements(d):
    for start in [0,6]:
        d.page("REQUIREMENTS" if start==0 else "REQUIREMENTS2","Requirement traceability | %d-%d"%(start+1,start+6),"Derived construction obligations; not a new theorem specification")
        y=673
        for r in d.model["requirements"][start:start+6]:
            owners=[b["id"] for b in d.model["blocks"] if r["id"] in b["requirements"]]
            y=d.text(43,y,r["id"]+"  "+r["name"],15,TEAL,bold=True)
            y=d.text(43,y-5,r["text"],12,INK,1020)
            x=43
            for bid in owners:d.link(x,y-2,bid,"B_"+bid,46,10);x+=53
            y-=39
def sources(d):
    values=list(d.refs.values())
    for i in range(0,len(values),8):
        d.page("SOURCES" if i==0 else "SOURCES%d"%i,"Source anchors | %d-%d"%(i+1,min(i+8,len(values))),"Pinned active implementation and proof locations")
        y=672
        for r in values[i:i+8]:
            d.bookmark("SRC_"+r["id"])
            y=d.text(43,y,r["id"]+"  "+r["path"]+" : "+str(r["line"]),13,TEAL,bold=True)
            y=d.text(43,y-2,r["anchor"],10,INK,1010)
            y=d.text(43,y-1,"SHA256 "+r["sha256"],9,MUTED,1010)-17
def scope(d):
    d.page("SCOPE","Coverage and publication boundary","Source-faithful documents; scientific replay is separate")
    sections=[
    ("Selected active heritage","PR249's 21 transported entrances -> PR259's 513 retained cohorts (five quartets removed) + seven new delayed-inverse intervals -> 25 same-gate PR258/PR260 retimings once. PR254 is ancestry, not another additive saving. PR251's extra sixteen entrances are excluded."),
    ("Architectural and theorem heritage","PR234 supplies Henry Grant / hcg890's five-stage architecture and finite interfaces. PR237 is a prior width-120 bank extension; no exclusive priority is claimed. The source527 and completed-bank chains retain all upstream licenses and contributor notices. Complex source is Jacob Sussman's f010392 snapshot; PR209 is its documentation pointer, and PR193 supplies the helper lineage."),
    ("Coverage stated exactly","The current architecture catalog and dependency index account for every declared block input port. All 87 original hierarchy IDs are explicitly reconciled. The visual views summarize architecture and compiler flow; reference pages preserve source and requirement traceability. Inherited theorem internals remain unexpanded."),
    ("Evidence and pending checks","The recorded cloud admission freshly executed changed stages and reused byte/AST-bound unchanged signed-source and complex evidence. Mac standalone replay has now reported all eight stages passing with 143 unchanged source files. This explicit PR259 hybrid checkpoint remains mathematically conditional and is below the later PR266 frontier. Documentation checks are separate from scientific replay."),
    ("Public follow-up only","Construction checkpoint PR #277: https://github.com/CrocSwap/integer-mult-bounds/pull/277. Public source commit c2f07d311bfdad0d89bf961e4da133ee97bb78de is linked in README.md. Source anchors retain exact relative paths, symbols, line numbers and hashes. The historical combined_system_schematic_20261010 generator is preserved unchanged.")
    ]
    y=666
    for title,body in sections:
        y=d.text(43,y,title,15,TEAL,bold=True)-4;y=d.text(43,y,body,12,INK,1018)-21
    d.page("BUILD","Reproduce the architecture reference","Pinned Python dependencies; no Graphviz requirement")
    y=672
    for title,body in [
    ("Install","Python 3.11+; python -m pip install -r joint259_system_docs_requirements.txt. Pinned reportlab 4.4.9, pypdf 6.10.0, Pillow 12.3.0, charset-normalizer 3.5.1. Graphviz is not used or required."),
    ("Architecture build command","python -B joint259_system_docs_incremental.py --source /path/to/public-package --output joint259-docs-build --svg. An admitted source ZIP also works. Actual consumed manifest is recorded separately from the tested science archive in source_binding.json and QA.json."),
    ("Outputs","functional_architecture.pdf; summary-functional.svg; QA.json; incremental_receipt.json. The retained renderer also emits local source, requirement and dependency indexes from the same pinned source."),
    ("Automatic reproducibility checks","Build every PDF twice in memory and require byte-identical SHA256, unchanged manifest, no missing/extra source files, valid proof anchors, all catalog block IDs present, all internal links resolved, nonempty extractable page text and no layout overflow. QA.json records counts, pins and output digests."),
    ("Independent visual check","Use Poppler: pdftoppm -png -r 100 functional_architecture.pdf review/page. Inspect every page for clipping, missing glyphs and readable connectors. Poppler is an optional renderer, not a generation dependency; record its actual version in visual QA."),
    ("Scientific verification remains separate","From a clean source package, use Python 3.11+ and SymPy 1.14.0 with assertions enabled: python -B verify.py --output /new/output/directory. Never write inside the immutable source package; never use -O. A successful documentation build is not an all-eight-stage science replay.")
    ]:
        y=d.text(43,y,title,15,TEAL,bold=True)-5;y=d.text(43,y,body,12,INK,1015)-25
def render(kind,model,refs):
    if kind != "functional":raise ValueError("Unsupported architecture output kind")
    validate_model(model)
    d=Doc(kind,model,refs);cover(d)
    hierarchy_views.overview(d);hierarchy_views.transforms(d)
    fviews(d)
    catalog(d);hierarchy_views.catalog(d);hierarchy_views.connections(d);hierarchy_views.requirements(d);requirements(d);sources(d);scope(d)
    return d.finish()
def integrity(root,expected):
    return source_views.integrity(root,expected)
def main(source_override=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path);ap.add_argument("--emit-json",action="store_true");args=ap.parse_args()
    model=json.loads(MODEL.read_text());root=source_views.open_source(source_override if source_override is not None else args.source.resolve());count=integrity(root,model["source_manifest_sha256"]);refs=source_index(root,model)
    consumed_manifest=sha((root/'MANIFEST.json').read_bytes())
    source_binding={**source_views.BINDING,'consumed_manifest_sha256':consumed_manifest,'consumed_manifest_members':count,'consumed_total_paths':count+1,'source_binding_configuration_sha256':sha((BASE/'joint259_system_docs_source_binding.json').read_bytes())}
    files={};reports={}
    for kind,name in [("functional","functional_architecture.pdf")]:
        one,report=render(kind,model,refs);two,_=render(kind,model,refs)
        if one!=two:raise ValueError("Nondeterministic "+kind)
        files[name]=one.decode("ascii");reports[name]=report
    index={"schema":"selected-functional-architecture/1","source_manifest_sha256":model["source_manifest_sha256"],"level":"functional architecture block dependencies","complete_individual_operation_inventory":False,"blocks":model["blocks"],"block_edges":model["edges"],"unexpanded":["all-size weighted compiler internals","full GL-cover and common-ancestor charts","restored-row and routing primitive internals","prime-supply theorem","recovery theorem","complex symbolic and analytic theorems"],"coverage_limits":["Block dependencies describe architecture and compiler/proof flow, not individual physical-operation wires.","The visual views and reference indexes do not expand inherited theorem internals."]}
    files["connection_index.json"]=stable(index)
    index['source_manifest_sha256']=consumed_manifest
    index['scientific_archive_manifest_sha256']=model['source_manifest_sha256']
    files["connection_index.json"]=stable(index)
    files['source_binding.json']=stable(source_binding)
    files["source_index.json"]=stable(list(refs.values()))
    files["requirement_traceability.json"]=stable([{**r,"blocks":[b["id"]for b in model["blocks"]if r["id"]in b["requirements"]]}for r in model["requirements"]])
    files["diagram_model.json"]=stable(model)
    files["hierarchy_reconciliation.json"]=stable(hierarchy_views.DATA)
    files["hierarchy_edges.json"]=stable(hierarchy_views.EDGES)
    files.update(previews.files(model))
    files["scientific_reproduction.json"]=(BASE/'joint259_system_docs_evidence.json').read_text()
    integrity(root,model["source_manifest_sha256"])
    qa={"status":"PASS_DOCUMENT_STRUCTURE_AND_DETERMINISM","source_files":count,"source_manifest_sha256":model["source_manifest_sha256"],"block_count":len(model["blocks"]),"typed_block_edges":len(model["edges"]),"requirements":len(model["requirements"]),"source_anchors":len(refs),"pdfs":reports,"byte_identical_rebuilds":True,"visual_review":"separate; not inferred from structural checks","science_replay":"not run by documentation build","Graphviz":"not used"}
    files["QA.json"]=stable(qa)
    qa['source_manifest_sha256']=consumed_manifest
    qa['scientific_archive_manifest_sha256']=model['source_manifest_sha256']
    qa['source_binding_configuration_sha256']=source_binding['source_binding_configuration_sha256']
    files['QA.json']=stable(qa)
    if args.emit_json:print(stable(files),end="")
    else:
        if not args.output:ap.error("--output or --emit-json required")
        args.output.mkdir(parents=True,exist_ok=False)
        for name,content in files.items():(args.output/name).write_bytes(content.encode("ascii"))
        print(stable(qa),end="")
if __name__=="__main__":main()

