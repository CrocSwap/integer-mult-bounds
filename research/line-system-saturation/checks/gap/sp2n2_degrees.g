# Smallest nontrivial ordinary character degrees of Sp(2n,2), n = 3,4,5, from the
# ATLAS character tables in the GAP Character Table Library (CTblLib).
# Run: gap -q -b sp2n2_degrees.g < /dev/null   (GAP >= 4.12 with package ctbllib)
OnBreak := function() Print("GAP_ERROR\n"); FORCE_QUIT_GAP(1); end;
if LoadPackage("ctbllib") <> true then Print("CTBLLIB_MISSING\n"); FORCE_QUIT_GAP(2); fi;
for pair in [["S6(2)",7],["S8(2)",35],["S10(2)",155]] do
  t := CharacterTable(pair[1]);
  degs := Set(List(Irr(t), chi -> chi[1]));
  m := Filtered(degs, d -> d > 1)[1];
  Print(pair[1], " order=", Size(t), " smallest_nontrivial_degree=", m,
        " expected=", pair[2], " ", (m = pair[2]), "\n");
  if m <> pair[2] then FORCE_QUIT_GAP(3); fi;
od;
Print("GAP_SP2N2_PASS\n");
QUIT;
