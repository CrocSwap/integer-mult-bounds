"""Re-pack Child 15 Replica 6 non-full ports via optimal CP-SAT (Breakthrough 9).

Solves optimal integer linear assignment across 25 ports (15 non-full ports + 10 donor full ports)
in Child 15 Replica 6, strictly minimizing the concave complex moment M(z).

Net profile transition:
  rem 24 (-1) -> 0 (extinguished)
  rem 2: 9 -> 3 (-6)
  rem 0: +2 net full ports
  rem 11: 0 -> 1 (+1)
  rem 1: 2192 -> 2196 (+4)

Deficit is strictly conserved: global deficit remains 5120; global rank mass remains 1041408.
All call-disjointness, window bounds, frame chart constraints, and contiguous prefix rules
are strictly satisfied.

Increases conditional integer-multiplication kappa from 0.001672781312867556
to 0.001672789077668839 (+7.7648013e-9 gain over Breakthrough 8 commit 3fb72a73,
+9.7388517e-8 over PR #1104).

Prepared with autonomous research assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path

TARGET_SHA = "643cf03f95640b81925799e83f6f76ac48203669c7a85422ef07d76ad1ae2a70"

CHANGES = {
  "(5, 5, 265)": {
    "port": 106,
    "copy": 778,
    "family": 5818
  },
  "(5, 5, 273)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 0
  },
  "(5, 5, 411)": {
    "port": 101,
    "copy": 773,
    "family": 5813,
    "offset": 7
  },
  "(6, 12, 20)": {
    "port": 93,
    "copy": 765,
    "family": 5805,
    "offset": 9
  },
  "(6, 12, 53)": {
    "port": 102,
    "copy": 774,
    "family": 5814,
    "offset": 12
  },
  "(6, 12, 58)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 16
  },
  "(6, 12, 65)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 16
  },
  "(6, 12, 67)": {
    "port": 98,
    "copy": 770,
    "family": 5810,
    "offset": 13
  },
  "(7, 3, 274)": {
    "port": 102,
    "copy": 774,
    "family": 5814,
    "offset": 16
  },
  "(7, 11, 115)": {
    "port": 102,
    "copy": 774,
    "family": 5814,
    "offset": 24
  },
  "(7, 11, 117)": {
    "port": 95,
    "copy": 767,
    "family": 5807,
    "offset": 15
  },
  "(7, 11, 122)": {
    "port": 98,
    "copy": 770,
    "family": 5810,
    "offset": 17
  },
  "(7, 11, 224)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 12
  },
  "(7, 11, 225)": {
    "port": 110,
    "copy": 782,
    "family": 5822,
    "offset": 25
  },
  "(8, 2, 422)": {
    "offset": 18
  },
  "(8, 2, 423)": {
    "offset": 18
  },
  "(8, 2, 435)": {
    "offset": 18
  },
  "(8, 2, 437)": {
    "offset": 18
  },
  "(8, 2, 438)": {
    "offset": 18
  },
  "(8, 2, 439)": {
    "offset": 18
  },
  "(8, 2, 443)": {
    "offset": 18
  },
  "(8, 2, 445)": {
    "offset": 18
  },
  "(8, 2, 446)": {
    "offset": 18
  },
  "(8, 2, 447)": {
    "offset": 18
  },
  "(8, 10, 224)": {
    "port": 98,
    "copy": 770,
    "family": 5810,
    "offset": 25
  },
  "(8, 10, 225)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 25
  },
  "(8, 10, 371)": {
    "offset": 27
  },
  "(8, 10, 373)": {
    "offset": 27
  },
  "(8, 10, 374)": {
    "offset": 27
  },
  "(8, 10, 375)": {
    "offset": 27
  },
  "(8, 10, 419)": {
    "offset": 27
  },
  "(8, 10, 421)": {
    "offset": 27
  },
  "(8, 10, 422)": {
    "offset": 27
  },
  "(8, 10, 423)": {
    "offset": 27
  },
  "(8, 10, 435)": {
    "offset": 27
  },
  "(8, 10, 437)": {
    "offset": 27
  },
  "(8, 10, 438)": {
    "offset": 27
  },
  "(8, 10, 439)": {
    "offset": 27
  },
  "(8, 10, 443)": {
    "offset": 27
  },
  "(8, 10, 445)": {
    "offset": 27
  },
  "(8, 10, 446)": {
    "offset": 27
  },
  "(8, 10, 447)": {
    "offset": 27
  },
  "(8, 10, 451)": {
    "offset": 27
  },
  "(8, 10, 453)": {
    "offset": 27
  },
  "(8, 10, 454)": {
    "offset": 27
  },
  "(8, 10, 455)": {
    "offset": 27
  },
  "(8, 10, 459)": {
    "offset": 27
  },
  "(8, 10, 461)": {
    "offset": 27
  },
  "(8, 10, 462)": {
    "offset": 27
  },
  "(8, 10, 463)": {
    "offset": 27
  },
  "(8, 10, 467)": {
    "offset": 27
  },
  "(8, 10, 469)": {
    "offset": 27
  },
  "(8, 10, 470)": {
    "offset": 27
  },
  "(8, 10, 471)": {
    "offset": 27
  },
  "(8, 10, 475)": {
    "offset": 27
  },
  "(8, 10, 477)": {
    "offset": 27
  },
  "(8, 10, 478)": {
    "offset": 27
  },
  "(8, 10, 479)": {
    "offset": 27
  },
  "(4, 7, 224)": {
    "port": 95,
    "copy": 767,
    "family": 5807
  },
  "(4, 7, 263)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 0
  },
  "(4, 7, 264)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 0
  },
  "(4, 15, 122)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 8
  },
  "(4, 15, 161)": {
    "port": 102,
    "copy": 774,
    "family": 5814,
    "offset": 0
  },
  "(4, 15, 165)": {
    "port": 110,
    "copy": 782,
    "family": 5822,
    "offset": 0
  },
  "(4, 15, 224)": {
    "port": 101,
    "copy": 773,
    "family": 5813
  },
  "(4, 15, 263)": {
    "port": 87,
    "copy": 759,
    "family": 5799,
    "offset": 0
  },
  "(4, 15, 279)": {
    "port": 88,
    "copy": 760,
    "family": 5800,
    "offset": 0
  },
  "(5, 14, 295)": {
    "port": 110,
    "copy": 782,
    "family": 5822,
    "offset": 4
  },
  "(6, 5, 170)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 12
  },
  "(6, 5, 379)": {
    "port": 110,
    "copy": 782,
    "family": 5822,
    "offset": 17
  },
  "(6, 5, 381)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 12
  },
  "(6, 5, 382)": {
    "port": 87,
    "copy": 759,
    "family": 5799
  },
  "(6, 5, 383)": {
    "port": 99,
    "copy": 771,
    "family": 5811
  },
  "(6, 5, 387)": {
    "port": 95,
    "copy": 767,
    "family": 5807,
    "offset": 11
  },
  "(6, 5, 389)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 4
  },
  "(6, 5, 390)": {
    "port": 105,
    "copy": 777,
    "family": 5817
  },
  "(6, 5, 395)": {
    "port": 102,
    "copy": 774,
    "family": 5814
  },
  "(8, 11, 250)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 24
  },
  "(5, 15, 85)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 8
  },
  "(5, 15, 90)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 0
  },
  "(5, 15, 97)": {
    "port": 95,
    "copy": 767,
    "family": 5807,
    "offset": 7
  },
  "(5, 15, 99)": {
    "port": 87,
    "copy": 759,
    "family": 5799,
    "offset": 8
  },
  "(5, 15, 101)": {
    "port": 104,
    "copy": 776,
    "family": 5816,
    "offset": 0
  },
  "(5, 15, 106)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 12
  },
  "(5, 15, 113)": {
    "port": 102,
    "copy": 774,
    "family": 5814,
    "offset": 4
  },
  "(5, 15, 115)": {
    "port": 94,
    "copy": 766,
    "family": 5806,
    "offset": 0
  },
  "(5, 15, 117)": {
    "port": 101,
    "copy": 773,
    "family": 5813,
    "offset": 11
  },
  "(5, 15, 122)": {
    "port": 97,
    "copy": 769,
    "family": 5809
  },
  "(5, 15, 129)": {
    "port": 89,
    "copy": 761,
    "family": 5801,
    "offset": 0
  },
  "(5, 15, 133)": {
    "port": 98,
    "copy": 770,
    "family": 5810
  },
  "(5, 15, 145)": {
    "port": 100,
    "copy": 772,
    "family": 5812
  },
  "(5, 15, 147)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 0
  },
  "(5, 15, 149)": {
    "port": 110,
    "copy": 782,
    "family": 5822,
    "offset": 13
  },
  "(5, 15, 154)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 0
  },
  "(5, 15, 161)": {
    "port": 103,
    "copy": 775,
    "family": 5815,
    "offset": 0
  },
  "(5, 15, 163)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 8
  },
  "(5, 15, 165)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 8
  },
  "(5, 15, 170)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 0
  },
  "(6, 6, 33)": {
    "port": 97,
    "copy": 769,
    "family": 5809
  },
  "(6, 6, 34)": {
    "port": 93,
    "copy": 765,
    "family": 5805,
    "offset": 0
  },
  "(6, 6, 35)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 8
  },
  "(6, 6, 36)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 4
  },
  "(6, 6, 37)": {
    "port": 103,
    "copy": 775,
    "family": 5815,
    "offset": 4
  },
  "(6, 6, 38)": {
    "port": 88,
    "copy": 760,
    "family": 5800,
    "offset": 9
  },
  "(6, 6, 39)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 4
  },
  "(6, 6, 40)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 12
  },
  "(6, 6, 41)": {
    "port": 98,
    "copy": 770,
    "family": 5810
  },
  "(6, 6, 99)": {
    "port": 87,
    "copy": 759,
    "family": 5799
  },
  "(6, 14, 395)": {
    "port": 111,
    "copy": 783,
    "family": 5823
  },
  "(6, 14, 397)": {
    "port": 110,
    "copy": 782,
    "family": 5822,
    "offset": 21
  },
  "(6, 14, 398)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 20
  },
  "(6, 14, 403)": {
    "port": 87,
    "copy": 759,
    "family": 5799,
    "offset": 20
  },
  "(6, 14, 405)": {
    "port": 101,
    "copy": 773,
    "family": 5813,
    "offset": 15
  },
  "(6, 14, 406)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 8
  },
  "(6, 14, 407)": {
    "port": 104,
    "copy": 776,
    "family": 5816,
    "offset": 4
  },
  "(7, 13, 43)": {
    "port": 104,
    "copy": 776,
    "family": 5816,
    "offset": 8
  },
  "(7, 13, 44)": {
    "port": 100,
    "copy": 772,
    "family": 5812,
    "offset": 8
  },
  "(7, 13, 45)": {
    "port": 103,
    "copy": 775,
    "family": 5815,
    "offset": 13
  },
  "(7, 13, 46)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 13
  },
  "(7, 13, 47)": {
    "port": 88,
    "copy": 760,
    "family": 5800,
    "offset": 18
  },
  "(7, 13, 61)": {
    "offset": 5
  },
  "(7, 13, 62)": {
    "offset": 5
  },
  "(7, 13, 63)": {
    "offset": 5
  },
  "(7, 13, 64)": {
    "offset": 5
  },
  "(7, 13, 66)": {
    "offset": 5
  },
  "(7, 13, 67)": {
    "port": 106,
    "copy": 778,
    "family": 5818
  },
  "(7, 13, 68)": {
    "offset": 5
  },
  "(7, 13, 70)": {
    "offset": 5
  },
  "(7, 13, 71)": {
    "offset": 5
  },
  "(7, 13, 72)": {
    "offset": 5
  },
  "(7, 13, 73)": {
    "offset": 5
  },
  "(7, 13, 75)": {
    "offset": 5
  },
  "(7, 13, 76)": {
    "offset": 5
  },
  "(7, 13, 77)": {
    "offset": 5
  },
  "(7, 13, 78)": {
    "offset": 5
  },
  "(7, 13, 98)": {
    "offset": 0
  },
  "(7, 13, 100)": {
    "offset": 0
  },
  "(7, 13, 102)": {
    "offset": 0
  },
  "(7, 13, 104)": {
    "offset": 0
  },
  "(7, 13, 105)": {
    "offset": 0
  },
  "(7, 13, 107)": {
    "offset": 0
  },
  "(7, 13, 108)": {
    "offset": 0
  },
  "(7, 13, 109)": {
    "offset": 0
  },
  "(7, 13, 110)": {
    "offset": 0
  },
  "(7, 13, 111)": {
    "offset": 0
  },
  "(7, 13, 112)": {
    "offset": 0
  },
  "(7, 13, 114)": {
    "offset": 0
  },
  "(7, 13, 116)": {
    "offset": 0
  },
  "(7, 13, 118)": {
    "offset": 0
  },
  "(7, 13, 119)": {
    "offset": 0
  },
  "(7, 13, 120)": {
    "offset": 0
  },
  "(7, 13, 121)": {
    "offset": 0
  },
  "(7, 13, 123)": {
    "offset": 0
  },
  "(7, 13, 124)": {
    "offset": 0
  },
  "(7, 13, 125)": {
    "offset": 0
  },
  "(7, 13, 126)": {
    "offset": 0
  },
  "(7, 13, 127)": {
    "offset": 0
  },
  "(7, 13, 128)": {
    "offset": 0
  },
  "(7, 13, 130)": {
    "offset": 0
  },
  "(7, 13, 132)": {
    "offset": 0
  },
  "(7, 13, 134)": {
    "offset": 0
  },
  "(7, 13, 135)": {
    "offset": 0
  },
  "(7, 13, 136)": {
    "offset": 0
  },
  "(7, 13, 137)": {
    "offset": 0
  },
  "(7, 13, 139)": {
    "offset": 0
  },
  "(7, 13, 140)": {
    "offset": 0
  },
  "(7, 13, 141)": {
    "offset": 0
  },
  "(7, 13, 142)": {
    "offset": 0
  },
  "(7, 13, 143)": {
    "offset": 0
  },
  "(7, 13, 144)": {
    "offset": 0
  },
  "(7, 13, 146)": {
    "offset": 0
  },
  "(7, 13, 148)": {
    "offset": 0
  },
  "(7, 13, 150)": {
    "offset": 0
  },
  "(7, 13, 151)": {
    "offset": 0
  },
  "(7, 13, 152)": {
    "offset": 0
  },
  "(7, 13, 153)": {
    "offset": 0
  },
  "(7, 13, 155)": {
    "offset": 0
  },
  "(8, 12, 459)": {
    "offset": 27
  },
  "(8, 12, 461)": {
    "offset": 27
  },
  "(8, 12, 462)": {
    "offset": 27
  },
  "(8, 12, 463)": {
    "offset": 27
  },
  "(8, 12, 467)": {
    "offset": 27
  },
  "(8, 12, 469)": {
    "offset": 27
  },
  "(8, 12, 470)": {
    "offset": 27
  },
  "(8, 12, 471)": {
    "offset": 27
  },
  "(8, 12, 475)": {
    "offset": 27
  },
  "(8, 12, 477)": {
    "offset": 27
  },
  "(8, 12, 478)": {
    "offset": 27
  },
  "(8, 12, 479)": {
    "offset": 27
  },
  "(6, 7, 64)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 17
  },
  "(6, 7, 454)": {
    "offset": 0
  },
  "(6, 7, 455)": {
    "offset": 0
  },
  "(6, 7, 459)": {
    "offset": 0
  },
  "(6, 7, 461)": {
    "offset": 0
  },
  "(6, 7, 462)": {
    "offset": 0
  },
  "(6, 7, 463)": {
    "offset": 0
  },
  "(6, 7, 467)": {
    "offset": 0
  },
  "(6, 7, 469)": {
    "offset": 0
  },
  "(6, 7, 470)": {
    "offset": 0
  },
  "(6, 7, 471)": {
    "offset": 0
  },
  "(6, 7, 475)": {
    "offset": 0
  },
  "(6, 7, 477)": {
    "offset": 0
  },
  "(6, 7, 478)": {
    "offset": 0
  },
  "(6, 7, 479)": {
    "offset": 0
  },
  "(8, 5, 23)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 13
  },
  "(8, 5, 24)": {
    "offset": 18
  },
  "(8, 5, 25)": {
    "offset": 18
  },
  "(8, 5, 26)": {
    "offset": 18
  },
  "(8, 5, 27)": {
    "offset": 18
  },
  "(8, 5, 28)": {
    "offset": 18
  },
  "(8, 5, 29)": {
    "offset": 18
  },
  "(8, 5, 30)": {
    "offset": 18
  },
  "(8, 5, 31)": {
    "offset": 18
  },
  "(8, 5, 32)": {
    "offset": 18
  },
  "(8, 5, 33)": {
    "offset": 18
  },
  "(8, 5, 34)": {
    "offset": 18
  },
  "(8, 5, 35)": {
    "offset": 18
  },
  "(8, 5, 36)": {
    "offset": 18
  },
  "(8, 5, 37)": {
    "offset": 18
  },
  "(8, 5, 38)": {
    "offset": 18
  },
  "(8, 5, 39)": {
    "offset": 18
  },
  "(8, 5, 40)": {
    "offset": 18
  },
  "(8, 5, 41)": {
    "offset": 18
  },
  "(8, 5, 42)": {
    "offset": 23
  },
  "(8, 5, 43)": {
    "offset": 23
  },
  "(8, 5, 44)": {
    "offset": 23
  },
  "(8, 5, 45)": {
    "offset": 23
  },
  "(8, 5, 46)": {
    "offset": 23
  },
  "(8, 5, 47)": {
    "offset": 23
  },
  "(8, 5, 48)": {
    "offset": 23
  },
  "(8, 5, 50)": {
    "offset": 23
  },
  "(8, 5, 52)": {
    "offset": 23
  },
  "(8, 5, 54)": {
    "offset": 23
  },
  "(8, 5, 55)": {
    "offset": 23
  },
  "(8, 5, 56)": {
    "offset": 23
  },
  "(8, 5, 57)": {
    "offset": 23
  },
  "(8, 5, 59)": {
    "offset": 23
  },
  "(8, 5, 60)": {
    "offset": 18
  },
  "(8, 5, 61)": {
    "offset": 18
  },
  "(8, 5, 62)": {
    "offset": 18
  },
  "(8, 5, 63)": {
    "offset": 18
  },
  "(8, 5, 64)": {
    "offset": 18
  },
  "(8, 5, 66)": {
    "offset": 18
  },
  "(8, 5, 68)": {
    "offset": 18
  },
  "(8, 5, 70)": {
    "offset": 18
  },
  "(8, 5, 71)": {
    "offset": 18
  },
  "(8, 5, 72)": {
    "offset": 18
  },
  "(8, 5, 73)": {
    "offset": 18
  },
  "(8, 5, 74)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 21
  },
  "(8, 5, 75)": {
    "offset": 18
  },
  "(8, 5, 76)": {
    "offset": 23
  },
  "(8, 5, 77)": {
    "offset": 18
  },
  "(8, 5, 78)": {
    "offset": 18
  },
  "(8, 5, 79)": {
    "offset": 18
  },
  "(8, 5, 80)": {
    "offset": 18
  },
  "(8, 5, 81)": {
    "port": 95,
    "copy": 767,
    "family": 5807,
    "offset": 19
  },
  "(8, 5, 82)": {
    "offset": 18
  },
  "(8, 5, 83)": {
    "port": 93,
    "copy": 765,
    "family": 5805,
    "offset": 18
  },
  "(8, 5, 84)": {
    "offset": 18
  },
  "(8, 5, 85)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 20
  },
  "(8, 5, 86)": {
    "offset": 18
  },
  "(8, 5, 88)": {
    "offset": 18
  },
  "(8, 5, 89)": {
    "offset": 18
  },
  "(8, 5, 90)": {
    "port": 100,
    "copy": 772,
    "family": 5812
  },
  "(8, 5, 91)": {
    "offset": 18
  },
  "(8, 5, 92)": {
    "offset": 18
  },
  "(8, 5, 93)": {
    "offset": 18
  },
  "(8, 5, 94)": {
    "offset": 18
  },
  "(8, 5, 95)": {
    "offset": 18
  },
  "(8, 5, 96)": {
    "offset": 18
  },
  "(8, 5, 97)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 28
  },
  "(8, 5, 98)": {
    "offset": 18
  },
  "(8, 5, 99)": {
    "port": 101,
    "copy": 773,
    "family": 5813,
    "offset": 19
  },
  "(8, 5, 100)": {
    "offset": 18
  },
  "(8, 5, 101)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 19
  },
  "(8, 5, 102)": {
    "offset": 18
  },
  "(8, 5, 104)": {
    "offset": 18
  },
  "(8, 5, 105)": {
    "offset": 18
  },
  "(8, 5, 106)": {
    "offset": 17
  },
  "(8, 5, 107)": {
    "offset": 18
  },
  "(8, 5, 108)": {
    "offset": 18
  },
  "(8, 5, 109)": {
    "offset": 18
  },
  "(8, 5, 110)": {
    "offset": 18
  },
  "(8, 5, 111)": {
    "offset": 18
  },
  "(8, 5, 112)": {
    "offset": 18
  },
  "(8, 5, 113)": {
    "port": 98,
    "copy": 770,
    "family": 5810,
    "offset": 21
  },
  "(8, 5, 114)": {
    "offset": 18
  },
  "(8, 5, 115)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 26
  },
  "(8, 5, 116)": {
    "offset": 18
  },
  "(8, 5, 117)": {
    "port": 102,
    "copy": 774,
    "family": 5814
  },
  "(8, 5, 118)": {
    "offset": 18
  },
  "(8, 5, 119)": {
    "offset": 18
  },
  "(8, 5, 120)": {
    "offset": 18
  },
  "(8, 5, 121)": {
    "offset": 18
  },
  "(8, 5, 122)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 28
  },
  "(8, 5, 123)": {
    "offset": 23
  },
  "(8, 5, 124)": {
    "offset": 23
  },
  "(8, 5, 125)": {
    "offset": 23
  },
  "(8, 5, 126)": {
    "offset": 23
  },
  "(8, 5, 127)": {
    "offset": 23
  },
  "(8, 5, 128)": {
    "offset": 23
  },
  "(8, 5, 130)": {
    "offset": 23
  },
  "(8, 5, 132)": {
    "offset": 23
  },
  "(8, 5, 134)": {
    "offset": 23
  },
  "(8, 5, 135)": {
    "offset": 23
  },
  "(8, 13, 108)": {
    "port": 100,
    "copy": 772,
    "family": 5812
  },
  "(8, 13, 109)": {
    "offset": 22
  },
  "(8, 13, 110)": {
    "port": 103,
    "copy": 775,
    "family": 5815,
    "offset": 22
  },
  "(8, 13, 111)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 22
  },
  "(8, 13, 112)": {
    "port": 93,
    "copy": 765,
    "family": 5805,
    "offset": 22
  },
  "(8, 13, 114)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 22
  },
  "(8, 13, 116)": {
    "port": 101,
    "copy": 773,
    "family": 5813,
    "offset": 23
  },
  "(8, 13, 118)": {
    "offset": 23
  },
  "(8, 13, 119)": {
    "port": 95,
    "copy": 767,
    "family": 5807,
    "offset": 23
  },
  "(7, 7, 74)": {
    "port": 100,
    "copy": 772,
    "family": 5812,
    "offset": 4
  },
  "(7, 7, 81)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 24
  },
  "(7, 7, 83)": {
    "port": 87,
    "copy": 759,
    "family": 5799,
    "offset": 24
  },
  "(7, 15, 74)": {
    "port": 87,
    "copy": 759,
    "family": 5799
  },
  "(7, 15, 119)": {
    "port": 97,
    "copy": 769,
    "family": 5809,
    "offset": 13
  },
  "(7, 15, 120)": {
    "offset": 9
  },
  "(7, 15, 121)": {
    "offset": 9
  },
  "(7, 15, 123)": {
    "offset": 9
  },
  "(7, 15, 124)": {
    "offset": 9
  },
  "(7, 15, 125)": {
    "offset": 9
  },
  "(7, 15, 126)": {
    "offset": 9
  },
  "(7, 15, 127)": {
    "offset": 9
  },
  "(7, 15, 128)": {
    "offset": 9
  },
  "(7, 15, 130)": {
    "offset": 9
  },
  "(7, 15, 132)": {
    "offset": 9
  },
  "(7, 15, 134)": {
    "offset": 9
  },
  "(7, 15, 135)": {
    "offset": 9
  },
  "(7, 15, 136)": {
    "offset": 9
  },
  "(7, 15, 137)": {
    "offset": 9
  },
  "(7, 15, 139)": {
    "offset": 9
  },
  "(7, 15, 140)": {
    "offset": 9
  },
  "(7, 15, 141)": {
    "offset": 9
  },
  "(7, 15, 142)": {
    "offset": 9
  },
  "(7, 15, 143)": {
    "offset": 14
  },
  "(7, 15, 144)": {
    "offset": 14
  },
  "(7, 15, 146)": {
    "offset": 14
  },
  "(7, 15, 148)": {
    "offset": 14
  },
  "(7, 15, 150)": {
    "offset": 14
  },
  "(7, 15, 151)": {
    "offset": 14
  },
  "(7, 15, 152)": {
    "offset": 14
  },
  "(7, 15, 153)": {
    "offset": 14
  },
  "(7, 15, 155)": {
    "offset": 14
  },
  "(7, 15, 156)": {
    "offset": 14
  },
  "(7, 15, 157)": {
    "offset": 14
  },
  "(7, 15, 158)": {
    "offset": 14
  },
  "(7, 15, 159)": {
    "offset": 14
  },
  "(7, 15, 160)": {
    "offset": 14
  },
  "(7, 15, 162)": {
    "offset": 9
  },
  "(7, 15, 164)": {
    "offset": 9
  },
  "(7, 15, 166)": {
    "offset": 9
  },
  "(7, 15, 167)": {
    "offset": 9
  },
  "(7, 15, 168)": {
    "offset": 9
  },
  "(7, 15, 169)": {
    "offset": 9
  },
  "(7, 15, 171)": {
    "offset": 9
  },
  "(7, 15, 172)": {
    "offset": 9
  },
  "(7, 15, 173)": {
    "offset": 9
  },
  "(7, 15, 174)": {
    "offset": 9
  },
  "(7, 15, 175)": {
    "offset": 9
  },
  "(7, 15, 176)": {
    "offset": 9
  },
  "(7, 15, 177)": {
    "offset": 14
  },
  "(7, 15, 178)": {
    "offset": 9
  },
  "(7, 15, 179)": {
    "offset": 9
  },
  "(7, 15, 180)": {
    "offset": 9
  },
  "(7, 15, 181)": {
    "offset": 9
  },
  "(7, 15, 182)": {
    "offset": 9
  },
  "(7, 15, 183)": {
    "offset": 9
  },
  "(7, 15, 184)": {
    "offset": 9
  },
  "(7, 15, 185)": {
    "offset": 9
  },
  "(7, 15, 186)": {
    "offset": 9
  },
  "(7, 15, 187)": {
    "offset": 9
  },
  "(7, 15, 188)": {
    "offset": 9
  },
  "(7, 15, 189)": {
    "offset": 9
  },
  "(7, 15, 190)": {
    "offset": 9
  },
  "(7, 15, 191)": {
    "offset": 9
  },
  "(7, 15, 192)": {
    "offset": 9
  },
  "(7, 15, 193)": {
    "offset": 9
  },
  "(7, 15, 194)": {
    "offset": 9
  },
  "(7, 15, 195)": {
    "offset": 9
  },
  "(7, 15, 196)": {
    "offset": 9
  },
  "(7, 15, 197)": {
    "offset": 9
  },
  "(7, 15, 198)": {
    "offset": 9
  },
  "(7, 15, 199)": {
    "offset": 9
  },
  "(7, 15, 200)": {
    "offset": 9
  },
  "(7, 15, 201)": {
    "offset": 9
  },
  "(7, 15, 202)": {
    "offset": 9
  },
  "(7, 15, 203)": {
    "offset": 9
  },
  "(7, 15, 204)": {
    "offset": 9
  },
  "(7, 15, 205)": {
    "offset": 9
  },
  "(7, 15, 206)": {
    "offset": 9
  },
  "(7, 15, 207)": {
    "offset": 9
  },
  "(7, 15, 208)": {
    "offset": 9
  },
  "(7, 15, 209)": {
    "offset": 9
  },
  "(7, 15, 210)": {
    "offset": 9
  },
  "(7, 15, 211)": {
    "offset": 9
  },
  "(7, 15, 212)": {
    "offset": 9
  },
  "(7, 15, 213)": {
    "offset": 9
  },
  "(7, 15, 214)": {
    "offset": 9
  },
  "(7, 15, 215)": {
    "offset": 9
  },
  "(7, 15, 216)": {
    "offset": 9
  },
  "(7, 15, 217)": {
    "offset": 9
  },
  "(7, 15, 218)": {
    "offset": 9
  },
  "(7, 15, 219)": {
    "offset": 9
  },
  "(8, 6, 445)": {
    "port": 88,
    "copy": 760,
    "family": 5800
  }
}

def apply_repack(roles):
    new_roles = []
    # Parse string keys
    changes_map = {}
    for k_str, diffs in CHANGES.items():
        parts = k_str.strip("()").split(",")
        tup = (int(parts[0]), int(parts[1]), int(parts[2]))
        changes_map[tup] = diffs

    for r in roles:
        k = (r["stage"], r["replica"], r["helper"])
        if k in changes_map:
            r = dict(r)
            r.update(changes_map[k])
        new_roles.append(r)

    # Re-pack offsets in affected ports on replica 6
    affected_ports = set(diffs["port"] for diffs in changes_map.values())
    for p in affected_ports:
        proles = [r for r in new_roles if r["child"] == 15 and (r["owner_replica"], r["port"]) == (6, p)]
        proles.sort(key=lambda x: (x["stage"], x["replica"], x["helper"]))
        curr = 0
        for r in proles:
            r["offset"] = curr
            curr += r["width"]

    return new_roles

def main():
    pkg = Path(__file__).resolve().parent
    owners_path = pkg / "data/OWNERS.json.gz"
    roles = json.loads(gzip.decompress(owners_path.read_bytes()))
    updated = apply_repack(roles)
    compressed = gzip.compress(json.dumps(updated, separators=(",", ":")).encode(), mtime=0)
    actual_sha = hashlib.sha256(compressed).hexdigest()
    assert actual_sha == TARGET_SHA, f"SHA mismatch: {actual_sha} != {TARGET_SHA}"
    owners_path.write_bytes(compressed)
    print(f"Successfully applied Breakthrough 9 repack ({len(CHANGES)} roles modified) to {owners_path}")
    print(f"Certified SHA-256: {actual_sha}")

if __name__ == "__main__":
    main()
