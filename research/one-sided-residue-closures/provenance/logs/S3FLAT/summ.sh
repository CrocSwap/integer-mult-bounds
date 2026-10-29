#!/bin/bash
# summ.sh tag : aggregate OVERALL lines
grep -h OVERALL out_$1_*.out | awk '{for(i=1;i<=NF;i++){ if($i=="pairs")p+=$(i+1); if($i=="surviving")s+=$(i+1); if($i=="leaves")l+=$(i+1); if($i=="overflow")o+=$(i+1); if($i=="span"){ if($(i+1)>m)m=$(i+1)} } n++} END{print "chunks",n,"pairs",p,"survpairs",s,"leaves",l,"overflow",o,"MAXSPAN",m}'
grep -h "^rep" out_$1_*.out | wc -l
grep -h CRACK out_$1_*.out | wc -l
