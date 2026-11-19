# Export integer data from the published ATLAS ordinary table.
if LoadPackage("CTblLib", "= 1.3.11") <> true then
  Error("CTblLib 1.3.11 is required");
fi;
t := CharacterTable("S10(2)");;
irr := List(Irr(t), ValuesOfClassFunction);;
positions := [1..Length(irr)];;
families := GaloisMat(irr).galoisfams;;
orbits := [];;
for i in positions do
  if families[i] = 1 then
    Add(orbits, [i]);
  elif IsList(families[i]) then
    Add(orbits, families[i][1]);
  fi;
od;
rows := List(orbits, orbit -> Sum(irr{orbit}));;
columns := TransposedMat(rows);;
groups := [];;
for i in positions do
  if Position(columns, columns[i]) = i then
    Add(groups, Positions(columns, columns[i]));
  fi;
od;
reps := List(groups, g -> g[1]);;
degrees := List(irr, r -> r[1]);;
natural := 2 + irr[Position(degrees,495)] + irr[Position(degrees,527)];;
classes := List(groups, g -> [g, SizesConjugacyClasses(t)[g[1]], LogInt(natural[g[1]],2)]);;
packets := List([1..Length(rows)], i -> [orbits[i], rows[i]{reps}]);;
if not ForAll(Flat(packets),IsInt) or ClassNames(t)[7]<>"2f" then Error("table convention"); fi;
Print([Size(t), classes, packets, List(irr, r->r[7])],"\n");
QUIT;
