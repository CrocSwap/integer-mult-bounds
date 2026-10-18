"""Optional nomination only. Requires an existing NetworkX installation."""
from pathlib import Path
import argparse,json,sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import verify
def main():
    import networkx as nx
    parser=argparse.ArgumentParser();parser.add_argument('--write-witness',action='store_true');args=parser.parse_args()
    word,old,recipe,lower=verify.inputs();targets,helpers,C,D=verify.matrix(word,recipe);table,_=verify.census(D)
    graphs=[nx.Graph(),nx.Graph()]
    for i,j,ident,bf,sc,desc in table.values():
        for graph,cost,kind in ((graphs[0],sc,desc),(graphs[1],min(bf,sc),'butterfly' if bf<sc else desc)):
            if ident>cost:graph.add_edge(i,j,weight=ident-cost,cost=cost,kind=kind)
    matchings=[]
    for graph in graphs:
        pairs=sorted([sorted(e) for e in nx.max_weight_matching(graph)])
        entries=[{'pair':p,**graph.edges[tuple(p)]} for p in pairs];gain=sum(x['weight'] for x in entries)
        matchings.append({'pairs':entries,'gain':gain,'panel':sum(verify.price(x) for row in D for x in row)+4*len(recipe['target_forest'])-gain})
    witness={'base_commit':verify.BASE,'seed':38,'shear_matching':matchings[0],'butterfly_matching':matchings[1]}
    if args.write_witness:(HERE/'WITNESS.json').write_text(json.dumps(witness,indent=2)+'\n',encoding='utf8')
    print('NOMINATED',[(x['panel'],len(x['pairs'])) for x in matchings],'NetworkX',nx.__version__)
if __name__=='__main__':main()
