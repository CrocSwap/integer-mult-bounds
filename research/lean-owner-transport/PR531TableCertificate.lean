/- Generated kernel-checked finite certificates for the pinned PR531 witness. -/
import PR531TableData
namespace OwnerTransport.PR531Table
open OwnerTable
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def checkGroup (g : Nat) : Bool :=
  checkBlocks witness g (witness.window (g / witness.ports)).capacity 0 (witness.group g)

def checkCall (t : Nat) : Bool :=
  checkFamilies witness t 0 (witness.byFamily t)

theorem rowChunk0 : checkRange (checkRow witness) 0 504 = true := by decide
theorem rowChunk1 : checkRange (checkRow witness) 504 504 = true := by decide
theorem rowChunk2 : checkRange (checkRow witness) 1008 504 = true := by decide
theorem rowChunk3 : checkRange (checkRow witness) 1512 504 = true := by decide
theorem rowChunk4 : checkRange (checkRow witness) 2016 504 = true := by decide
theorem rowChunk5 : checkRange (checkRow witness) 2520 504 = true := by decide
theorem rowChunk6 : checkRange (checkRow witness) 3024 504 = true := by decide
theorem rowChunk7 : checkRange (checkRow witness) 3528 504 = true := by decide
theorem rowChunk8 : checkRange (checkRow witness) 4032 504 = true := by decide
theorem rowChunk9 : checkRange (checkRow witness) 4536 504 = true := by decide
theorem rowChunk10 : checkRange (checkRow witness) 5040 504 = true := by decide
theorem rowChunk11 : checkRange (checkRow witness) 5544 504 = true := by decide
theorem rowChunk12 : checkRange (checkRow witness) 6048 504 = true := by decide
theorem rowChunk13 : checkRange (checkRow witness) 6552 504 = true := by decide
theorem rowChunk14 : checkRange (checkRow witness) 7056 504 = true := by decide
theorem rowChunk15 : checkRange (checkRow witness) 7560 504 = true := by decide
theorem rowChunk16 : checkRange (checkRow witness) 8064 504 = true := by decide
theorem rowChunk17 : checkRange (checkRow witness) 8568 504 = true := by decide
theorem rowChunk18 : checkRange (checkRow witness) 9072 504 = true := by decide
theorem rowChunk19 : checkRange (checkRow witness) 9576 504 = true := by decide
theorem rowChunk20 : checkRange (checkRow witness) 10080 504 = true := by decide
theorem rowChunk21 : checkRange (checkRow witness) 10584 504 = true := by decide
theorem rowChunk22 : checkRange (checkRow witness) 11088 504 = true := by decide
theorem rowChunk23 : checkRange (checkRow witness) 11592 504 = true := by decide
theorem rowChunk24 : checkRange (checkRow witness) 12096 504 = true := by decide
theorem rowChunk25 : checkRange (checkRow witness) 12600 504 = true := by decide
theorem rowChunk26 : checkRange (checkRow witness) 13104 504 = true := by decide
theorem rowChunk27 : checkRange (checkRow witness) 13608 504 = true := by decide
theorem rowChunk28 : checkRange (checkRow witness) 14112 504 = true := by decide
theorem rowChunk29 : checkRange (checkRow witness) 14616 504 = true := by decide
theorem rowChunk30 : checkRange (checkRow witness) 15120 504 = true := by decide
theorem rowChunk31 : checkRange (checkRow witness) 15624 504 = true := by decide
theorem rowChunk32 : checkRange (checkRow witness) 16128 504 = true := by decide
theorem rowChunk33 : checkRange (checkRow witness) 16632 504 = true := by decide
theorem rowChunk34 : checkRange (checkRow witness) 17136 504 = true := by decide
theorem rowChunk35 : checkRange (checkRow witness) 17640 504 = true := by decide
theorem rowChunk36 : checkRange (checkRow witness) 18144 504 = true := by decide
theorem rowChunk37 : checkRange (checkRow witness) 18648 504 = true := by decide
theorem rowChunk38 : checkRange (checkRow witness) 19152 504 = true := by decide
theorem rowChunk39 : checkRange (checkRow witness) 19656 504 = true := by decide
theorem rowChunk40 : checkRange (checkRow witness) 20160 504 = true := by decide
theorem rowChunk41 : checkRange (checkRow witness) 20664 504 = true := by decide
theorem rowChunk42 : checkRange (checkRow witness) 21168 504 = true := by decide
theorem rowChunk43 : checkRange (checkRow witness) 21672 504 = true := by decide
theorem rowChunk44 : checkRange (checkRow witness) 22176 504 = true := by decide
theorem rowChunk45 : checkRange (checkRow witness) 22680 504 = true := by decide
theorem rowChunk46 : checkRange (checkRow witness) 23184 504 = true := by decide
theorem rowChunk47 : checkRange (checkRow witness) 23688 504 = true := by decide
theorem rowChunk48 : checkRange (checkRow witness) 24192 504 = true := by decide
theorem rowChunk49 : checkRange (checkRow witness) 24696 504 = true := by decide
theorem rowChunk50 : checkRange (checkRow witness) 25200 504 = true := by decide
theorem rowChunk51 : checkRange (checkRow witness) 25704 504 = true := by decide
theorem rowChunk52 : checkRange (checkRow witness) 26208 504 = true := by decide
theorem rowChunk53 : checkRange (checkRow witness) 26712 504 = true := by decide
theorem rowChunk54 : checkRange (checkRow witness) 27216 504 = true := by decide
theorem rowChunk55 : checkRange (checkRow witness) 27720 504 = true := by decide
theorem rowChunk56 : checkRange (checkRow witness) 28224 504 = true := by decide
theorem rowChunk57 : checkRange (checkRow witness) 28728 504 = true := by decide
theorem rowChunk58 : checkRange (checkRow witness) 29232 504 = true := by decide
theorem rowChunk59 : checkRange (checkRow witness) 29736 504 = true := by decide
theorem rowChunk60 : checkRange (checkRow witness) 30240 504 = true := by decide
theorem rowChunk61 : checkRange (checkRow witness) 30744 504 = true := by decide
theorem rowChunk62 : checkRange (checkRow witness) 31248 504 = true := by decide
theorem rowChunk63 : checkRange (checkRow witness) 31752 504 = true := by decide
theorem rowChunk64 : checkRange (checkRow witness) 32256 504 = true := by decide
theorem rowChunk65 : checkRange (checkRow witness) 32760 504 = true := by decide
theorem rowChunk66 : checkRange (checkRow witness) 33264 504 = true := by decide
theorem rowChunk67 : checkRange (checkRow witness) 33768 504 = true := by decide
theorem rowChunk68 : checkRange (checkRow witness) 34272 504 = true := by decide
theorem rowChunk69 : checkRange (checkRow witness) 34776 504 = true := by decide
theorem rowChunk70 : checkRange (checkRow witness) 35280 504 = true := by decide
theorem rowChunk71 : checkRange (checkRow witness) 35784 504 = true := by decide

