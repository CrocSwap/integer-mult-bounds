cd ../E6SLACK2
for n in B0 A0 B1 A1 B2; do s=$(date +%s); timeout 1200 kissat -q $n.cnf $n.drat > $n.kis 2>&1; echo "$n rc=$? $(grep -E '^s ' $n.kis) $(( $(date +%s)-s ))s" >> kissat.log; done
