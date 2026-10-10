"""Full-system overview and reconciliation of all 87 prior stable block IDs."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parent
DATA=json.loads((BASE/"joint259_system_docs_hierarchy.json").read_text())
EDGES=json.loads((BASE/"joint259_system_docs_hierarchy_edges.json").read_text())
WHY={
"A0a":"Determine the exact input domain and operand lengths.",
"A0b":"Choose sizes and precision that satisfy every later interface.",
"A0c":"Make address, scale and phase choices explicit and reproducible.",
"A0d":"Route small cases to the attained ordinary leaf and retain finite guards.",
"A1":"Expose a convolution whose integer coefficients recover the product.",
"A2":"Keep transform inputs within the declared numerical envelope.",
"A3a":"Prevent cyclic wraparound from corrupting ordinary convolution.",
"A3b":"Preserve convolution while using the selected multidimensional layout.",
"A4a":"Move source samples into the working transform grid.",
"A4b":"Realize the source transform through the retained chirp reduction.",
"A4b1":"Represent the chirp convolution in the required negacyclic ring.",
"A4b2":"Evaluate the two normalized transforms used by ring convolution.",
"A4b3":"Form the ring convolution without hiding record-product work.",
"A4b4":"Return transformed products through the opposite normalization.",
"A4b5":"Remove the twist and restore the promised coefficient representation.",
"A4c":"Return from working-grid values to ordered source samples.",
"A4d":"Put both operand spectra in the same declared order.",
"A5":"Compute transform-domain convolution products at the chosen precision.",
"A6":"Recover a scaled convolution using the opposite transform sign.",
"A7a":"Undo the first transform normalization before exact recovery.",
"A7b":"Restore every remaining scale and the original coefficient layout.",
"A8":"Use the strict error bound to recover exact integer coefficients.",
"A9":"Propagate carries and serialize the exact integer product.",
"A4p1":"Generate phase exponents with their exact address/precision context.",
"A4p2":"Approximate phase factors within the allocated error budget.",
"A4p3":"Charge factor multiplication and truncation, rather than treating phases as free.",
"A4b2a":"Present stored records in the order required by each transform round.",
"A4b2b":"Realize the normalized local synthetic transform maps.",
"A4b2c":"Preserve the exact signed polynomial phase convention.",
"A4b2d":"Contain numerical growth and restore temporary work after each round.",
"A4b4a":"Reverse the transform orientation with its exact normalization.",
"A4c1":"Select the correct ordered source sample set.",
"A4c2":"Correct the bounded interpolation discrepancy.",
"A4c3":"Undo the diagonal Gaussian weighting with a paid factor.",
"A4io":"Make record shape and axis-order adapters explicit.",
"B0":"Keep F2 payload semantics separate from odd-prime address geometry.",
"B1":"Cancel arbitrary pre-existing dirty response before desired updates.",
"B2":"Produce the local helper action in exact admissible common frames.",
"B3":"Use a copied center without mutating its source or reading expired work.",
"B4":"Deliver only the specified target shear while preserving old target values.",
"B5":"Return all promised source and dirty payload states.",
"B6a":"Enter a source loan with a declared ownership and observation boundary.",
"B6b":"Prepare the source-carrier mix needed by the selected alias recipe.",
"B6c":"Consume the alias only inside its admitted lifetime and frames.",
"B6d":"Return the borrowed source before it is observed by its caller.",
"B6e":"Remove the carrier mix after its compensation obligations close.",
"B7a":"Prepare exact compensation for source-owned response.",
"B7b":"Transport the compensated target contribution to its legal observation cut.",
"B7c":"Cancel unwanted response without discarding the desired signal.",
"B8a":"Distinguish full routed addresses, not merely equal family numbers.",
"B8b":"Move complete streams with the exact route and finite charge.",
"B9a":"Invoke the exact smaller residual operator with restored-row obligations.",
"B9b":"Apply payload updates only at their common required frame.",
"B10":"Compose five routed orientations with legal phase-major boundaries.",
"B11":"Close arbitrary dirty residuals through the selected exact bank proof.",
"B12":"Restore the final external data-bank ordering by a paid exchange.",
"C1":"Cancel the old complex dirty response before the desired linear update.",
"C2":"Meet the exact phase-sensitive source entry labels.",
"C3":"Execute the first set of paid live-frame transitions.",
"C4":"Retain every copied-center child and scalar consumer.",
"C5":"Execute the second set of paid live-frame transitions.",
"C6":"Finish all live climbs before exit adaptation and cleanup.",
"C7":"Meet the exact complex exit labels, not a same-rank substitute.",
"C8":"Restore borrowed complex payload and clear the tableau.",
"C9":"Implement the literal forward center-copy scalar macro.",
"C10":"Implement the backward/transposed macro with fresh work.",
"C11a":"Create scalar work while preserving its source.",
"C11b":"Realize each exact rational coefficient on the declared common grid.",
"C11c":"Accumulate the signed scalar response at its correct destination.",
"C11d":"Clear temporary scalar work before reuse or recursion.",
"C12a":"Route each complex owner to its exact label and cover class.",
"C12b":"Compose all five complex windows, including idle banks.",
"C12c":"Finish the signed terminal exchange and restore external ownership.",
"C13":"Supply the residual with exact complex phases and normalization.",
"R1":"Package the complete residual operator and ownership obligations.",
"R2":"Call a genuinely smaller completed transform under the induction hypothesis.",
"R3":"Terminate at an attained ordinary algorithm below the finite cutoff.",
"R4":"Return every borrowed high row and spectator state.",
"R5a":"Retain both good-edge dispatch and the complete bad-edge fallback.",
"R5b":"Repair exceptional record layouts with paid primitives.",
"D0":"Bind every later check to a reconstructed source recipe.",
"D1":"Reject missing, changed or unpinned inputs.",
"D2":"Prove every formal bit column and its inverse restoration.",
"D3":"Check actual geometry, route order and determinant inventory.",
"D4":"Bind complex numerical checks to the pinned symbolic declarations.",
"D5":"Prevent a local cost improvement from bypassing complete closure.",
"D6":"Keep inherited all-size assumptions visible at the certificate boundary."
}
def card(d,x,y,w,h,key,title,body,target):
    d.panel(x,y,w,h,key+"  "+title,body,compact=True)
    d.link(x+15,y+12,"Drill down: "+target,"H_"+target if target[0]in"ABCRD" else "B_"+target,w-30,9)
    return (x,y,w,h)
def overview(d):
    d.page("H_SYSTEM","Functional hierarchy | integers to exact product","Runtime data path; supplier and theorem support are separate")
    d.text(42,666,"The selected hybrid replaces the BIT supplier inside this retained conditional integer-multiplication architecture.",13,"#526873")
    groups=[
    ("A0","Accept and configure","U,V,n -> admissible sizes, precision and descriptors\nA0a-A0d","A0a"),
    ("A1-A3","Represent operands","radix digits -> bounded arrays -> padded/CRT layout\nA1,A2,A3a,A3b","A1"),
    ("A4","Two source transforms","normalized source Fourier arrays, same retained order\nGaussian / chirp / resampling hierarchy","A4a"),
    ("A5-A6","Convolve and invert","matching Fourier products -> opposite-sign transform\nscaled convolution coefficients","A5"),
    ("A7-A8","Recover exactly","undo all scales/layout -> error below 1/2 -> integer coefficients","A7a"),
    ("A9","Normalize output","carry propagation and serialization -> exact UV","A9")]
    for i,(key,title,body,target) in enumerate(groups):
        col=i%3;row=i//3
        p=card(d,42+col*352,487-row*171,324,124,key,title,body,target)
        if col:d.arrow(last,p)
        last=p
    d.panel(42,95,323,159,"BIT SUPPLIER B0-B12","Current F02-F15 expand source527, kernels, intervals, frame paths, copied centers, 40-replica banks and exact completion. Historical source471 details are replaced, not silently retained.",compact=True)
    d.panel(394,95,323,159,"COMPLEX C1-C13","F16 expands the pinned complex supplier: labels, two scalar orientations, copied centers, live climbs, exact phases and finite guards. Its symbolic/analytic source theorem remains inherited.",compact=True)
    d.panel(746,95,332,159,"RECURSION / PROOF","R1-R5b state completed-child, row and fallback contracts. D0-D6 are evidence flow, not runtime payload. F17-F21 bind the selected literal cost and conditional outer closure.",compact=True)
    d.text(45,278,"Continuation: the output of A4 enters A5 on the next row. Each grouped ID opens its preserved detailed allocation.",10,"#526873")
def transforms(d):
    d.page("H_TRANSFORMS","Functional hierarchy | source-transform internals","Retained outer interfaces; not new executable helper gates")
    d.panel(42,492,320,156,"A4a  GAUSSIAN EXPANSION","CRTInputs -> WorkingTensor\nPaid descriptors and phase factors come from A4p1-A4p3; layout adapters are A4io.\nWhy: put source samples in the working grid.",compact=True)
    d.panel(390,492,334,156,"A4b  CHIRP TRANSFORM","A4b1 twist -> A4b2 two normalized transforms -> A4b3 ring products -> A4b4 opposite transform -> A4b5 untwist.\nWorkingTensor -> WorkingSpectrum.",compact=True)
    d.panel(752,492,326,156,"A4c / A4d  RESAMPLE","A4c1 sample selection -> A4c2 bounded Neumann correction -> A4c3 diagonal correction -> ordered SourceSpectrum / PairedSpectrum.",compact=True)
    d.arrow((42,492,320,156),(390,492,334,156));d.arrow((390,492,334,156),(752,492,326,156))
    d.panel(42,250,498,166,"A4b2 / A4b4  SYNTHETIC TRANSFORM","A4b2a tensor layout; A4b2b normalized butterfly rounds; A4b2c exact signed polynomial twiddle; A4b2d truncation and work cleanup. A4b4a supplies opposite rounds and normalization.\nTyped input/output: SyntheticState, with explicit numerical and ownership refinement.",compact=True)
    d.panel(567,250,511,166,"SUPPLIER CONNECTIONS","Bit supplier B supplies exact address movement, with F2 payload and rational address frames.\nComplex supplier C supplies phase-correct linear residuals.\nR supplies completed recursive returns and restored borrowed rows. Supplier proofs do not prove all outer internals.",compact=True)
    d.text(43,191,"Every original A/B/C/R/D ID appears below with its typed ports, why it exists, current allocation and exact scope.",13,"#147D77",bold=True)
    d.text(43,157,"Unexpanded all-size numerical routines and theorem primitives remain explicit contracts. No transistor/gate-level or all-size implementation completeness is claimed.",12,"#526873",width=1010)
def catalog(d):
    rows=DATA["blocks"]
    if len(rows)!=87 or len({z["id"]for z in rows})!=87 or set(WHY)!={z["id"]for z in rows}:raise ValueError("Historical block coverage mismatch")
    for start in range(0,len(rows),6):
        d.page("H_CATALOG" if start==0 else "H_CATALOG%d"%start,"Full hierarchy | blocks %d-%d of 87"%(start+1,min(start+6,87)),"Preserved stable IDs; current allocation and explicit implementation boundary")
        for j,z in enumerate(rows[start:start+6]):
            x=43+(j%2)*532;y=646-(j//2)*199
            d.bookmark("H_"+z["id"])
            y=d.text(x,y,z["id"]+"  "+z["name"],13,"#142D3A",492,True)-6
            y=d.text(x,y,"WHY: "+WHY[z["id"]],10,"#147D77",492,leading=13)-6
            ports="; ".join(k+": "+v for k,v in z["ports"].items())
            y=d.text(x,y,"PORTS: "+ports,9.5,"#142D3A",492,leading=12.5)-7
            y=d.text(x,y,z["note"],9.3,"#526873",492,leading=12)-7
            xx=x
            for bid in z["current_blocks"]:d.link(xx,y,bid,"B_"+bid,43,9.5);xx+=55
            d.text(xx,y,z["status"].replace("_"," "),8.4,"#526873",width=max(10,x+495-xx))
            y-=18
            for rid in z['historical_requirements']:
                d.link(x,y,rid,'H_REQ_'+rid,47,8.5);x+=52
            refs=list(z['source_refs'].items())
            preferred=[v for p,v in refs if '/sections/' in p]or[v for p,v in refs]
            url=preferred[0].get('primary_url') if preferred else None
            if url:
                label='Exact historical proof/source'
                d.text(x,y,label,8.5,'#176B8B',230)
                d.c.linkURL(url,(x,y-3,x+180,y+11),relative=0,thickness=0)

def requirements(d):
    rows=DATA['requirement_definitions']
    for start in range(0,len(rows),5):
        d.page('H_REQUIREMENTS' if start==0 else 'H_REQUIREMENTS%d'%start,'Original requirement vocabulary | %d-%d'%(start+1,min(start+5,len(rows))),'Retained outcome/model obligations; not source471 implementation mandates')
        y=671
        for row in rows[start:start+5]:
            d.bookmark('H_REQ_'+row['id'])
            y=d.text(43,y,row['id']+'  '+row['title'],14,'#147D77',1020,True)-4
            y=d.text(43,y,row['statement'],11,'#142D3A',1020)-6
            y=d.text(43,y,'Why: '+row['rationale'],10,'#526873',1020)-22

def connections(d):
    rows=[z for z in EDGES['relations']if z['inventory']=='typed_edges']
    if len(rows)!=53 or len(EDGES['relations'])!=128:raise ValueError('Historical edge reconciliation incomplete')
    ids={z['id']for z in DATA['blocks']}
    if any(e['source_block']not in ids or e['target_block']not in ids for e in EDGES['relations']):raise ValueError('Unknown historical endpoint')
    for start in range(0,len(rows),10):
        d.page('H_CONNECTIONS'if start==0 else'H_CONNECTIONS%d'%start,'Preserved interface connections | %d-%d of 53'%(start+1,min(start+10,53)),'Original typed relations reconciled; not promoted to current scalar execution')
        y=671
        for r in rows[start:start+10]:
            e=r['original'];d.bookmark(r['id'])
            d.text(43,y,r['id'],10,'#147D77',70,True)
            d.link(110,y,e['source'],'H_'+r['source_block'],194,10)
            d.text(305,y,'->',10,'#142D3A',30)
            d.link(334,y,e['target'],'H_'+r['target_block'],194,10)
            d.text(543,y,e['kind']+' / '+e.get('type','contract'),9.5,'#142D3A',500)
            d.text(110,y-17,r['selected_status'].replace('_',' '),9,'#526873',850)
            y-=49
        d.text(43,91,'Also preserved: 75 documentary relations with separate classification in hierarchy_edges.json. Neither inventory is silently relabeled as current gate order.',10,'#526873',1020)
        d.text(43,68,'Current F01-F21 dependencies and the exact selected local event inventory are separate, source-bound layers.',10,'#526873',1020)