theorem rowChunks (q : Nat) (h : q < 72) :
    checkRange (checkRow witness) (q * 504) 504 = true := by
  match q with
  | 0 => exact rowChunk0
  | 1 => exact rowChunk1
  | 2 => exact rowChunk2
  | 3 => exact rowChunk3
  | 4 => exact rowChunk4
  | 5 => exact rowChunk5
  | 6 => exact rowChunk6
  | 7 => exact rowChunk7
  | 8 => exact rowChunk8
  | 9 => exact rowChunk9
  | 10 => exact rowChunk10
  | 11 => exact rowChunk11
  | 12 => exact rowChunk12
  | 13 => exact rowChunk13
  | 14 => exact rowChunk14
  | 15 => exact rowChunk15
  | 16 => exact rowChunk16
  | 17 => exact rowChunk17
  | 18 => exact rowChunk18
  | 19 => exact rowChunk19
  | 20 => exact rowChunk20
  | 21 => exact rowChunk21
  | 22 => exact rowChunk22
  | 23 => exact rowChunk23
  | 24 => exact rowChunk24
  | 25 => exact rowChunk25
  | 26 => exact rowChunk26
  | 27 => exact rowChunk27
  | 28 => exact rowChunk28
  | 29 => exact rowChunk29
  | 30 => exact rowChunk30
  | 31 => exact rowChunk31
  | 32 => exact rowChunk32
  | 33 => exact rowChunk33
  | 34 => exact rowChunk34
  | 35 => exact rowChunk35
  | 36 => exact rowChunk36
  | 37 => exact rowChunk37
  | 38 => exact rowChunk38
  | 39 => exact rowChunk39
  | 40 => exact rowChunk40
  | 41 => exact rowChunk41
  | 42 => exact rowChunk42
  | 43 => exact rowChunk43
  | 44 => exact rowChunk44
  | 45 => exact rowChunk45
  | 46 => exact rowChunk46
  | 47 => exact rowChunk47
  | 48 => exact rowChunk48
  | 49 => exact rowChunk49
  | 50 => exact rowChunk50
  | 51 => exact rowChunk51
  | 52 => exact rowChunk52
  | 53 => exact rowChunk53
  | 54 => exact rowChunk54
  | 55 => exact rowChunk55
  | 56 => exact rowChunk56
  | 57 => exact rowChunk57
  | 58 => exact rowChunk58
  | 59 => exact rowChunk59
  | 60 => exact rowChunk60
  | 61 => exact rowChunk61
  | 62 => exact rowChunk62
  | 63 => exact rowChunk63
  | 64 => exact rowChunk64
  | 65 => exact rowChunk65
  | 66 => exact rowChunk66
  | 67 => exact rowChunk67
  | 68 => exact rowChunk68
  | 69 => exact rowChunk69
  | 70 => exact rowChunk70
  | 71 => exact rowChunk71
  | n + 72 => omega

