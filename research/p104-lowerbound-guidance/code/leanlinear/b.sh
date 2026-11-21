#!/bin/bash
# usage: b.sh File.lean [olean]  -- runs shared runlean.sh, saves own full log to logs/<name>.log
cd <research-tree>/cards/WILD/LEANCERT
name=$(basename "$1" .lean)
./runlean.sh "$@" > <tmpdir> 2>&1 &
pid=$!
wait $pid
L=code/leanlinear/logs/$name.log
{ head -5 <tmpdir> grep -v "push_neg\|^If you'd\|^\`\`\`\|^open Lean\|^macro\|^  \`(tactic" <tmpdir> } > $L
echo finished $name >> $L
