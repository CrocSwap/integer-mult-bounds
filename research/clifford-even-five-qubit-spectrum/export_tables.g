# Class convolution data. Output invariant under the ordering of irreducibles
# and classes, including the classes found from the explicit permutation group.
if LoadPackage("CTblLib", "= 1.3.11") <> true then Error("CTblLib 1.3.11 is required"); fi;
project := function(irr, counts, sizes, full)
  local d,k,coeff,polys,spectral,packets,columns,keys,mass,i,j,first;
  if not ForAll(counts,n->IsInt(n) and n>0 and 2^LogInt(n,2)=n) then Error("fixed counts");fi;
  d:=Log2Int(counts[1]); k:=List(counts,Log2Int);
  coeff:=List([0..d], j->List(k, x->0));
  for i in [1..Length(k)] do coeff[k[i]+1][i]:=sizes[i]; od;
  polys:=List(irr,r->coeff*r/r[1]);
  if not ForAll(Flat(polys),IsInt) or not ForAll(polys,p->p[d+1]=1) then Error("wrong class transform");fi;
  spectral:=Set(polys);
  if not full then return List(spectral,p->[p,Number(polys,x->x=p)]);fi;
  packets:=List(spectral, p->Sum(Filtered([1..Length(irr)],i->polys[i]=p),i->irr[i][1]*irr[i]));
  if not ForAll(Flat(packets),IsInt) then Error("nonintegral spectral packet");fi;
  columns:=List([1..Length(k)],i->Concatenation([k[i]],List(packets,r->r[i])));
  keys:=Set(columns);
  mass:=List(keys,col->Sum(sizes{Positions(columns,col)}));
  first:=List(spectral,p->Number(polys,y->p=y));
  return [spectral,first,List([1..Length(keys)],i->Concatenation([mass[i]],keys[i]))];
end;;
# Five-qubit tables and the stabilizer of a natural nonzero vector.
large := [];;
for name in ["S10(2)","O10+(2).2","O10-(2).2"] do
  tbl:=CharacterTable(name);; parent:=CharacterTable("S10(2)");;
  natural:=List(Irr(parent),ValuesOfClassFunction);;ds:=List(natural,r->r[1]);;
  fixed:=2+natural[Position(ds,495)]+natural[Position(ds,527)];;
  if name<>"S10(2)" then fixed:=fixed{GetFusionMap(tbl,parent)}; fi;
  Add(large,project(List(Irr(tbl),ValuesOfClassFunction),fixed,SizesConjugacyClasses(tbl),true));
od;
sp:=Sp(10,2);;nat:=Orbit(sp,One(GF(2))*[1,0,0,0,0,0,0,0,0,0]);;
perm:=Action(sp,nat,OnRight);;par:=Stabilizer(perm,1);;
classes:=ConjugacyClasses(par);;counts:=List(classes,c->1024-Length(MovedPoints(Representative(c))));;
sizes:=List(classes,Size);;irr:=List(Irr(CharacterTable(par)),ValuesOfClassFunction);;
Add(large,project(irr,counts,sizes,true));
small:=[];
for m in [1..4] do
  family:=[];
  if m=4 then
    parent:=CharacterTable("S8(2)");;
    natirr:=List(Irr(parent),ValuesOfClassFunction);;
    deg:=List(natirr,r->r[1]);;
    vecfix:=2+natirr[Position(deg,119)]+natirr[Position(deg,135)];;
    for name in ["S8(2)","O8+(2).2","O8-(2).2"] do
      tbl:=CharacterTable(name);; fixed:=vecfix;;
      if name<>"S8(2)" then fixed:=vecfix{GetFusionMap(tbl,parent)};fi;
      Add(family,project(List(Irr(tbl),ValuesOfClassFunction),fixed,SizesConjugacyClasses(tbl),false));
    od;
  else
    for matrixgroup in [Sp(2*m,2),GO(1,2*m,2),GO(-1,2*m,2)] do
      basis:=IdentityMat(2*m,GF(2));;
      points:=Filtered(AsList(VectorSpace(GF(2),basis)),v->not IsZero(v));
      perm:=Action(matrixgroup,points,OnRight);;
      cls:=ConjugacyClasses(perm);; fixed:=List(cls,c->2^(2*m)-Length(MovedPoints(Representative(c))));;
      Add(family,project(List(Irr(CharacterTable(perm)),ValuesOfClassFunction),fixed,List(cls,Size),false));
    od;
  fi;
  Add(small,family);
od;
Print([large,small],"\n");
QUIT;