theorem groupChunk0 : checkRange (checkGroup) 0 112 = true := by decide
theorem groupChunk1 : checkRange (checkGroup) 112 112 = true := by decide
theorem groupChunk2 : checkRange (checkGroup) 224 112 = true := by decide
theorem groupChunk3 : checkRange (checkGroup) 336 112 = true := by decide
theorem groupChunk4 : checkRange (checkGroup) 448 112 = true := by decide
theorem groupChunk5 : checkRange (checkGroup) 560 112 = true := by decide
theorem groupChunk6 : checkRange (checkGroup) 672 112 = true := by decide
theorem groupChunk7 : checkRange (checkGroup) 784 112 = true := by decide
theorem groupChunk8 : checkRange (checkGroup) 896 112 = true := by decide
theorem groupChunk9 : checkRange (checkGroup) 1008 112 = true := by decide
theorem groupChunk10 : checkRange (checkGroup) 1120 112 = true := by decide
theorem groupChunk11 : checkRange (checkGroup) 1232 112 = true := by decide
theorem groupChunk12 : checkRange (checkGroup) 1344 112 = true := by decide
theorem groupChunk13 : checkRange (checkGroup) 1456 112 = true := by decide
theorem groupChunk14 : checkRange (checkGroup) 1568 112 = true := by decide
theorem groupChunk15 : checkRange (checkGroup) 1680 112 = true := by decide
theorem groupChunk16 : checkRange (checkGroup) 1792 112 = true := by decide
theorem groupChunk17 : checkRange (checkGroup) 1904 112 = true := by decide
theorem groupChunk18 : checkRange (checkGroup) 2016 112 = true := by decide
theorem groupChunk19 : checkRange (checkGroup) 2128 112 = true := by decide
theorem groupChunk20 : checkRange (checkGroup) 2240 112 = true := by decide
theorem groupChunk21 : checkRange (checkGroup) 2352 112 = true := by decide
theorem groupChunk22 : checkRange (checkGroup) 2464 112 = true := by decide
theorem groupChunk23 : checkRange (checkGroup) 2576 112 = true := by decide
theorem groupChunk24 : checkRange (checkGroup) 2688 112 = true := by decide
theorem groupChunk25 : checkRange (checkGroup) 2800 112 = true := by decide
theorem groupChunk26 : checkRange (checkGroup) 2912 112 = true := by decide
theorem groupChunk27 : checkRange (checkGroup) 3024 112 = true := by decide
theorem groupChunk28 : checkRange (checkGroup) 3136 112 = true := by decide
theorem groupChunk29 : checkRange (checkGroup) 3248 112 = true := by decide
theorem groupChunk30 : checkRange (checkGroup) 3360 112 = true := by decide
theorem groupChunk31 : checkRange (checkGroup) 3472 112 = true := by decide
theorem groupChunk32 : checkRange (checkGroup) 3584 112 = true := by decide
theorem groupChunk33 : checkRange (checkGroup) 3696 112 = true := by decide
theorem groupChunk34 : checkRange (checkGroup) 3808 112 = true := by decide
theorem groupChunk35 : checkRange (checkGroup) 3920 112 = true := by decide
theorem groupChunk36 : checkRange (checkGroup) 4032 112 = true := by decide
theorem groupChunk37 : checkRange (checkGroup) 4144 112 = true := by decide
theorem groupChunk38 : checkRange (checkGroup) 4256 112 = true := by decide
theorem groupChunk39 : checkRange (checkGroup) 4368 112 = true := by decide
theorem groupChunk40 : checkRange (checkGroup) 4480 112 = true := by decide
theorem groupChunk41 : checkRange (checkGroup) 4592 112 = true := by decide
theorem groupChunk42 : checkRange (checkGroup) 4704 112 = true := by decide
theorem groupChunk43 : checkRange (checkGroup) 4816 112 = true := by decide
theorem groupChunk44 : checkRange (checkGroup) 4928 112 = true := by decide
theorem groupChunk45 : checkRange (checkGroup) 5040 112 = true := by decide
theorem groupChunk46 : checkRange (checkGroup) 5152 112 = true := by decide
theorem groupChunk47 : checkRange (checkGroup) 5264 112 = true := by decide
theorem groupChunk48 : checkRange (checkGroup) 5376 112 = true := by decide
theorem groupChunk49 : checkRange (checkGroup) 5488 112 = true := by decide
theorem groupChunk50 : checkRange (checkGroup) 5600 112 = true := by decide
theorem groupChunk51 : checkRange (checkGroup) 5712 112 = true := by decide
theorem groupChunk52 : checkRange (checkGroup) 5824 112 = true := by decide
theorem groupChunk53 : checkRange (checkGroup) 5936 112 = true := by decide
theorem groupChunk54 : checkRange (checkGroup) 6048 112 = true := by decide
theorem groupChunk55 : checkRange (checkGroup) 6160 112 = true := by decide
theorem groupChunk56 : checkRange (checkGroup) 6272 112 = true := by decide
theorem groupChunk57 : checkRange (checkGroup) 6384 112 = true := by decide
theorem groupChunk58 : checkRange (checkGroup) 6496 112 = true := by decide
theorem groupChunk59 : checkRange (checkGroup) 6608 112 = true := by decide
theorem groupChunk60 : checkRange (checkGroup) 6720 112 = true := by decide
theorem groupChunk61 : checkRange (checkGroup) 6832 112 = true := by decide
theorem groupChunk62 : checkRange (checkGroup) 6944 112 = true := by decide
theorem groupChunk63 : checkRange (checkGroup) 7056 112 = true := by decide
theorem groupChunk64 : checkRange (checkGroup) 7168 112 = true := by decide
theorem groupChunk65 : checkRange (checkGroup) 7280 112 = true := by decide
theorem groupChunk66 : checkRange (checkGroup) 7392 112 = true := by decide
theorem groupChunk67 : checkRange (checkGroup) 7504 112 = true := by decide
theorem groupChunk68 : checkRange (checkGroup) 7616 112 = true := by decide
theorem groupChunk69 : checkRange (checkGroup) 7728 112 = true := by decide
theorem groupChunk70 : checkRange (checkGroup) 7840 112 = true := by decide
theorem groupChunk71 : checkRange (checkGroup) 7952 112 = true := by decide
theorem groupChunk72 : checkRange (checkGroup) 8064 112 = true := by decide
theorem groupChunk73 : checkRange (checkGroup) 8176 112 = true := by decide
theorem groupChunk74 : checkRange (checkGroup) 8288 112 = true := by decide
theorem groupChunk75 : checkRange (checkGroup) 8400 112 = true := by decide
theorem groupChunk76 : checkRange (checkGroup) 8512 112 = true := by decide
theorem groupChunk77 : checkRange (checkGroup) 8624 112 = true := by decide
theorem groupChunk78 : checkRange (checkGroup) 8736 112 = true := by decide
theorem groupChunk79 : checkRange (checkGroup) 8848 112 = true := by decide
theorem groupChunk80 : checkRange (checkGroup) 8960 112 = true := by decide
theorem groupChunk81 : checkRange (checkGroup) 9072 112 = true := by decide
theorem groupChunk82 : checkRange (checkGroup) 9184 112 = true := by decide
theorem groupChunk83 : checkRange (checkGroup) 9296 112 = true := by decide
theorem groupChunk84 : checkRange (checkGroup) 9408 112 = true := by decide
theorem groupChunk85 : checkRange (checkGroup) 9520 112 = true := by decide
theorem groupChunk86 : checkRange (checkGroup) 9632 112 = true := by decide
theorem groupChunk87 : checkRange (checkGroup) 9744 112 = true := by decide
theorem groupChunk88 : checkRange (checkGroup) 9856 112 = true := by decide
theorem groupChunk89 : checkRange (checkGroup) 9968 112 = true := by decide
theorem groupChunk90 : checkRange (checkGroup) 10080 112 = true := by decide
theorem groupChunk91 : checkRange (checkGroup) 10192 112 = true := by decide
theorem groupChunk92 : checkRange (checkGroup) 10304 112 = true := by decide
theorem groupChunk93 : checkRange (checkGroup) 10416 112 = true := by decide
theorem groupChunk94 : checkRange (checkGroup) 10528 112 = true := by decide
theorem groupChunk95 : checkRange (checkGroup) 10640 112 = true := by decide
theorem groupChunk96 : checkRange (checkGroup) 10752 112 = true := by decide
theorem groupChunk97 : checkRange (checkGroup) 10864 112 = true := by decide
theorem groupChunk98 : checkRange (checkGroup) 10976 112 = true := by decide
theorem groupChunk99 : checkRange (checkGroup) 11088 112 = true := by decide
theorem groupChunk100 : checkRange (checkGroup) 11200 112 = true := by decide
theorem groupChunk101 : checkRange (checkGroup) 11312 112 = true := by decide
theorem groupChunk102 : checkRange (checkGroup) 11424 112 = true := by decide
theorem groupChunk103 : checkRange (checkGroup) 11536 112 = true := by decide
theorem groupChunk104 : checkRange (checkGroup) 11648 112 = true := by decide
theorem groupChunk105 : checkRange (checkGroup) 11760 112 = true := by decide
theorem groupChunk106 : checkRange (checkGroup) 11872 112 = true := by decide
theorem groupChunk107 : checkRange (checkGroup) 11984 112 = true := by decide
theorem groupChunk108 : checkRange (checkGroup) 12096 112 = true := by decide
theorem groupChunk109 : checkRange (checkGroup) 12208 112 = true := by decide
theorem groupChunk110 : checkRange (checkGroup) 12320 112 = true := by decide
theorem groupChunk111 : checkRange (checkGroup) 12432 112 = true := by decide
theorem groupChunk112 : checkRange (checkGroup) 12544 112 = true := by decide
theorem groupChunk113 : checkRange (checkGroup) 12656 112 = true := by decide
theorem groupChunk114 : checkRange (checkGroup) 12768 112 = true := by decide
theorem groupChunk115 : checkRange (checkGroup) 12880 112 = true := by decide
theorem groupChunk116 : checkRange (checkGroup) 12992 112 = true := by decide
theorem groupChunk117 : checkRange (checkGroup) 13104 112 = true := by decide
theorem groupChunk118 : checkRange (checkGroup) 13216 112 = true := by decide
theorem groupChunk119 : checkRange (checkGroup) 13328 112 = true := by decide
theorem groupChunk120 : checkRange (checkGroup) 13440 112 = true := by decide
theorem groupChunk121 : checkRange (checkGroup) 13552 112 = true := by decide
theorem groupChunk122 : checkRange (checkGroup) 13664 112 = true := by decide
theorem groupChunk123 : checkRange (checkGroup) 13776 112 = true := by decide
theorem groupChunk124 : checkRange (checkGroup) 13888 112 = true := by decide
theorem groupChunk125 : checkRange (checkGroup) 14000 112 = true := by decide
theorem groupChunk126 : checkRange (checkGroup) 14112 112 = true := by decide
theorem groupChunk127 : checkRange (checkGroup) 14224 112 = true := by decide
theorem groupChunk128 : checkRange (checkGroup) 14336 112 = true := by decide
theorem groupChunk129 : checkRange (checkGroup) 14448 112 = true := by decide
theorem groupChunk130 : checkRange (checkGroup) 14560 112 = true := by decide
theorem groupChunk131 : checkRange (checkGroup) 14672 112 = true := by decide
theorem groupChunk132 : checkRange (checkGroup) 14784 112 = true := by decide
theorem groupChunk133 : checkRange (checkGroup) 14896 112 = true := by decide
theorem groupChunk134 : checkRange (checkGroup) 15008 112 = true := by decide
theorem groupChunk135 : checkRange (checkGroup) 15120 112 = true := by decide
theorem groupChunk136 : checkRange (checkGroup) 15232 112 = true := by decide
theorem groupChunk137 : checkRange (checkGroup) 15344 112 = true := by decide
theorem groupChunk138 : checkRange (checkGroup) 15456 112 = true := by decide
theorem groupChunk139 : checkRange (checkGroup) 15568 112 = true := by decide
theorem groupChunk140 : checkRange (checkGroup) 15680 112 = true := by decide
theorem groupChunk141 : checkRange (checkGroup) 15792 112 = true := by decide
theorem groupChunk142 : checkRange (checkGroup) 15904 112 = true := by decide
theorem groupChunk143 : checkRange (checkGroup) 16016 112 = true := by decide

