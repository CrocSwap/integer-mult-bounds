# SPDX-License-Identifier: Apache-2.0
"""Full authenticated native validation for the changed 485/1455 producer.

Based on retained #7480 verify_native.py, attributed there to Rohan Arun,
dillona, and OpenAI Codex assistance. Source closure is authenticated through
its unmodified source.py. Every engine adaptation is counted and logged.
All inventories, prices, grids, envelopes, and physical checks are freshly
computed for the literal candidate. This does not select a public frontier.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from types import ModuleType
import sys,json,gzip,subprocess,tempfile,io,contextlib,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480'
CANDIDATE=ROOT/'producer54/reroute'
sys.path.insert(0,str(SOURCE))
from source import read,load,sources,canonical,need
from construct import construct
from derive_grid import derive
from verify_native import normalized,delta,rejects,forward_endpoint

EXPECTED='03da65fb97ffaf4d0e9756f3867df588b162975f6015d8458821d05b5fcb006b'
BASELINE='5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'
PATCHES=[]
TIMINGS=[]
def module(name,path,edits=()):
    raw=path.read_text();record={'module':name,'source_name':path.name,'source_sha256':sha256(raw.encode()).hexdigest(),'edits':[]}
    for before,after in edits:
        count=raw.count(before);need(count==1,'Unique adaptation '+repr(before))
        raw=raw.replace(before,after)
        record['edits'].append({'before':before,'after':after,'occurrences':count})
    record['adapted_sha256']=sha256(raw.encode()).hexdigest();PATCHES.append(record)
    obj=ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(raw,str(path),'exec'),obj.__dict__)
    return obj

def checkpoint(stage,data=None):
    now=time.time();TIMINGS.append({'stage':stage,'elapsed_seconds':now-STARTED})
    (HERE/'CHECKPOINT.json').write_text(json.dumps(normalized({'stage':stage,'word_canonical_sha256':EXPECTED,'data':data,'timings':TIMINGS}),indent=2)+'\n')
    print('PASS',stage,flush=True)

def charts(vendor,word):
    compiler=load('helper757_chart_compiler',vendor/'frozen/clifford_exact.py')
    interpreter=load('helper757_chart_interpreter',vendor/'frozen/native_verify.py')
    before=read(ROOT/'frozen-composition/7481-WORD.json.gz')
    need(sha256(canonical(before)).hexdigest()=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8','Exact #7481 physical comparator')
    routes=lambda w:{i:[tuple(e[2:4])for e in w['program']if e[0]=='MOVE'and e[1]==i]for i in range(w['public'])}
    source7620=read(ROOT/'frozen-composition/7620-WORD.json.gz')
    need(sha256(canonical(source7620)).hexdigest()=='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d','Exact source 7620 for preserved physical census')
    old_routes,new_routes=routes(before),routes(source7620)
    changed=[i for i in old_routes if old_routes[i]!=new_routes[i]]
    affected={pair for i in changed for pair in old_routes[i]+new_routes[i]}
    need(affected==set([(1, 389), (1, 390), (2, 299), (3, 1), (3, 2), (3, 9), (3, 10), (3, 11), (3, 18), (3, 21), (3, 23), (3, 24), (3, 25), (3, 27), (3, 29), (3, 30), (3, 31), (3, 35), (3, 39), (3, 40), (3, 46), (3, 50), (3, 51), (3, 52), (3, 58), (3, 60), (3, 61), (3, 66), (3, 68), (3, 71), (3, 79), (3, 83), (3, 84), (3, 85), (3, 86), (3, 90), (3, 95), (3, 96), (3, 97), (3, 100), (3, 101), (3, 102), (3, 257), (3, 259), (3, 261), (3, 278), (3, 280), (3, 281), (3, 282), (3, 284), (3, 285), (3, 298), (3, 299), (3, 300), (3, 301), (3, 313), (3, 315), (3, 319), (3, 320), (3, 321), (3, 322), (3, 323), (3, 324), (3, 327), (3, 331), (3, 332), (3, 333), (3, 334), (3, 337), (3, 338), (3, 339), (3, 340), (3, 351), (3, 353), (3, 359), (3, 360), (3, 361), (3, 369), (3, 371), (3, 372), (3, 373), (3, 375), (3, 376), (3, 377), (3, 378), (3, 381), (3, 382), (3, 386), (3, 389), (3, 390), (3, 393), (3, 394), (3, 395), (3, 397), (3, 398), (3, 400), (3, 401), (3, 404), (3, 405), (3, 411), (3, 413), (3, 414), (3, 419), (3, 420), (3, 429), (3, 431), (3, 432), (3, 435), (3, 436), (3, 438), (3, 441), (3, 451), (3, 452), (3, 455), (3, 456), (3, 475), (3, 488), (3, 492), (3, 493), (3, 495), (3, 506), (3, 521), (3, 545), (3, 546), (3, 551), (3, 561), (3, 562), (3, 574), (3, 575), (3, 576), (3, 594), (3, 595), (3, 597), (3, 602), (3, 603), (3, 652), (3, 661), (3, 744), (3, 745), (3, 746), (3, 817), (3, 1053), (3, 1083), (7, 251), (9, 635), (9, 665), (10, 270), (10, 277), (11, 275), (18, 334), (21, 370), (23, 301), (24, 429), (25, 255), (27, 411), (29, 315), (30, 351), (31, 371), (31, 372), (35, 316), (39, 484), (40, 487), (42, 501), (46, 369), (50, 331), (51, 333), (51, 334), (52, 313), (58, 274), (60, 446), (61, 428), (66, 272), (68, 405), (70, 386), (71, 314), (76, 386), (78, 404), (79, 353), (83, 295), (83, 296), (84, 274), (85, 276), (85, 277), (86, 260), (90, 441), (90, 448), (93, 310), (95, 332), (95, 344), (96, 313), (97, 485), (100, 356), (101, 369), (101, 373), (101, 376), (102, 372), (128, 127), (129, 127), (131, 127), (133, 127), (134, 127), (139, 127), (140, 127), (141, 127), (142, 127), (149, 127), (152, 127), (153, 127), (155, 127), (156, 127), (158, 127), (165, 127), (167, 127), (172, 127), (174, 127), (176, 127), (178, 127), (181, 127), (183, 127), (184, 127), (186, 127), (188, 127), (190, 127), (192, 127), (194, 127), (196, 127), (200, 127), (201, 127), (202, 127), (204, 127), (206, 127), (207, 127), (209, 127), (210, 127), (212, 127), (215, 127), (218, 127), (221, 127), (225, 127), (227, 127), (229, 127), (238, 127), (245, 127), (246, 127), (251, 264), (255, 261), (257, 553), (257, 682), (259, 127), (259, 723), (260, 719), (261, 730), (261, 736), (264, 743), (270, 285), (272, 281), (274, 283), (274, 284), (275, 287), (276, 282), (277, 280), (277, 286), (278, 564), (278, 633), (280, 826), (280, 838), (280, 951), (280, 965), (281, 827), (281, 839), (281, 952), (281, 966), (282, 537), (282, 846), (282, 959), (282, 973), (283, 525), (283, 834), (283, 960), (283, 974), (284, 850), (284, 979), (284, 993), (284, 1074), (285, 851), (285, 866), (285, 980), (285, 994), (286, 857), (286, 873), (286, 985), (286, 999), (287, 858), (287, 874), (287, 986), (287, 1000), (295, 300), (296, 298), (298, 526), (298, 828), (298, 953), (298, 975), (299, 829), (299, 847), (299, 954), (299, 976), (300, 538), (300, 840), (300, 961), (300, 967), (301, 835), (301, 841), (301, 962), (301, 968), (310, 716), (313, 322), (313, 323), (313, 554), (314, 326), (315, 321), (315, 822), (316, 325), (319, 838), (320, 839), (321, 526), (321, 822), (322, 554), (322, 847), (323, 853), (323, 881), (323, 981), (323, 1007), (324, 1008), (324, 1075), (325, 863), (325, 889), (325, 985), (325, 1013), (326, 864), (326, 890), (326, 986), (326, 1014), (327, 783), (327, 907), (331, 338), (331, 817), (332, 340), (332, 555), (333, 339), (333, 823), (334, 337), (334, 343), (334, 816), (337, 816), (337, 846), (338, 525), (338, 817), (339, 823), (339, 840), (340, 555), (340, 841), (343, 855), (343, 979), (344, 856), (344, 892), (344, 980), (344, 1016), (351, 360), (351, 555), (353, 359), (353, 823), (356, 727), (359, 538), (359, 823), (360, 555), (360, 835), (361, 885), (361, 1009), (362, 1010), (362, 1076), (369, 378), (369, 379), (369, 554), (370, 382), (371, 377), (371, 822), (372, 375), (372, 381), (372, 816), (372, 871), (373, 618), (373, 733), (373, 913), (375, 537), (375, 816), (376, 817), (376, 834), (377, 822), (377, 828), (378, 554), (378, 829), (379, 877), (379, 1001), (379, 1007), (379, 1077), (380, 888), (380, 1008), (381, 871), (381, 893), (382, 872), (382, 894), (382, 994), (382, 1016), (386, 574), (386, 740), (386, 909), (389, 395), (389, 557), (390, 393), (390, 818), (393, 818), (393, 1074), (394, 866), (395, 557), (395, 875), (397, 881), (398, 1075), (400, 892), (401, 922), (401, 1062), (404, 521), (404, 913), (405, 414), (405, 821), (411, 575), (411, 912), (413, 873), (414, 821), (414, 874), (419, 889), (420, 890), (428, 437), (429, 576), (429, 770), (431, 850), (432, 851), (435, 885), (436, 1076), (437, 528), (437, 973), (438, 894), (441, 456), (441, 527), (446, 458), (448, 457), (451, 857), (452, 858), (455, 1077), (456, 527), (456, 888), (457, 844), (457, 965), (458, 845), (458, 966), (475, 877), (484, 494), (485, 497), (487, 496), (488, 548), (488, 660), (492, 855), (493, 856), (494, 528), (495, 872), (496, 766), (497, 767), (501, 513), (506, 651), (506, 664), (513, 127), (513, 914), (521, 913), (521, 1029), (525, 127), (525, 974), (526, 127), (526, 975), (527, 976), (528, 127), (528, 973), (537, 127), (537, 959), (538, 127), (538, 961), (545, 665), (546, 548), (548, 127), (548, 660), (551, 553), (553, 127), (553, 682), (554, 946), (555, 948), (557, 945), (561, 657), (562, 564), (564, 127), (564, 633), (574, 909), (574, 1035), (575, 912), (575, 1036), (576, 770), (576, 1033), (594, 602), (594, 723), (594, 760), (594, 764), (594, 765), (595, 127), (595, 603), (595, 618), (595, 736), (597, 731), (597, 732), (602, 636), (602, 638), (602, 640), (602, 641), (602, 684), (602, 685), (602, 686), (602, 687), (602, 688), (602, 689), (603, 127), (618, 733), (618, 789), (618, 913), (631, 127), (631, 152), (633, 127), (633, 212), (635, 127), (635, 210), (636, 631), (636, 647), (638, 645), (638, 651), (640, 647), (641, 645), (645, 127), (645, 651), (647, 127), (647, 631), (649, 127), (649, 176), (651, 127), (651, 140), (651, 174), (652, 649), (652, 657), (657, 127), (657, 649), (660, 127), (660, 231), (661, 664), (664, 127), (664, 651), (665, 127), (665, 635), (674, 127), (674, 142), (682, 127), (682, 134), (682, 180), (684, 682), (684, 695), (685, 694), (685, 696), (686, 674), (686, 693), (687, 694), (688, 695), (689, 693), (693, 127), (693, 674), (694, 127), (694, 696), (695, 127), (695, 682), (696, 127), (696, 165), (716, 783), (716, 807), (719, 127), (719, 907), (723, 127), (723, 902), (727, 729), (729, 789), (729, 808), (730, 127), (730, 913), (731, 826), (732, 827), (733, 238), (736, 127), (736, 909), (740, 1062), (740, 1071), (743, 245), (743, 922), (744, 746), (744, 916), (745, 747), (746, 207), (746, 916), (747, 245), (747, 917), (760, 853), (764, 863), (765, 864), (766, 844), (767, 845), (770, 901), (783, 807), (783, 907), (789, 808), (789, 913), (807, 932), (808, 933), (816, 939), (817, 940), (818, 939), (821, 938), (822, 945), (823, 947), (826, 127), (826, 951), (827, 127), (827, 952), (828, 127), (828, 953), (829, 127), (829, 954), (834, 127), (834, 960), (835, 127), (835, 962), (838, 127), (838, 965), (839, 127), (839, 966), (840, 127), (840, 967), (841, 127), (841, 968), (844, 127), (844, 965), (845, 127), (845, 966), (846, 127), (846, 973), (847, 127), (847, 976), (850, 127), (850, 979), (851, 127), (851, 980), (853, 127), (853, 981), (855, 127), (855, 979), (856, 127), (856, 980), (857, 127), (857, 985), (858, 127), (858, 986), (863, 127), (863, 985), (864, 127), (864, 986), (866, 127), (866, 994), (871, 993), (872, 127), (872, 994), (873, 127), (873, 999), (874, 127), (874, 1000), (875, 127), (877, 127), (877, 1001), (881, 127), (881, 1007), (885, 127), (885, 1009), (888, 127), (888, 1008), (889, 127), (889, 1013), (890, 127), (890, 1014), (892, 127), (892, 1016), (893, 1015), (894, 127), (894, 1016), (901, 246), (902, 127), (907, 127), (907, 177), (909, 127), (912, 127), (913, 127), (913, 147), (914, 245), (916, 127), (917, 245), (922, 195), (922, 245), (932, 128), (933, 152), (938, 184), (939, 184), (939, 212), (940, 192), (945, 200), (945, 210), (946, 194), (947, 210), (948, 194), (951, 127), (951, 156), (952, 127), (952, 139), (953, 127), (953, 156), (954, 127), (954, 139), (959, 127), (959, 178), (960, 127), (960, 221), (961, 127), (961, 178), (962, 127), (962, 221), (965, 127), (965, 149), (965, 206), (966, 127), (966, 218), (966, 227), (967, 127), (967, 206), (968, 127), (968, 218), (973, 127), (973, 158), (973, 229), (974, 127), (974, 172), (975, 127), (975, 158), (976, 127), (976, 172), (976, 229), (979, 127), (979, 129), (979, 153), (980, 127), (980, 133), (980, 181), (981, 127), (981, 181), (985, 127), (985, 183), (985, 196), (986, 127), (986, 155), (986, 204), (993, 127), (993, 188), (993, 209), (994, 127), (994, 201), (994, 215), (999, 127), (999, 131), (1000, 127), (1000, 190), (1001, 127), (1001, 186), (1007, 127), (1007, 176), (1007, 225), (1008, 127), (1008, 141), (1008, 165), (1009, 127), (1009, 165), (1010, 127), (1010, 225), (1013, 127), (1013, 174), (1014, 127), (1014, 140), (1015, 142), (1016, 127), (1016, 140), (1016, 167), (1029, 1079), (1033, 1041), (1035, 1042), (1036, 1043), (1041, 246), (1042, 127), (1043, 127), (1053, 1083), (1062, 922), (1062, 1071), (1071, 1082), (1074, 127), (1074, 993), (1075, 127), (1075, 1008), (1076, 127), (1076, 1010), (1077, 127), (1077, 1007), (1079, 127), (1082, 134), (1083, 202)]),'Exact W3 versus pinned #7481 census')
    pairs_path=ROOT/'frozen-composition/CONTACT7620-PAIRS.json'
    need(sha256(pairs_path.read_bytes()).hexdigest()=='7958d92dcff854704e400e8ac5004ce01433ce1f3ed4193a58cfffe6add3a999','Exact independently frozen candidate-pair manifest')
    pairs=read(pairs_path)
    candidate_routes=routes(word)
    changed=[i for i in old_routes if old_routes[i]!=candidate_routes[i]]
    affected={pair for i in changed for pair in old_routes[i]+candidate_routes[i]}
    splice_changed=[i for i in new_routes if new_routes[i]!=candidate_routes[i]]
    need(splice_changed==[902,1091],'Exact splice route fields')
    affected |= {pair for i in splice_changed for pair in new_routes[i]+candidate_routes[i]}
    need(affected=={tuple(x) for x in pairs['full_validation_pairs']},'Complete fresh candidate affected pairs')
    need(changed==pairs['candidate_changed_fields'],'Fresh changed public fields')
    report=[]
    for a,b in sorted(affected):
        ca,cb=(compiler.canonical_frame(9,tuple(word['frames'][f]))for f in(a,b))
        recipe,_=compiler.lower_child(ca.adjoint().then(cb))
        expected=interpreter.adjoint(interpreter.frame(word['frames'][a],9))+interpreter.frame(word['frames'][b],9)
        actual=interpreter.recipe(recipe)
        interpreter.equal(actual,expected,'Signed Pauli action and absolute phase')
        need(recipe['rank']==len(word['frames'][b])-len(word['frames'][a]),'Exact public ascent rank')
        for x,y in ((actual,expected),(interpreter.adjoint(actual),interpreter.adjoint(expected))):
            for column in range(512):need(interpreter.state(x,column)==interpreter.state(y,column),'Exact forward/adjoint Gaussian column')
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
        need(rejects(lambda:interpreter.equal(interpreter.recipe(bad),expected,'Wrong absolute phase')),'Reject wrong phase')
        report.append({'pair':[a,b],'rank':recipe['rank'],'columns':512,'adjoint_columns':512,'absolute_phase_verified':True})
    return {'all_affected_pairs':report,'changed_public_fields':changed,'wrong_phase_rejected':True}

def run():
    need(__debug__,'Assertions are proof obligations')
    new=read(CANDIDATE/'WORD.json.gz');need(sha256(canonical(new)).hexdigest()==EXPECTED,'Only final short candidate')
    previous=read(SOURCE/'NATIVE-RESULT.json')
    proposal=read(CANDIDATE/'RESULT.json')
    with sources()as(vendor,archive,rank9,bundle,parent,parent_word):
        old=construct(parent_word)
        need(canonical(old)==gzip.decompress((SOURCE/'WORD.json.gz').read_bytes()),'Regenerate frozen #7480 from authenticated #7334 closure')
        need(sha256(canonical(old)).hexdigest()==BASELINE,'Exact source word')
        emitted=[];skip=set(proposal['removed_old_indices'])
        for i,e in enumerate(old['program']):
            if i==proposal['insert_before_old_index']:emitted.extend(proposal['splice'])
            if i not in skip:emitted.append(e)
        incumbent=read(ROOT/'frozen-composition/7481-WORD.json.gz')
        need(incumbent==dict(old,program=emitted),'Rebuild exact #7481 from its predecessor')
        peer=read(ROOT/'frozen-composition/7604-WORD.json.gz')
        need(sha256((ROOT/'frozen-composition/7604-WORD.json.gz').read_bytes()).hexdigest()=='aae5a85746db1abc5145b993e9a9408076f34c53c4bb8040a99b6a39f2685527','Exact open #7604 comparator')
        program=peer['program']
        required={33517:['ADD',1143,757,'-1',3],38584:['MOVE',757,3,595,False],38585:['ADD',757,902,'-1',595],42714:['ADD',757,1557,'-2/3',595],42716:['MOVE',757,595,603,False],42717:['ADD',1255,757,'-1',603]}
        need(all(program[i]==e for i,e in required.items()),'Exact helper757 contacts')
        touches=[i for i in range(33518,42716)if 757 in(program[i][1:3]if program[i][0]in('ADD','COPY')else program[i][1:2])]
        need(touches==[38584,38585,42714],'No intervening read of helper757')
        emitted=[]
        for i,event in enumerate(program):
            if i==33518:emitted.append(['ADD',757,1255,'-1',3])
            if i==42716:emitted.extend([['MOVE',757,3,603,False],['ADD',757,1255,'1',603]])
            elif i not in(38584,38585,42714):emitted.append(event)
        helper_word=dict(peer,program=emitted)
        edits_path=ROOT/'frozen-composition/W2-EDITS.json'
        need(sha256(edits_path.read_bytes()).hexdigest()=='15d784c0515565eeefe40a11817fc47bc87e5f6eb00c83b2f95de670c35d0622','Pinned literal W2 edits')
        edits=read(edits_path)
        need(sha256(canonical(helper_word)).hexdigest()==edits['base_canonical_sha256'],'Exact reconstructed helper757 base')
        rebuilt=list(emitted)
        for edit in reversed(edits['replacements']):
            need(rebuilt[edit['start']:edit['end']]==edit['old'],'Exact old slice')
            rebuilt[edit['start']:edit['end']]=edit['new']
        source7620=read(ROOT/'frozen-composition/7620-WORD.json.gz')
        need(sha256(canonical(source7620)).hexdigest()=='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d','Exact original 7620 source')
        need(source7620==dict(helper_word,program=rebuilt),'Literal original W3 reconstruction and unchanged metadata')
        manifest_path=ROOT/'frozen-composition/CONTACT7620-MANIFEST.json'
        need(sha256(manifest_path.read_bytes()).hexdigest()=='58fd6a8fb76f0dad335abab6973f0ceae29a1c687c47cb2d98d6d0c64e9ed1e7','Exact frozen successor edit manifest')
        manifest=read(manifest_path); changes={e['original_index']:e for e in manifest['edits']}
        need(len(changes)==10 and manifest['source_canonical_sha256']=='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d' and manifest['candidate_canonical_sha256']==EXPECTED,'Exact successor source/candidate edit contract')
        successor=[];origins=[];reverse=[None]*len(rebuilt)
        for i,event in enumerate(rebuilt):
            if i in changes:
                edit=changes[i];need(event==edit['old'],'Exact original splice literal')
                event=edit['new_or_null']
                if event is None:continue
            reverse[i]=len(successor);origins.append(i);successor.append(event)
        need(origins==manifest['candidate_origins'] and reverse==manifest['original_to_candidate'],'Complete successor origin map')
        need(new==dict(helper_word,program=successor),'Exact successor word and unchanged full metadata')
        need({k:v for k,v in new.items() if k!='program'}=={k:v for k,v in incumbent.items() if k!='program'},'Unchanged boundary metadata')
        G=load('producer_native_price_engine',bundle/'gate.py');sys.path.insert(0,str(rank9))
        helper_count=sum(previous['native']['helpers'].values())
        base=module('producer_rank9',rank9/'candidate_gate.py',(
            ('== 1080','== '+str(helper_count)),
            ('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * '+str(helper_count)),
            ('grid.word_run(word), grid.caller_run(caller)','grid.word_run(word, frac=25), grid.caller_run(caller)'),
            ("    exec(compile(src, str(env_path), 'exec'), env.__dict__)",'    assert src.count("(life, peak, owned_count) == (54, 43, 51)") == 1\n    src=src.replace("(life, peak, owned_count) == (54, 43, 51)","(life, peak, owned_count) == (167, 50, 68)")\n    exec(compile(src, str(env_path), \'exec\'), env.__dict__)')))
        I=base.independent(vendor)
        oldN,peerN,N=map(I.native,(old,peer,new))
        sourceN=I.native(source7620)
        reference_path=ROOT/'frozen-composition/7620-NATIVE.json'
        need(sha256(reference_path.read_bytes()).hexdigest()=='151e88d588d254d10fe8c9acc2201991ef8fc166990269f3863f270fffbceb0e','Exact source 7620 native receipt')
        reference=read(reference_path)
        need(reference['status']=='PASS_W3_ADAPTED_COMPLETE_NATIVE' and reference['word_canonical_sha256']=='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d','Source native receipt binding')
        need(normalized(sourceN)==reference['native'] and not sourceN['bad_inputs'],'Fresh original 7620 native inventory')
        need(delta(N['paid'],sourceN['paid'])=={1:-3,2:1,4:-1,5:1},'Exact candidate-versus-7620 native paid delta')
        need(all(N[k]==sourceN[k] for k in ('public','helpers','rises','owned_peak','lifetimes')),'Candidate versus 7620 native boundary')
        need(all(N[k]==peerN[k]for k in('public','helpers','rises','owned_peak','bad_inputs')),'Fixed complete #7604 ownership and target contract')
        need(delta(N['paid'],peerN['paid'])=={1: -15, 2: 77, 3: -148, 4: 54, 5: 9, 6: 6, 8: 1},'Exact additional helper757 native saving')
        need(normalized(oldN)==previous['native'] and not N['bad_inputs'],'Recomputed source inventory and every candidate adjoint input')
        need(all(N[k]==oldN[k]for k in('owned_peak','rises')),'Unchanged complete owned contract')
        need(new['owned_fields']==old['owned_fields']==68,'Unchanged 68 owned labels')
        need(delta(N['helpers'],oldN['helpers'])=={} and delta(N['paid'],oldN['paid'])=={1: -20, 2: 71, 3: -148, 4: 55, 5: 9, 6: 7, 7: 1, 8: 1},'Exact paid delta and all helper targets')
        need(N['lifetimes']==167 and N['owned_peak']==50 and len(new['program'])==len(old['program'])+716,'Actual instruction and lifetime counts')
        checkpoint('authenticated source, complete frame and adjoint checks',{'native':N})
        derived,_=derive(new)
        need(derived['odd_scale']==1125 and derived['fractional_bits']==25,'Fresh minimal common grid')
        audit=module('producer_forward',archive/'audit_native.py',(('2**24','2**25'),('25 - (abs(value) & -abs(value)).bit_length()','26 - (abs(value) & -abs(value)).bit_length()')))
        forward,grid=audit.replay(new,list(enumerate(new['program'])),set())
        forward_receipt=forward_endpoint(new,forward[0])
        forward_receipt['copy_guards_checked']=len(forward[3])
        forward_receipt['owned_clear_rows_checked']=len(forward[2])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Fresh exact grid and owned ascent')
        need(grid['dyadic_height']==derived['fractional_bits'] and grid['maximum_scaled_mass']==derived['scaled_maximum_mass'],'Independent integer and rational grid agreement')
        checkpoint('complete forward grid, COPY guards and all public/owned endpoints',{'grid':grid,'derived_grid':derived})
        caller_path=rank9/'dyadic/CALLER.json';C=read(caller_path)
        need(sha256(caller_path.read_bytes()).hexdigest()==G.CALLER,'Exact 18-stage ingredient caller')
        symbolic=I.caller(C)
        need(not symbolic['bad_outputs'] and normalized(symbolic)==previous['caller'],'Full retained ingredient caller')
        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)
        source_invoice=I.invoices(source7620,C,sourceN)
        need(normalized(source_invoice)==reference['invoice'],'Fresh complete 7620 native ingredient invoice')
        need(normalized(before)==previous['invoice'],'Recomputed complete source ingredient invoice')
        unadjusted=I.ordinary(old,C,oldN);ordinary=I.ordinary(new,C,N)
        routes=previous['ordinary']['caller_items']['B']['fused_routes'];route_delta=routes-unadjusted['caller_items']['B']['fused_routes']
        surcharge=0
        for e in C['events']:
            if e[0]=='B'and e[1]in('ADD','SCALE'):
                q=Q(e[4]if e[1]=='ADD'else e[3]);a,d=abs(q.numerator),q.denominator
                surcharge+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count()if e[1]=='ADD'else 0))
        surcharge*=len(C['types']['B']['ports'])
        need(surcharge==previous['ordinary']['extra_B_scalar_surcharge'],'Fresh caller scalar surcharge')
        need(unadjusted['conservative_total']+route_delta+surcharge==previous['ordinary']['conservative_total'],'Complete source ordinary bill')
        ordinary['caller_items']['B']['fused_routes']=routes
        for k in('caller_total','raw_upper','conservative_total'):ordinary[k]+=route_delta
        ordinary['extra_B_scalar_surcharge']=surcharge;ordinary['conservative_total']+=surcharge
        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Full ordinary allowance')
        source_ordinary=I.ordinary(source7620,C,sourceN)
        source_ordinary['caller_items']['B']['fused_routes']=routes
        for k in ('caller_total','raw_upper','conservative_total'):source_ordinary[k]+=route_delta
        source_ordinary['extra_B_scalar_surcharge']=surcharge;source_ordinary['conservative_total']+=surcharge
        source_ordinary['margin_to_billion']=10**9-source_ordinary['conservative_total']
        need(source_ordinary['margin_to_billion']>0,'Source complete ordinary allowance')
        need(source_ordinary['conservative_total']==863312128,'Source 7620 ingredient ordinary total')
        need(normalized(source_ordinary)==reference['ordinary'],'Fresh source ordinary with identical caller route and scalar surcharge')
        gate,price=G.exact_price(vendor,archive,before,invoice,previous)
        (HERE/'INGREDIENT-PRICE.json').write_text(json.dumps(normalized({'before':before,'after':invoice,'gate':gate,'price':price,'ordinary':ordinary}),indent=2)+'\n')
        manifest=read(vendor/'INDEPENDENT-SOURCES.json');P=load('producer_bit_binding',archive/'verify.py');P.bit_binding(I,manifest)
        source_gate,source_price=G.exact_price(vendor,archive,before,source_invoice,previous)
        source_precision=base.precision(vendor,source7620,C,source_gate,manifest)
        need(normalized(source_precision)==reference['precision'],'Fresh full 7620 precision equals deterministic pinned reference')
        precision=base.precision(vendor,new,C,gate,manifest)
        need(precision['word']['odd_scale_lcm']==1125 and precision['word']['dyadic_height']==25,'Fresh ingredient precision')
        checkpoint('complete ingredient invoices, both directed prices, all outer gates and precision',{'gate_claim':gate['claim'],'ordinary':ordinary['conservative_total'],'context_c':precision['context_c']})
        chart_receipt=charts(vendor,new)
        controls={}
        for name,event in(
            ('doubled_early_encoding',['ADD',1455,485,'2/3',3]),
            ('doubled_late_decoding',['ADD',1455,485,'-2/3',724]),
            ('doubled_824_compensation',['ADD',824,54,'-1',721]),
            ('doubled_1438_restoration',['ADD',1438,1439,'1',127])):
            need(new['program'].count(event)==1,'Unique producer correction')
            controls[name]=bool(I.native(new,mutant=new['program'].index(event))['bad_inputs'])
        bad=deepcopy(new);i=bad['program'].index(['MOVE',757,3,603,False]);bad['program'][i][2]=595
        controls['wrong_helper757_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['program'].remove(['MOVE',757,3,603,False])
        controls['missing_helper757_paid_move']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721
        controls['wrong_move_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['final'][485]=721
        controls['wrong_output_frame']=rejects(lambda:I.native(bad))
        owned=module('producer_owned_census',vendor/'retained/query-only-precision-envelope/envelopes.py',(('(life, peak, owned_count) == (54, 43, 51)','(life, peak, owned_count) == (167, 50, 68)'),))
        need(owned.validate_word(new)['lifetimes']==167,'Fresh owned census from envelope validator')
        bad=deepcopy(new);bad['program']=[['INIT',1501,724],['CLEAR',1501,724]]+bad['program']
        controls['extra_uncharged_owned_lifetime']=rejects(lambda:owned.validate_word(bad))
        grid_engine=module('producer_grid_controls',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        controls['insufficient_odd_grid']=rejects(lambda:grid_engine.word_run(new,375,25))
        controls['insufficient_fractional_grid']=rejects(lambda:grid_engine.word_run(new,1125,24))
        def candidate_rejected(mutated):
            try:
                result=I.native(mutated)
            except (ValueError,AssertionError,KeyError,IndexError):
                return True
            return bool(result['bad_inputs'])
        contact=['ADD',1091,902,'1/2',373]
        need(new['program'].count(contact)==1,'Unique 902/1091 candidate contact')
        bad=deepcopy(new);i=bad['program'].index(contact);bad['program'][i][2]=1093
        controls['wrong_902_1091_contact_source']=candidate_rejected(bad)
        move=['MOVE',902,3,373,False]
        need(new['program'].count(move)==1,'Unique 902 paid movement')
        bad=deepcopy(new);bad['program'].remove(move)
        controls['missing_902_paid_move']=candidate_rejected(bad)
        need(all(controls.values()),'Every corruption control rejected')
        physical_checks=[]
        with tempfile.TemporaryDirectory(prefix='producer-physical-')as tmp:
            path=Path(tmp)/'word.json.gz';path.write_bytes(gzip.compress(canonical(new),mtime=0))
            for command,args in[(vendor/'frozen/verify_host3_odd.py',[path,'1125']),(vendor/'frozen/physical.py',[path,vendor/'frozen/clifford_exact.py','1000000009','11'])]:
                with(HERE/(command.name+'.log')).open('w')as stream:
                    subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(ROOT/'isolated/pycache'),str(command),*map(str,args)],stdout=stream,stderr=subprocess.STDOUT,check=True)
                physical_checks.append(command.name)
                print((HERE/(command.name+'.log')).read_text(),end='',flush=True)
            engine=module('producer_signed_routes',rank9/'physical_child.py',(('cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066',EXPECTED),))
            capture=io.StringIO()
            with contextlib.redirect_stdout(capture):engine.main(path,vendor/'data/caller.json',caller_path)
            signed_routes=json.loads(capture.getvalue())
            need(signed_routes['status']=='PASS_PHYSICAL_RANK9_ALGEBRA'and signed_routes['paid_calls']==32,'Signed physical fields')
            need(1000*sum(len(row['caller_fields'])*row['ordinary_elementary_units']for row in signed_routes['bindings'])==routes,'Actual signed-route elementary charge')
        checkpoint('all affected Gaussian columns and absolute phase, finite physical replay and signed routes')
        return normalized(dict(status='PASS_CONTACT7620_COMPLETE_NATIVE',source_head='b1356c84a0733843ce59855f02511c49c6a44133',predecessor_source_head='58a9d052143f5d85295ed2d0163591c47f89a331',source_word_canonical_sha256=BASELINE,word_canonical_sha256=EXPECTED,native=N,source_native=sourceN,source_invoice=source_invoice,forward=forward_receipt,grid=grid,derived_grid=derived,caller=symbolic,invoice=invoice,ordinary=ordinary,paired_ordinary={'source_7620':source_ordinary,'candidate':ordinary,'formula':'same fresh 18-stage ingredient caller, route adjustment and scalar surcharge','common_U_incremental_tariff':'UNRESOLVED_NOT_INCLUDED'},gate=gate,price=price,precision=precision,paired_precision={'source_7620':source_precision,'candidate':precision,'source_gate':source_gate,'source_price':source_price,'scope':'Fresh native ingredient envelopes on both words; signed precision/tape and common U service are separate.'},charts=chart_receipt,controls=controls,physical_checks=physical_checks,signed_routes=signed_routes,adapter=PATCHES,timings=TIMINGS,limitations=['Five inherited framework assumptions remain.','Source-aware retained engines are not independent human/formal acceptance.','The complete 17-stage signed application is checked separately.','Common U is a stronger unimplemented service; changed private states and its full numerical tariff remain unresolved.']))

if __name__=='__main__':
    STARTED=time.time();result=run()
    (HERE/'NATIVE-RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],result['price']['claim_decimal'],flush=True)
