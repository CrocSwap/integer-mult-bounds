#!/usr/bin/env python3
"""Regenerate both selected-construction diagrams, master PDF and connection index.

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
    d.page("CONTENTS","The selected construction, at three levels","Functional architecture and logical wiring")
    d.text(42,673,d.model["title"],14,INK,width=1000,bold=True)
    d.panel(42,458,500,155,"THE NUMERICAL CONTRACT","513 retained PR259 cohorts + seven delayed-inverse intervals + the same 25 PR258/260 retimings applied once.\nConditional kappa: 0.000711045547624400.\nLiteral stock 867,045; 19,786,600 paid children.",TEAL)
    d.panel(566,458,512,155,"HOW TO READ THE CONNECTIONS",str(len(d.model['blocks']))+" current blocks and "+str(len(d.model['edges']))+" typed block dependencies. All 87 original hierarchy IDs are reconciled separately.\nL01-L05 expand parametric wiring. The literal event inventory is separate; inherited all-size internals remain contracts.",GOLD)
    y=418
    d.link(46,y,"Full integer-product hierarchy and all 87 original blocks","H_SYSTEM",850,12);y-=27
    if d.kind in ("functional","combined"):
        for key,t in [("FVIEW1","Functional: source-bound local supplier"),("FVIEW2","Functional: global assembly and exact closure")]:
            d.link(46,y,t,key,600,13);y-=29
    if d.kind in ("logical","combined"):
        for key,t in [("L01","Logical: stream ABI and state transitions"),("L02","Logical: seven delayed-inverse interval wires"),("L03","Logical: five-stage data-bank wiring"),("L04","Logical: bank address and replica mapping"),("L05","Logical: proof ports and unexpanded interfaces")]:
            d.link(46,y,t,key,750,13);y-=29
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
def lviews(d):
    d.page("L01","Logical wiring | actual stream ABI","Six-field local word to eight-field global record")
    d.panel(42,502,498,148,"LOCAL REGISTER INTERFACE","source s: 0 <= s < 1,760\nold target t: 1,760 <= t < 3,520\nindependent helper h: 3,520 <= h < 20,107\ntemporary work: 20,107, live only inside COPY/ERASE",BLUE)
    d.panel(565,502,513,148,"LOCAL RECORD (op,a,b,c,f,z)","MOVE: (0, q, before, after, rank, 0)\nADD: (1, dst, src, coefficient, common_frame, category)\nCOPY: (2, source, temporary, input_frame, output_frame, rank)\nERASE: (3, source, temporary, input_frame, output_frame, rank)\nThe local center rank is 22 for both COPY and ERASE.",TEAL,True)
    y=419
    for title,txt in [("ADD state transition","dst[v+1] <- dst[v] + coefficient * src[u]; every other payload version survives. MOVE changes address-frame state, not the scalar payload version."),("COPY lifecycle","COPY creates a temporary view of an immutable source in an explicit frame. Its 220 scatter consumers occur before ERASE; reflected stages create a fresh copy and never invert erasure."),("Global record","(op, family_a, family_b, coefficient_or_frame, frame_or_rank, category_or_boundary, stage, complement). Interpretation is opcode-specific; frame fields are never mistaken for stream IDs."),("Connection extraction boundary","The authoritative word has explicit source/destination IDs and lifetime delimiters. SSA-style versions and producer/consumer edges are a derived inventory, not native fields. Block-edge E IDs do not enumerate these operations.")]:
        y=d.text(45,y,title,14,TEAL,bold=True);y=d.text(45,y-5,txt,12,INK,1020)-20
    d.link(45,88,"F03 emitter","B_F03",140);d.link(215,88,"F10 semantic replay","B_F10",180);d.link(430,88,"F11 global ABI","B_F11",165)
    d.page("L02","Logical wiring | delayed target inverse","Exact parametric six-stream network; repeated seven times")
    d.text(42,666,"For one interval j: targets [p,t1,t2,t3], helpers [low,high]. All old target and helper values are arbitrary.",13,MUTED)
    xs=[155,370,585,800,1000];ys=[580,516,452,388,324,260];names=["pivot p","target t1","target t2","target t3","helper low","helper high"]
    for yy,name in zip(ys,names):
        d.text(42,yy-4,name,12,INK,bold=True);d.c.setStrokeColor(HexColor("#C0CFD5"));d.c.line(142,yy,1044,yy)
    for x,lab in zip(xs[1:4],["frame ZERO","L: rank 5 / H: rank 14","K: rank 20"]):d.text(x-73,620,lab,12,TEAL,width=215,bold=True)
    # Three target subtractions, then two pivot compensations, then inverse.
    for yy in ys[1:4]:
        d.c.setStrokeColor(HexColor(BLUE));d.c.line(xs[1],ys[0],xs[1],yy)
        d.c.setFillColor(HexColor(BLUE));d.c.circle(xs[1],yy,6,fill=1,stroke=0);d.text(xs[1]+11,yy+7,"-p",10,BLUE)
    for off,yy,label in [(-15,ys[4],"-low @L"),(15,ys[5],"-high @H")]:
        d.c.setStrokeColor(HexColor(TEAL));d.c.line(xs[2]+off,yy,xs[2]+off,ys[0]);d.c.setFillColor(HexColor(TEAL));d.c.circle(xs[2]+off,ys[0],6,fill=1,stroke=0);d.text(xs[2]-65,yy+12,label,10,TEAL)
    for yy in ys[1:4]:
        d.c.setStrokeColor(HexColor(GOLD));d.c.line(xs[3],ys[0],xs[3],yy)
        d.c.setFillColor(HexColor(GOLD));d.c.circle(xs[3],yy,6,fill=1,stroke=0);d.text(xs[3]+12,yy+7,"+p",10,GOLD)
    d.panel(42,78,502,121,"EXACT ENDPOINT","Each of p,t1,t2,t3 receives -low-high. Helpers retain their values. The literal inverse restores all six columns.\n8 ADDs per interval; 56 total replacement ADDs.",TEAL)
    d.panel(566,78,512,121,"FRAME / OBSERVER CONTRACT","L <= H <= K, with nonzero exact Gram determinants. No surviving external observer crosses the interval. Four retained-cohort cuts see zero on all 14 chosen helper-prefix columns.",GOLD)
    d.link(800,226,"F08 proof and witnesses","B_F08",230)
    d.page("L03","Logical wiring | five-stage data paths","One logical replica; literal expansion repeats forty times")
    d.text(42,666,"Every stage iterates its complete local word for all cover classes. Helper families are reused logically, then banked stage-privately.",13,MUTED)
    lanes=[("X1",578),("Y1",492),("X2",406),("Y2",320)]
    for name,yy in lanes:
        d.text(42,yy-4,name,14,INK,bold=True);d.c.setStrokeColor(HexColor("#C0CFD5"));d.c.line(113,yy,1070,yy)
    pairs=[(0,1),(1,0),(0,1),(3,2),(2,3)]
    for i,((a,b),x) in enumerate(zip(pairs,[175,354,533,712,891])):
        d.text(x-39,620,"stage %d %s"%(i,"R" if i in(1,3)else"F"),13,TEAL,bold=True)
        ya,yb=lanes[a][1],lanes[b][1];d.c.setStrokeColor(HexColor(BLUE));d.c.setLineWidth(2);d.c.line(x,ya,x,yb)
        for yy in [ya,yb]:d.c.setFillColor(HexColor(BLUE));d.c.circle(x,yy,8,fill=1,stroke=0)
        d.text(x-56,245,"source %s"%lanes[a][0],10,MUTED,140);d.text(x-56,229,"target %s"%lanes[b][0],10,MUTED,140)
        if i in(1,2,4):d.text(x-66,286,"idle + bridges",10,GOLD,width=150)
    d.panel(42,73,1028,111,"EXACT BOUNDARY CONNECTIONS","After stage 1: X1 += X2; Y2 -= Y1. After stage 2: Y2 += Y1; X1 -= X2.\nAfter stage 4: Y1 -= Y2; X2 += X1. Final pairs (X1,Y1) and (X2,Y2) exchange as newX=oldY, newY=-oldX.\nIDLE projector widths: (46,46), (23,23), then (50,50,4,4). Each applies across all 1,760 ports.",TEAL)
    d.link(842,208,"F11 exact route projectors","B_F11",240)
    d.page("L04","Logical wiring | exact bank and replica map","Parametric expansion, not millions of drawn edges")
    d.panel(42,491,485,157,"INDEX DOMAIN","stage i in [0,5); replica r in [0,40); port t in [0,1760).\nResidual width a=24-dim(entrance(u)). Index j_a(u) is local to the sorted role family of width a, not the global helper census.\nOccurrence q=40*j_a(u)+r; symbolic cover class d.",BLUE)
    d.panel(554,491,524,157,"FULL ADDRESS","data family=(4*r+bank)*1760+t\nhelper family=281600+i*117089+stage_bank\nhelper route=d*tau_i*N^-1\nexternal work family=867045, route=(external_work,0)\nN=(block+1)*Pi*embed_i(B^-1)",TEAL)
    d.text(43,459,"E-BANK: choose the unique rank-a segment [lo,hi) containing q, with block-slot list S and stage-bank base beta.",11,INK)
    d.text(43,439,"k=floor((q-lo)/len(S)); b=S[(q-lo) mod len(S)]; stage_bank=beta+k; offset=sum(widths[0:b]); widths is this pattern.",11,TEAL)
    d.text(43,418,'Example pattern 17: five residual blocks of width 24, totaling 120 coordinates.',10,MUTED)
    x=43;y=337;unit=8.4
    for k,rank in enumerate([24,24,24,24,24]):
        d.c.setFillColor(HexColor(["#C4E2E9","#A8D2DA"][k%2]));d.c.rect(x,y,rank*unit,60,fill=1,stroke=0)
        d.text(x+20,y+22,"block %d: rank %d"%(k,rank),12,INK,width=rank*unit-22);x+=rank*unit
    d.panel(42,133,503,163,"RECONCILIATION","3,317,400 assignments = 5*40*16,587.\n200 complete stage/replica namespaces are injective in (family,route), even with 34,965 intentional same-family coincidences.\n770 frame-ID charts; 459 distinct entrance bases.",TEAL)
    d.panel(568,133,510,163,"COMPLETION DISCHARGE","Match all 2,827 tagged entrances and prove each full 240-column bank/work swap. Subtract only tagged counts.\nOrdinary children sharing widths 5,10,15,20,50 survive. map_boundary_row rejects COMPLETE opcode 6.",GOLD)
    d.link(43,86,"F12 assignment","B_F12",180);d.link(260,86,"F13 actual charts","B_F13",180);d.link(480,86,"F14 full addresses","B_F14",200)
    d.page("L05","Logical wiring | closed proof ports","What is expanded, parameterized, and still inherited")
    d.panel(42,456,322,186,"EXPANDED / EXACT","Local ADD/MOVE/COPY/ERASE ABI; seven interval templates; five active data-bank pairs; boundary shears/exchanges; exact stage/replica/helper address formulas.\nAll F01-F21 ports have source anchors.",TEAL)
    d.panel(389,456,332,186,"PARAMETRIC REPETITION","513 retained cohorts with exact candidate bases; 25 scalar-keyed retimings; 18 packing patterns; 40 replicas; 200 stage/replica namespaces; all symbolic cover classes.\nWitness IDs remain authoritative.",BLUE)
    d.panel(747,456,331,186,"UNEXPANDED INTERNALS","All-size weighted compiler, full GL-cover/common-ancestor charts, restored-row routing primitives, eligible-prime supply, recovery and complex symbolic/analytic theorems.\nThese are contracts, not gate-level drawings.",GOLD)
    d.text(44,412,"Required proof ports into F21",19,INK,bold=True)
    ports=[("raw","reconstructed source ledger"),("bit","physical / global / geometry"),("scalar","F2, chosen lift, source decoder"),("primes","actual determinant inventory"),("banks","full-address callable bank word"),("complex","pinned complex source and guard"),("math","two moments + bootstrap + outer47"),("finite","complete bill and full cutoff")]
    for i,(a,b) in enumerate(ports):
        x=45+(i%2)*526;y=342-(i//2)*60
        d.text(x,y,a,13,TEAL,bold=True);d.text(x+84,y,b,12,INK,width=418)
    d.text(44,71,"Coverage limit: these PDFs do not claim an individual-operation connection inventory. See connection_index.json for exact level and extraction status.",11,RED,width=1010)
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
    ("Coverage stated exactly","The current block catalog and connection index account for every declared input port. All 87 original hierarchy IDs are explicitly reconciled. Logical sheets give compact parametric wiring; the separate local event extractor provides value/frame versions and producer-consumer edges. The symbolic cover domain and inherited theorem internals remain unexpanded."),
    ("Evidence and pending checks","The recorded cloud admission freshly executed changed stages and reused byte/AST-bound unchanged signed-source and complex evidence. Mac standalone replay has now reported all eight stages passing with 143 unchanged source files. This explicit PR259 hybrid checkpoint remains mathematically conditional and is below the later PR266 frontier. Documentation checks are separate from scientific replay."),
    ("Public follow-up only","Construction checkpoint PR #277: https://github.com/CrocSwap/integer-mult-bounds/pull/277. Public source commit c2f07d311bfdad0d89bf961e4da133ee97bb78de is linked in README.md. Source anchors retain exact relative paths, symbols, line numbers and hashes. The historical combined_system_schematic_20261010 generator is preserved unchanged.")
    ]
    y=666
    for title,body in sections:
        y=d.text(43,y,title,15,TEAL,bold=True)-4;y=d.text(43,y,body,12,INK,1018)-21
    d.page("BUILD","Reproduce both diagram families","Pinned Python dependencies; no Graphviz requirement")
    y=672
    for title,body in [
    ("Install","Python 3.11+; python -m pip install -r joint259_system_docs_requirements.txt. Pinned reportlab 4.4.9, pypdf 6.10.0, Pillow 12.3.0, charset-normalizer 3.5.1. Graphviz is not used or required."),
    ("One build command","python -B joint259_system_docs_incremental.py --source /path/to/public-package --output joint259-docs-build --svg. An admitted source ZIP also works. Actual consumed manifest is recorded separately from the tested science archive in source_binding.json and QA.json."),
    ("Outputs","functional_architecture.pdf; logical_wiring.pdf; complete_system.pdf; connection_index.json; source_index.json; requirement_traceability.json; diagram_model.json; QA.json. Both families are regenerated from the same block/edge model and same pinned source."),
    ("Automatic reproducibility checks","Build every PDF twice in memory and require byte-identical SHA256, unchanged manifest, no missing/extra source files, valid proof anchors, all catalog block IDs present, all internal links resolved, nonempty extractable page text and no layout overflow. QA.json records counts, pins and output digests."),
    ("Independent visual check","Use Poppler: pdftoppm -png -r 100 complete_system.pdf review/page. Inspect every page for clipping, missing glyphs and readable connectors. Poppler is an optional renderer, not a generation dependency; record its actual version in visual QA."),
    ("Scientific verification remains separate","From a clean source package, use Python 3.11+ and SymPy 1.14.0 with assertions enabled: python -B verify.py --output /new/output/directory. Never write inside the immutable source package; never use -O. A successful documentation build is not an all-eight-stage science replay.")
    ]:
        y=d.text(43,y,title,15,TEAL,bold=True)-5;y=d.text(43,y,body,12,INK,1015)-25
def render(kind,model,refs):
    validate_model(model)
    d=Doc(kind,model,refs);cover(d)
    hierarchy_views.overview(d);hierarchy_views.transforms(d)
    if kind in("functional","combined"):fviews(d)
    if kind in("logical","combined"):lviews(d)
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
    for kind,name in [("functional","functional_architecture.pdf"),("logical","logical_wiring.pdf"),("combined","complete_system.pdf")]:
        one,report=render(kind,model,refs);two,_=render(kind,model,refs)
        if one!=two:raise ValueError("Nondeterministic "+kind)
        files[name]=one.decode("ascii");reports[name]=report
    index={"schema":"selected-construction-connections/1","source_manifest_sha256":model["source_manifest_sha256"],"level":"functional blocks with exact parametric wiring contracts","complete_individual_operation_inventory":False,"blocks":model["blocks"],"block_edges":model["edges"],"operation_schema":{"local_fields":["op","a","b","c","f","z"],"global_fields":["op","operand_a","operand_b","coefficient_or_frame","frame_or_rank","category_or_boundary","stage","complement"],"opcodes":{"MOVE":0,"ADD":1,"COPY":2,"ERASE":3,"IDLE":4,"BRIDGE":5,"COMPLETE":6,"EXCHANGE":7},"local_source_ids":[0,1759],"local_target_ids":[1760,3519],"local_helper_ids":[3520,20106],"local_work_id":20107},"parametric_domains":{"stages":5,"replicas":40,"ports":1760,"helper_roles":16587,"helper_assignments":3317400,"cover_classes":"symbolic finite GL cover; compiler theorem supplies enumeration"},"state_versions":{"native":False,"derived_ssa_extraction":"Separate JOINT259_CONNECTION_EXTRACT.py generates complete local value/frame producer-consumer inventory; this overview index is not that trace."},"unexpanded":["all-size weighted compiler internals","full GL-cover and common-ancestor charts","restored-row and routing primitive internals","prime-supply theorem","recovery theorem","complex symbolic and analytic theorems"],"coverage_limits":["E-series IDs are block dependencies, not scalar/COPY events.","Global numerical operation counts do not prove complete per-operation extraction.","Parametric address formulas are anchored to BankPlan; no fabricated gate-level internals."]}
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