theorem groupChunks (q : Nat) (h : q < 144) :
    checkRange (checkGroup) (q * 112) 112 = true := by
  match q with
  | 0 => exact groupChunk0
  | 1 => exact groupChunk1
  | 2 => exact groupChunk2
  | 3 => exact groupChunk3
  | 4 => exact groupChunk4
  | 5 => exact groupChunk5
  | 6 => exact groupChunk6
  | 7 => exact groupChunk7
  | 8 => exact groupChunk8
  | 9 => exact groupChunk9
  | 10 => exact groupChunk10
  | 11 => exact groupChunk11
  | 12 => exact groupChunk12
  | 13 => exact groupChunk13
  | 14 => exact groupChunk14
  | 15 => exact groupChunk15
  | 16 => exact groupChunk16
  | 17 => exact groupChunk17
  | 18 => exact groupChunk18
  | 19 => exact groupChunk19
  | 20 => exact groupChunk20
  | 21 => exact groupChunk21
  | 22 => exact groupChunk22
  | 23 => exact groupChunk23
  | 24 => exact groupChunk24
  | 25 => exact groupChunk25
  | 26 => exact groupChunk26
  | 27 => exact groupChunk27
  | 28 => exact groupChunk28
  | 29 => exact groupChunk29
  | 30 => exact groupChunk30
  | 31 => exact groupChunk31
  | 32 => exact groupChunk32
  | 33 => exact groupChunk33
  | 34 => exact groupChunk34
  | 35 => exact groupChunk35
  | 36 => exact groupChunk36
  | 37 => exact groupChunk37
  | 38 => exact groupChunk38
  | 39 => exact groupChunk39
  | 40 => exact groupChunk40
  | 41 => exact groupChunk41
  | 42 => exact groupChunk42
  | 43 => exact groupChunk43
  | 44 => exact groupChunk44
  | 45 => exact groupChunk45
  | 46 => exact groupChunk46
  | 47 => exact groupChunk47
  | 48 => exact groupChunk48
  | 49 => exact groupChunk49
  | 50 => exact groupChunk50
  | 51 => exact groupChunk51
  | 52 => exact groupChunk52
  | 53 => exact groupChunk53
  | 54 => exact groupChunk54
  | 55 => exact groupChunk55
  | 56 => exact groupChunk56
  | 57 => exact groupChunk57
  | 58 => exact groupChunk58
  | 59 => exact groupChunk59
  | 60 => exact groupChunk60
  | 61 => exact groupChunk61
  | 62 => exact groupChunk62
  | 63 => exact groupChunk63
  | 64 => exact groupChunk64
  | 65 => exact groupChunk65
  | 66 => exact groupChunk66
  | 67 => exact groupChunk67
  | 68 => exact groupChunk68
  | 69 => exact groupChunk69
  | 70 => exact groupChunk70
  | 71 => exact groupChunk71
  | 72 => exact groupChunk72
  | 73 => exact groupChunk73
  | 74 => exact groupChunk74
  | 75 => exact groupChunk75
  | 76 => exact groupChunk76
  | 77 => exact groupChunk77
  | 78 => exact groupChunk78
  | 79 => exact groupChunk79
  | 80 => exact groupChunk80
  | 81 => exact groupChunk81
  | 82 => exact groupChunk82
  | 83 => exact groupChunk83
  | 84 => exact groupChunk84
  | 85 => exact groupChunk85
  | 86 => exact groupChunk86
  | 87 => exact groupChunk87
  | 88 => exact groupChunk88
  | 89 => exact groupChunk89
  | 90 => exact groupChunk90
  | 91 => exact groupChunk91
  | 92 => exact groupChunk92
  | 93 => exact groupChunk93
  | 94 => exact groupChunk94
  | 95 => exact groupChunk95
  | 96 => exact groupChunk96
  | 97 => exact groupChunk97
  | 98 => exact groupChunk98
  | 99 => exact groupChunk99
  | 100 => exact groupChunk100
  | 101 => exact groupChunk101
  | 102 => exact groupChunk102
  | 103 => exact groupChunk103
  | 104 => exact groupChunk104
  | 105 => exact groupChunk105
  | 106 => exact groupChunk106
  | 107 => exact groupChunk107
  | 108 => exact groupChunk108
  | 109 => exact groupChunk109
  | 110 => exact groupChunk110
  | 111 => exact groupChunk111
  | 112 => exact groupChunk112
  | 113 => exact groupChunk113
  | 114 => exact groupChunk114
  | 115 => exact groupChunk115
  | 116 => exact groupChunk116
  | 117 => exact groupChunk117
  | 118 => exact groupChunk118
  | 119 => exact groupChunk119
  | 120 => exact groupChunk120
  | 121 => exact groupChunk121
  | 122 => exact groupChunk122
  | 123 => exact groupChunk123
  | 124 => exact groupChunk124
  | 125 => exact groupChunk125
  | 126 => exact groupChunk126
  | 127 => exact groupChunk127
  | 128 => exact groupChunk128
  | 129 => exact groupChunk129
  | 130 => exact groupChunk130
  | 131 => exact groupChunk131
  | 132 => exact groupChunk132
  | 133 => exact groupChunk133
  | 134 => exact groupChunk134
  | 135 => exact groupChunk135
  | 136 => exact groupChunk136
  | 137 => exact groupChunk137
  | 138 => exact groupChunk138
  | 139 => exact groupChunk139
  | 140 => exact groupChunk140
  | 141 => exact groupChunk141
  | 142 => exact groupChunk142
  | 143 => exact groupChunk143
  | n + 144 => omega

