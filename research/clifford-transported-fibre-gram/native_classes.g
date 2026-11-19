# Recompute Sp(8,2) class data from the natural permutation group in GAP 4.14.
# Redirect standard output to a file and pass that file to build_classes.py.
g := Sp(8,2);;
form := InvariantBilinearForm(g).matrix;;
if not ForAll([1..8], i -> ForAll([1..8], j ->
    (not IsZero(form[i][j])) = (i+j=9))) then Error("Unexpected natural pairing"); fi;
space := GF(2)^8;;
vectors := Difference(AsList(space), [Zero(space)]);;
action := ActionHomomorphism(g, vectors, OnRight, "surjective");;
h := Image(action);;
classes := ConjugacyClasses(h);;
tbl := CharacterTable(h);;
chars := List(Irr(tbl),ValuesOfClassFunction);;
if Size(h) <> 47377612800 or Length(classes) <> 81 or
   List(classes,Size) <> SizesConjugacyClasses(tbl) then Error("Class order"); fi;
labels := List(vectors, v -> Sum([1..8], i->IntFFE(v[i])*2^(i-1)));;
reps := List(classes, c -> List([0..7], i -> labels[Position(labels,2^i)^Representative(c)]));;
Print([reps,List(classes,Size),RationalizedMat(chars)],"\n");
QUIT;
