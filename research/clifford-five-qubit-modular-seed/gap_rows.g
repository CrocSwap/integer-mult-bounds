# Independent check with GAP 4.14.0 and CTblLib 1.3.11.
if LoadPackage("CTblLib", "= 1.3.11") <> true then
  Error("Install the pinned CTblLib 1.3.11 release");
fi;
OutputBrauerTriples := function(name, p, ordcols)
  local t, b, fusion, cols;
  t := CharacterTable(name);
  b := t mod p;
  fusion := GetFusionMap(b, t);
  cols := List(ordcols, i -> Position(fusion, i));
  if fail in cols then Error("Seed class is not p-regular"); fi;
  return List(Irr(b), chi -> chi{cols});
end;
result := List([5,7,11,17,31], p -> OutputBrauerTriples("S10(2)", p, [1,3,6]));;
Add(result, OutputBrauerTriples("O10+(2)", 3, [1,2,4]));
Add(result, OutputBrauerTriples("O10-(2)", 3, [1,2,4]));
Print(result, "\n");
QUIT;