theorem callChunk0 : checkRange (checkCall) 0 1 = true := by decide
theorem callChunk1 : checkRange (checkCall) 1 1 = true := by decide
theorem callChunk2 : checkRange (checkCall) 2 1 = true := by decide
theorem callChunk3 : checkRange (checkCall) 3 1 = true := by decide
theorem callChunk4 : checkRange (checkCall) 4 1 = true := by decide
theorem callChunk5 : checkRange (checkCall) 5 1 = true := by decide
theorem callChunk6 : checkRange (checkCall) 6 1 = true := by decide
theorem callChunk7 : checkRange (checkCall) 7 1 = true := by decide
theorem callChunk8 : checkRange (checkCall) 8 1 = true := by decide
theorem callChunk9 : checkRange (checkCall) 9 1 = true := by decide
theorem callChunk10 : checkRange (checkCall) 10 1 = true := by decide
theorem callChunk11 : checkRange (checkCall) 11 1 = true := by decide
theorem callChunk12 : checkRange (checkCall) 12 1 = true := by decide
theorem callChunk13 : checkRange (checkCall) 13 1 = true := by decide
theorem callChunk14 : checkRange (checkCall) 14 1 = true := by decide
theorem callChunk15 : checkRange (checkCall) 15 1 = true := by decide
theorem callChunk16 : checkRange (checkCall) 16 1 = true := by decide
theorem callChunk17 : checkRange (checkCall) 17 1 = true := by decide
theorem callChunk18 : checkRange (checkCall) 18 1 = true := by decide
theorem callChunk19 : checkRange (checkCall) 19 1 = true := by decide
theorem callChunk20 : checkRange (checkCall) 20 1 = true := by decide
theorem callChunk21 : checkRange (checkCall) 21 1 = true := by decide
theorem callChunk22 : checkRange (checkCall) 22 1 = true := by decide
theorem callChunk23 : checkRange (checkCall) 23 1 = true := by decide
theorem callChunk24 : checkRange (checkCall) 24 1 = true := by decide
theorem callChunk25 : checkRange (checkCall) 25 1 = true := by decide
theorem callChunk26 : checkRange (checkCall) 26 1 = true := by decide
theorem callChunk27 : checkRange (checkCall) 27 1 = true := by decide
theorem callChunk28 : checkRange (checkCall) 28 1 = true := by decide
theorem callChunk29 : checkRange (checkCall) 29 1 = true := by decide
theorem callChunk30 : checkRange (checkCall) 30 1 = true := by decide
theorem callChunk31 : checkRange (checkCall) 31 1 = true := by decide
theorem callChunk32 : checkRange (checkCall) 32 1 = true := by decide
theorem callChunk33 : checkRange (checkCall) 33 1 = true := by decide
theorem callChunk34 : checkRange (checkCall) 34 1 = true := by decide
theorem callChunk35 : checkRange (checkCall) 35 1 = true := by decide
theorem callChunk36 : checkRange (checkCall) 36 1 = true := by decide
theorem callChunk37 : checkRange (checkCall) 37 1 = true := by decide
theorem callChunk38 : checkRange (checkCall) 38 1 = true := by decide
theorem callChunk39 : checkRange (checkCall) 39 1 = true := by decide
theorem callChunk40 : checkRange (checkCall) 40 1 = true := by decide
theorem callChunk41 : checkRange (checkCall) 41 1 = true := by decide
theorem callChunk42 : checkRange (checkCall) 42 1 = true := by decide
theorem callChunk43 : checkRange (checkCall) 43 1 = true := by decide
theorem callChunk44 : checkRange (checkCall) 44 1 = true := by decide
theorem callChunk45 : checkRange (checkCall) 45 1 = true := by decide
theorem callChunk46 : checkRange (checkCall) 46 1 = true := by decide
theorem callChunk47 : checkRange (checkCall) 47 1 = true := by decide
theorem callChunk48 : checkRange (checkCall) 48 1 = true := by decide
theorem callChunk49 : checkRange (checkCall) 49 1 = true := by decide
theorem callChunk50 : checkRange (checkCall) 50 1 = true := by decide
theorem callChunk51 : checkRange (checkCall) 51 1 = true := by decide
theorem callChunk52 : checkRange (checkCall) 52 1 = true := by decide
theorem callChunk53 : checkRange (checkCall) 53 1 = true := by decide
theorem callChunk54 : checkRange (checkCall) 54 1 = true := by decide
theorem callChunk55 : checkRange (checkCall) 55 1 = true := by decide
theorem callChunk56 : checkRange (checkCall) 56 1 = true := by decide
theorem callChunk57 : checkRange (checkCall) 57 1 = true := by decide
theorem callChunk58 : checkRange (checkCall) 58 1 = true := by decide
theorem callChunk59 : checkRange (checkCall) 59 1 = true := by decide
theorem callChunk60 : checkRange (checkCall) 60 1 = true := by decide
theorem callChunk61 : checkRange (checkCall) 61 1 = true := by decide
theorem callChunk62 : checkRange (checkCall) 62 1 = true := by decide
theorem callChunk63 : checkRange (checkCall) 63 1 = true := by decide
theorem callChunk64 : checkRange (checkCall) 64 1 = true := by decide
theorem callChunk65 : checkRange (checkCall) 65 1 = true := by decide
theorem callChunk66 : checkRange (checkCall) 66 1 = true := by decide
theorem callChunk67 : checkRange (checkCall) 67 1 = true := by decide
theorem callChunk68 : checkRange (checkCall) 68 1 = true := by decide
theorem callChunk69 : checkRange (checkCall) 69 1 = true := by decide
theorem callChunk70 : checkRange (checkCall) 70 1 = true := by decide
theorem callChunk71 : checkRange (checkCall) 71 1 = true := by decide

