# Convolution on ordinary rational conjugacy classes using native GAP and CTblLib.
# This alternative starts from the two actions on quadratic refinements, builds
# the integral multiplication matrix for the complete central kernel, and solves
# a 192-dimensional rational system. The sole expected denominator is checked
# only after the solve. apoursh with substantial OpenAI Codex assistance. Apache-2.0.
if LoadPackage("CTblLib", "= 1.3.11") <> true then
  Error("Install GAP CTblLib 1.3.11");
fi;
g := CharacterTable("S10(2)");;
chars := List(Irr(g), ValuesOfClassFunction);;
nc := NrConjugacyClasses(g);;
ord := Size(g);;
# For any symplectic s, the difference q(sv)-q(v) of a refinement is linear
# and vanishes on ker(s-I). It is therefore a coboundary of a linear form.
# Fixed quadratic refinements exist, and their number is |ker(s-I)|. Count
# these by the two stabilizer fusions, without using the 495/527 constituents.
fixed := List([1..nc], i -> 0);;
for name in ["O10+(2).2", "O10-(2).2"] do
  sub := CharacterTable(name);
  fusion := GetFusionMap(sub,g);
  for j in [1..Length(fusion)] do
    i := fusion[j];
    fixed[i] := fixed[i] + SizesCentralizers(g)[i]/SizesCentralizers(sub)[j];
  od;
od;
rows := RationalizedMat(chars);;
if Length(rows) <> 192 or not ForAll(Flat(rows), IsInt) then Error("Packet sums"); fi;
cols := TransposedMat(rows);;
classes := [];;
for col in Set(cols) do Add(classes,Filtered([1..nc], i->cols[i]=col)); od;
SortBy(classes, a->a[1]);;
positions := List(classes, c->c[1]);;
if Length(classes) <> 192 or not ForAll(classes,c->Length(Set(fixed{c}))=1) then Error("Rational classes"); fi;
# The scalar of each rational class sum on each absolute constituent of a packet.
sizes := List(classes,c->Sum(SizesConjugacyClasses(g){c}));;
evals := List(rows,r->List([1..Length(classes)],j->sizes[j]*r[positions[j]]/r[1]));;
if not ForAll(Flat(evals), IsInt) then Error("Class-evaluation integral basis"); fi;
# Projecting the regular characters back to class sums inverts this transform.
inverseNumerator := List([1..Length(rows)], j -> List(rows, r ->
    r[positions[j]] * (ord / Sum([1..nc],i->SizesConjugacyClasses(g)[i]*r[i]*r[i])) * r[1]));;
if not ForAll(Flat(inverseNumerator), IsInt) then Error("Inverse Fourier numerator"); fi;
# If r is the sum of a rational packet of m ordinary characters of degree d,
# its squared scalar product is m, and d=r(1)/m. Orthogonality gives the
# inverse transform at a class i as d*r(i)/|G| (r is rational and real).
if inverseNumerator * evals <> ord * IdentityMat(Length(rows)) then
  Error("Character transform and inverse disagree");
fi;
# The sign is positive at width 15. In the rational class-sum basis the
# coefficient on each conjugacy class is |ker(s-I)|^7.
f := List(positions,i -> fixed[i]^7);;
scalars := evals * f;;
if not ForAll(scalars, n -> IsPosInt(n)) then Error("Nonpositive shell frequency"); fi;
op := (inverseNumerator * List([1..Length(rows)], i -> scalars[i] * evals[i])) / ord;;
if not ForAll(Flat(op), n->IsInt(n) and n>=0) or op{[1..Length(rows)]}{[1]} <> List(f,x->[x]) then
  Error("Convolution by the positive integral class function");
fi;
target := Concatenation([1], List([2..Length(rows)], i->0));;
h := SolutionMat(TransposedMat(op), target);;
if h=fail or op*h <> target then Error("Convolution identity"); fi;
den := Lcm(List(h,DenominatorRat));;
while den mod 2 = 0 do den:=den/2; od;
if den <> 3893475211724344589772283104450359211356271788394430137298138320180684819953076729962451809990220934288705085671875 then Error("Unexpected odd denominator"); fi;
Print("PASS convolution solve: ",Length(classes)," rational classes, odd denominator ",den,"\n");
QUIT;
