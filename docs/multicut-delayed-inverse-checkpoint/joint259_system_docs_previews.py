"""Compact PR previews, readable as two separate images at GitHub width."""
from html import escape
def preview(model,logical=False):
    bg="#F7FAFB";ink="#142D3A";blue="#176B8B";teal="#147D77";muted="#526873"
    title="Logical wiring: indexed, source-bound connections"if logical else"Functional architecture: exact product with two suppliers"
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="570" viewBox="0 0 1200 570"><rect width="1200" height="570" fill="{bg}"/>',
    '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#147D77"/></marker></defs>',
    '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#142D3A} .title{font-size:28px;font-weight:700}.label{font-size:20px;font-weight:700}.body{font-size:17px}.note{font-size:16px;fill:#526873}</style>',
    f'<text class="title" x="34" y="48">{escape(title)}</text>',
    '<text class="note" x="34" y="78">Verified PR259 hybrid checkpoint | conditional kappa 0.000711045547624400</text>']
    def box(x,y,w,h,title,lines,color=blue):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="white" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<text class="label" x="{x+17}" y="{y+32}">{escape(title)}</text>')
        for i,line in enumerate(lines):parts.append(f'<text class="body" x="{x+17}" y="{y+63+i*25}">{escape(line)}</text>')
    def arrow(x1,y1,x2,y2,dashed=False):
        parts.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{teal}" stroke-width="3"'+(' stroke-dasharray="7 6"'if dashed else'')+' marker-end="url(#arrow)"/>')
    if logical:
        box(34,119,250,134,"Typed operand bus",["U,V -> digits -> tensors","operand a in [0,2)","digit index j in [0,N)"])
        box(329,119,250,134,"Transforms",["source spectra[a,k]","k in declared R order","bit + complex calls"])
        box(624,119,250,134,"Product / inverse",["match equal index k","opposite transform","restore scale/layout"])
        box(919,119,247,134,"Exact result",["error < 1/2","integer coefficients","carry -> product UV"])
        for a,b in[(284,329),(579,624),(874,919)]:arrow(a,186,b,186)
        box(34,313,350,145,"Local event template",["OP[e]: src/dst + frame","value/frame versions + uses","859,771 exact local records"],teal)
        box(426,313,350,145,"Indexed physical map",["stage s in [0,5)","replica r in [0,40)","address = (family, route)"],teal)
        box(818,313,348,145,"Closed proof ports",["all 8 scientific stages","COPY lifetime + bank checks","unexpanded theorem boundary"],teal)
        arrow(384,384,426,384);arrow(776,384,818,384)
        parts.append('<text class="note" x="34" y="505">Compact parametric specification, not a flattened million-wire circuit. Exact formulas and exceptions are in the full PDF.</text>')
    else:
        box(34,119,250,134,"Represent operands",["read U,V and sizes","radix / scale / pad","A0-A3"])
        box(329,119,250,134,"Transform stages",["two source transforms","matching products","A4-A6"])
        box(624,119,250,134,"Exact recovery",["undo scales/layout","bounded error -> round","A7-A8"])
        box(919,119,247,134,"Emit exact product",["carry propagation","serialize UV","A9"])
        for a,b in[(284,329),(579,624),(874,919)]:arrow(a,186,b,186)
        box(34,313,350,145,"Selected bit supplier",["513 cohorts + 7 intervals","25 final retimings, once","literal 40-replica banks"],teal)
        box(426,313,350,145,"Pinned complex supplier",["exact labels and phases","copied centers / live climbs","finite precision and rows"],teal)
        box(818,313,348,145,"Recursion and evidence",["all 87 original roles mapped","complete finite price","inherited assumptions explicit"],teal)
        arrow(210,313,410,253,True);arrow(600,313,490,253,True)
        parts.append('<text class="note" x="34" y="505">Solid arrows: runtime data interfaces. Dashed arrows: supplier support. This is a conditional mathematical construction.</text>')
    parts.append('<text class="note" x="34" y="541">Source snapshot: 9f6d8637...  |  Readable overview; full explanations, typed ports, requirements and proofs are linked below.</text></svg>')
    svg="\n".join(parts)+"\n"
    styles={"title":'font-size="28" font-weight="700"',"label":'font-size="20" font-weight="700"',"body":'font-size="17"',"note":'font-size="16" fill="#526873"'}
    for cls,attributes in styles.items():
        svg=svg.replace('class="'+cls+'"','font-family="DejaVu Sans" '+attributes)
    return svg
def files(model):return {"summary-functional.svg":preview(model),"summary-logical.svg":preview(model,True)}