theorem callChunks (q : Nat) (h : q < 72) :
    checkRange (checkCall) (q * 1) 1 = true := by
  match q with
  | 0 => exact callChunk0
  | 1 => exact callChunk1
  | 2 => exact callChunk2
  | 3 => exact callChunk3
  | 4 => exact callChunk4
  | 5 => exact callChunk5
  | 6 => exact callChunk6
  | 7 => exact callChunk7
  | 8 => exact callChunk8
  | 9 => exact callChunk9
  | 10 => exact callChunk10
  | 11 => exact callChunk11
  | 12 => exact callChunk12
  | 13 => exact callChunk13
  | 14 => exact callChunk14
  | 15 => exact callChunk15
  | 16 => exact callChunk16
  | 17 => exact callChunk17
  | 18 => exact callChunk18
  | 19 => exact callChunk19
  | 20 => exact callChunk20
  | 21 => exact callChunk21
  | 22 => exact callChunk22
  | 23 => exact callChunk23
  | 24 => exact callChunk24
  | 25 => exact callChunk25
  | 26 => exact callChunk26
  | 27 => exact callChunk27
  | 28 => exact callChunk28
  | 29 => exact callChunk29
  | 30 => exact callChunk30
  | 31 => exact callChunk31
  | 32 => exact callChunk32
  | 33 => exact callChunk33
  | 34 => exact callChunk34
  | 35 => exact callChunk35
  | 36 => exact callChunk36
  | 37 => exact callChunk37
  | 38 => exact callChunk38
  | 39 => exact callChunk39
  | 40 => exact callChunk40
  | 41 => exact callChunk41
  | 42 => exact callChunk42
  | 43 => exact callChunk43
  | 44 => exact callChunk44
  | 45 => exact callChunk45
  | 46 => exact callChunk46
  | 47 => exact callChunk47
  | 48 => exact callChunk48
  | 49 => exact callChunk49
  | 50 => exact callChunk50
  | 51 => exact callChunk51
  | 52 => exact callChunk52
  | 53 => exact callChunk53
  | 54 => exact callChunk54
  | 55 => exact callChunk55
  | 56 => exact callChunk56
  | 57 => exact callChunk57
  | 58 => exact callChunk58
  | 59 => exact callChunk59
  | 60 => exact callChunk60
  | 61 => exact callChunk61
  | 62 => exact callChunk62
  | 63 => exact callChunk63
  | 64 => exact callChunk64
  | 65 => exact callChunk65
  | 66 => exact callChunk66
  | 67 => exact callChunk67
  | 68 => exact callChunk68
  | 69 => exact callChunk69
  | 70 => exact callChunk70
  | 71 => exact callChunk71
  | n + 72 => omega

/-- Every row and every inverse-index list of the selected witness is checked. -/
theorem accepted : Accepted witness := by
  refine ⟨?_, ?_, ?_⟩
  · intro i hi
    exact chunks_sound (checkRow witness) 504 72 (by decide) rowChunks i hi
  · intro g hg
    exact chunks_sound checkGroup 112 144 (by decide) groupChunks g hg
  · intro t ht
    exact chunks_sound checkCall 1 72 (by decide) callChunks t ht

/-- Each of the actual selected rows meets the semantic row contract. -/
theorem every_row_valid (i : Nat) (hi : i < rowCount witness) : RowValid witness i :=
  accepted_row witness accepted i hi

/-- The exact declared window bounds every occupied coordinate. -/
theorem every_coordinate_fits (i x : Nat) (hi : i < rowCount witness)
    (hx : x < (witness.row i).width) :
    (witness.row i).offset + x <
      (witness.window ((witness.row i).ownerReplica * witness.children + (witness.row i).child)).capacity :=
  accepted_declared_window_capacity witness accepted i x hi hx

/-- Equal physical-family identifiers in the same call identify the same row. -/
theorem owners_injective (i j : Nat) (hi : i < rowCount witness) (hj : j < rowCount witness)
    (ht : (witness.row i).time = (witness.row j).time)
    (hf : (witness.row i).family = (witness.row j).family) : i = j :=
  accepted_owner_injective witness accepted i j hi hj ht hf

/-- The actual per-group occupied addresses are injective. -/
theorem coordinates_injective (i j x y : Nat)
    (hi : i < rowCount witness) (hj : j < rowCount witness)
    (hg : groupId witness (witness.row i) = groupId witness (witness.row j))
    (hx : x < (witness.row i).width) (hy : y < (witness.row j).width)
    (heq : (witness.row i).offset + x = (witness.row j).offset + y) : i = j ∧ x = y :=
  accepted_nonalias witness accepted i j x y hi hj hg hx hy heq

/-- Every call/helper pair is represented by exactly one row. -/
theorem every_helper_present (t helper : Nat) (ht : t < witness.calls) (hh : helper < witness.helpers) :
    ∃ i, i < rowCount witness ∧ (witness.row i).time = t ∧ (witness.row i).helper = helper ∧
      ∀ j, j < rowCount witness → (witness.row j).time = t → (witness.row j).helper = helper → j = i :=
  accepted_census witness accepted t helper ht hh

/-- Concrete helpers in each selected invocation have pairwise distinct owners. -/
theorem helper_owners_injective (t : Nat) (ht : t < witness.calls) :
    ∀ a b : Fin witness.helpers, helperOwner witness t a = helperOwner witness t b → a = b :=
  helper_owner_injective witness accepted t ht

end OwnerTransport.PR531Table
