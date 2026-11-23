/- Generated projection of the pinned PR531 hosted controller.
Original construction: icekylinx and credited predecessors; Apache-2.0.
Projection/proofs: Rohan Arun with OpenAI Codex assistance. -/
import PR531DataWindows
import BorrowSchedule
namespace OwnerTransport.PR531Controller
open OwnerTable OwnerSeparation PR531Table PR531DataWindows
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def eventsPart0 : Array (BorrowSchedule.Event) := #[
  ⟨some 0, [0], [], some (0, 0), false⟩,
  ⟨some 1, [0], [], some (0, 1), false⟩,
  ⟨some 0, [0], [], some (1, 2), false⟩,
  ⟨some 0, [1], [0, 2], none, false⟩,
  ⟨some 0, [1, 0], [], none, false⟩,
  ⟨some 2, [0], [], some (0, 3), false⟩,
  ⟨some 1, [0], [], some (1, 4), false⟩,
  ⟨some 1, [1], [0, 2], none, false⟩,
  ⟨some 1, [1, 0], [], none, false⟩,
  ⟨some 0, [0], [], some (2, 5), false⟩,
  ⟨some 0, [1], [1, 3], none, false⟩,
  ⟨some 0, [1, 0], [], none, false⟩,
  ⟨some 3, [0], [], some (0, 6), false⟩,
  ⟨some 2, [0], [], some (1, 7), false⟩,
  ⟨some 2, [1], [0, 2], none, false⟩,
  ⟨some 2, [1, 0], [], none, false⟩,
  ⟨some 1, [0], [], some (2, 8), false⟩,
  ⟨some 1, [1], [1, 3], none, false⟩,
  ⟨some 1, [1, 0], [], none, false⟩,
  ⟨some 0, [1], [], some (3, 9), false⟩,
  ⟨some 0, [2], [4, 6], none, false⟩,
  ⟨some 0, [2, 1], [], none, false⟩,
  ⟨some 4, [0], [], some (0, 10), false⟩,
  ⟨some 3, [0], [], some (1, 11), false⟩,
  ⟨some 3, [1], [0, 2], none, false⟩,
  ⟨some 3, [1, 0], [], none, false⟩,
  ⟨some 2, [0], [], some (2, 12), false⟩,
  ⟨some 2, [1], [1, 3], none, false⟩,
  ⟨some 2, [1, 0], [], none, false⟩,
  ⟨some 1, [1], [], some (3, 13), false⟩,
  ⟨some 1, [2], [4, 6], none, false⟩,
  ⟨some 1, [2, 1], [], none, false⟩]

def eventsPart1 : Array (BorrowSchedule.Event) := #[
  ⟨some 0, [1], [], some (4, 14), false⟩,
  ⟨some 0, [2], [5, 7], none, false⟩,
  ⟨some 0, [2, 1], [], none, false⟩,
  ⟨some 5, [0], [], some (0, 15), false⟩,
  ⟨some 4, [0], [], some (1, 16), false⟩,
  ⟨some 4, [1], [0, 2], none, false⟩,
  ⟨some 4, [1, 0], [], none, false⟩,
  ⟨some 3, [0], [], some (2, 17), false⟩,
  ⟨some 3, [1], [1, 3], none, false⟩,
  ⟨some 3, [1, 0], [], none, false⟩,
  ⟨some 2, [1], [], some (3, 18), false⟩,
  ⟨some 2, [2], [4, 6], none, false⟩,
  ⟨some 2, [2, 1], [], none, false⟩,
  ⟨some 1, [1], [], some (4, 19), false⟩,
  ⟨some 1, [2], [5, 7], none, false⟩,
  ⟨some 1, [2, 1], [], none, false⟩,
  ⟨some 0, [2], [], some (5, 20), false⟩,
  ⟨some 0, [3], [8, 10], none, false⟩,
  ⟨some 0, [3, 2], [], none, false⟩,
  ⟨some 6, [0], [], some (0, 21), false⟩,
  ⟨some 5, [0], [], some (1, 22), false⟩,
  ⟨some 5, [1], [0, 2], none, false⟩,
  ⟨some 5, [1, 0], [], none, false⟩,
  ⟨some 4, [0], [], some (2, 23), false⟩,
  ⟨some 4, [1], [1, 3], none, false⟩,
  ⟨some 4, [1, 0], [], none, false⟩,
  ⟨some 3, [1], [], some (3, 24), false⟩,
  ⟨some 3, [2], [4, 6], none, false⟩,
  ⟨some 3, [2, 1], [], none, false⟩,
  ⟨some 2, [1], [], some (4, 25), false⟩,
  ⟨some 2, [2], [5, 7], none, false⟩,
  ⟨some 2, [2, 1], [], none, false⟩]

def eventsPart2 : Array (BorrowSchedule.Event) := #[
  ⟨some 1, [2], [], some (5, 26), false⟩,
  ⟨some 1, [3], [8, 10], none, false⟩,
  ⟨some 1, [3, 2], [], none, false⟩,
  ⟨some 7, [0], [], some (0, 27), false⟩,
  ⟨some 0, [2], [], some (6, 28), false⟩,
  ⟨some 0, [3], [9, 11], none, false⟩,
  ⟨some 0, [3, 2], [], none, false⟩,
  ⟨some 6, [0], [], some (1, 29), false⟩,
  ⟨some 6, [1], [0, 2], none, false⟩,
  ⟨some 6, [1, 0], [], none, false⟩,
  ⟨some 5, [0], [], some (2, 30), false⟩,
  ⟨some 5, [1], [1, 3], none, false⟩,
  ⟨some 5, [1, 0], [], none, false⟩,
  ⟨some 4, [1], [], some (3, 31), false⟩,
  ⟨some 4, [2], [4, 6], none, false⟩,
  ⟨some 4, [2, 1], [], none, false⟩,
  ⟨some 3, [1], [], some (4, 32), false⟩,
  ⟨some 3, [2], [5, 7], none, false⟩,
  ⟨some 3, [2, 1], [], none, false⟩,
  ⟨some 2, [2], [], some (5, 33), false⟩,
  ⟨some 2, [3], [8, 10], none, false⟩,
  ⟨some 2, [3, 2], [], none, false⟩,
  ⟨some 1, [2], [], some (6, 34), false⟩,
  ⟨some 1, [3], [9, 11], none, false⟩,
  ⟨some 1, [3, 2], [], none, false⟩,
  ⟨some 7, [0], [], some (1, 35), false⟩,
  ⟨some 7, [1], [0, 2], none, false⟩,
  ⟨some 7, [1, 0], [], none, false⟩,
  ⟨some 0, [3], [], some (7, 36), false⟩,
  ⟨some 6, [0], [], some (2, 37), false⟩,
  ⟨some 6, [1], [1, 3], none, false⟩,
  ⟨some 6, [1, 0], [], none, false⟩]

def eventsPart3 : Array (BorrowSchedule.Event) := #[
  ⟨some 5, [1], [], some (3, 38), false⟩,
  ⟨some 5, [2], [4, 6], none, false⟩,
  ⟨some 5, [2, 1], [], none, false⟩,
  ⟨some 4, [1], [], some (4, 39), false⟩,
  ⟨some 4, [2], [5, 7], none, false⟩,
  ⟨some 4, [2, 1], [], none, false⟩,
  ⟨some 3, [2], [], some (5, 40), false⟩,
  ⟨some 3, [3], [8, 10], none, false⟩,
  ⟨some 3, [3, 2], [], none, false⟩,
  ⟨some 2, [2], [], some (6, 41), false⟩,
  ⟨some 2, [3], [9, 11], none, false⟩,
  ⟨some 2, [3, 2], [], none, false⟩,
  ⟨some 1, [3], [], some (7, 42), false⟩,
  ⟨some 7, [0], [], some (2, 43), false⟩,
  ⟨some 7, [1], [1, 3], none, false⟩,
  ⟨some 7, [1, 0], [], none, false⟩,
  ⟨some 0, [3], [], some (8, 44), false⟩,
  ⟨some 0, [0], [12, 13], none, false⟩,
  ⟨some 0, [1], [14, 15], none, false⟩,
  ⟨some 0, [2], [16, 17], none, false⟩,
  ⟨some 0, [3], [18, 19], none, false⟩,
  ⟨some 0, [2, 3], [], none, false⟩,
  ⟨some 0, [1, 2], [], none, false⟩,
  ⟨some 0, [0, 1], [], none, false⟩,
  ⟨some 0, [], [], none, true⟩,
  ⟨some 0, [], [], none, true⟩,
  ⟨some 6, [1], [], some (3, 45), false⟩,
  ⟨some 6, [2], [4, 6], none, false⟩,
  ⟨some 6, [2, 1], [], none, false⟩,
  ⟨some 5, [1], [], some (4, 46), false⟩,
  ⟨some 5, [2], [5, 7], none, false⟩,
  ⟨some 5, [2, 1], [], none, false⟩]

def eventsPart4 : Array (BorrowSchedule.Event) := #[
  ⟨some 4, [2], [], some (5, 47), false⟩,
  ⟨some 4, [3], [8, 10], none, false⟩,
  ⟨some 4, [3, 2], [], none, false⟩,
  ⟨some 3, [2], [], some (6, 48), false⟩,
  ⟨some 3, [3], [9, 11], none, false⟩,
  ⟨some 3, [3, 2], [], none, false⟩,
  ⟨some 2, [3], [], some (7, 49), false⟩,
  ⟨some 1, [3], [], some (8, 50), false⟩,
  ⟨some 1, [0], [12, 13], none, false⟩,
  ⟨some 1, [1], [14, 15], none, false⟩,
  ⟨some 1, [2], [16, 17], none, false⟩,
  ⟨some 1, [3], [18, 19], none, false⟩,
  ⟨some 1, [2, 3], [], none, false⟩,
  ⟨some 1, [1, 2], [], none, false⟩,
  ⟨some 1, [0, 1], [], none, false⟩,
  ⟨some 1, [], [], none, true⟩,
  ⟨some 1, [], [], none, true⟩,
  ⟨some 7, [1], [], some (3, 51), false⟩,
  ⟨some 7, [2], [4, 6], none, false⟩,
  ⟨some 7, [2, 1], [], none, false⟩,
  ⟨some 6, [1], [], some (4, 52), false⟩,
  ⟨some 6, [2], [5, 7], none, false⟩,
  ⟨some 6, [2, 1], [], none, false⟩,
  ⟨some 5, [2], [], some (5, 53), false⟩,
  ⟨some 5, [3], [8, 10], none, false⟩,
  ⟨some 5, [3, 2], [], none, false⟩,
  ⟨some 4, [2], [], some (6, 54), false⟩,
  ⟨some 4, [3], [9, 11], none, false⟩,
  ⟨some 4, [3, 2], [], none, false⟩,
  ⟨some 3, [3], [], some (7, 55), false⟩,
  ⟨some 2, [3], [], some (8, 56), false⟩,
  ⟨some 2, [0], [12, 13], none, false⟩]

def eventsPart5 : Array (BorrowSchedule.Event) := #[
  ⟨some 2, [1], [14, 15], none, false⟩,
  ⟨some 2, [2], [16, 17], none, false⟩,
  ⟨some 2, [3], [18, 19], none, false⟩,
  ⟨some 2, [2, 3], [], none, false⟩,
  ⟨some 2, [1, 2], [], none, false⟩,
  ⟨some 2, [0, 1], [], none, false⟩,
  ⟨some 2, [], [], none, true⟩,
  ⟨some 2, [], [], none, true⟩,
  ⟨some 7, [1], [], some (4, 57), false⟩,
  ⟨some 7, [2], [5, 7], none, false⟩,
  ⟨some 7, [2, 1], [], none, false⟩,
  ⟨some 6, [2], [], some (5, 58), false⟩,
  ⟨some 6, [3], [8, 10], none, false⟩,
  ⟨some 6, [3, 2], [], none, false⟩,
  ⟨some 5, [2], [], some (6, 59), false⟩,
  ⟨some 5, [3], [9, 11], none, false⟩,
  ⟨some 5, [3, 2], [], none, false⟩,
  ⟨some 4, [3], [], some (7, 60), false⟩,
  ⟨some 3, [3], [], some (8, 61), false⟩,
  ⟨some 3, [0], [12, 13], none, false⟩,
  ⟨some 3, [1], [14, 15], none, false⟩,
  ⟨some 3, [2], [16, 17], none, false⟩,
  ⟨some 3, [3], [18, 19], none, false⟩,
  ⟨some 3, [2, 3], [], none, false⟩,
  ⟨some 3, [1, 2], [], none, false⟩,
  ⟨some 3, [0, 1], [], none, false⟩,
  ⟨some 3, [], [], none, true⟩,
  ⟨some 3, [], [], none, true⟩,
  ⟨some 7, [2], [], some (5, 62), false⟩,
  ⟨some 7, [3], [8, 10], none, false⟩,
  ⟨some 7, [3, 2], [], none, false⟩,
  ⟨some 6, [2], [], some (6, 63), false⟩]

def eventsPart6 : Array (BorrowSchedule.Event) := #[
  ⟨some 6, [3], [9, 11], none, false⟩,
  ⟨some 6, [3, 2], [], none, false⟩,
  ⟨some 5, [3], [], some (7, 64), false⟩,
  ⟨some 4, [3], [], some (8, 65), false⟩,
  ⟨some 4, [0], [12, 13], none, false⟩,
  ⟨some 4, [1], [14, 15], none, false⟩,
  ⟨some 4, [2], [16, 17], none, false⟩,
  ⟨some 4, [3], [18, 19], none, false⟩,
  ⟨some 4, [2, 3], [], none, false⟩,
  ⟨some 4, [1, 2], [], none, false⟩,
  ⟨some 4, [0, 1], [], none, false⟩,
  ⟨some 4, [], [], none, true⟩,
  ⟨some 4, [], [], none, true⟩,
  ⟨some 7, [2], [], some (6, 66), false⟩,
  ⟨some 7, [3], [9, 11], none, false⟩,
  ⟨some 7, [3, 2], [], none, false⟩,
  ⟨some 6, [3], [], some (7, 67), false⟩,
  ⟨some 5, [3], [], some (8, 68), false⟩,
  ⟨some 5, [0], [12, 13], none, false⟩,
  ⟨some 5, [1], [14, 15], none, false⟩,
  ⟨some 5, [2], [16, 17], none, false⟩,
  ⟨some 5, [3], [18, 19], none, false⟩,
  ⟨some 5, [2, 3], [], none, false⟩,
  ⟨some 5, [1, 2], [], none, false⟩,
  ⟨some 5, [0, 1], [], none, false⟩,
  ⟨some 5, [], [], none, true⟩,
  ⟨some 5, [], [], none, true⟩,
  ⟨some 7, [3], [], some (7, 69), false⟩,
  ⟨some 6, [3], [], some (8, 70), false⟩,
  ⟨some 6, [0], [12, 13], none, false⟩,
  ⟨some 6, [1], [14, 15], none, false⟩,
  ⟨some 6, [2], [16, 17], none, false⟩]

def eventsPart7 : Array (BorrowSchedule.Event) := #[
  ⟨some 6, [3], [18, 19], none, false⟩,
  ⟨some 6, [2, 3], [], none, false⟩,
  ⟨some 6, [1, 2], [], none, false⟩,
  ⟨some 6, [0, 1], [], none, false⟩,
  ⟨some 6, [], [], none, true⟩,
  ⟨some 6, [], [], none, true⟩,
  ⟨some 7, [3], [], some (8, 71), false⟩,
  ⟨some 7, [0], [12, 13], none, false⟩,
  ⟨some 7, [1], [14, 15], none, false⟩,
  ⟨some 7, [2], [16, 17], none, false⟩,
  ⟨some 7, [3], [18, 19], none, false⟩,
  ⟨some 7, [2, 3], [], none, false⟩,
  ⟨some 7, [1, 2], [], none, false⟩,
  ⟨some 7, [0, 1], [], none, false⟩,
  ⟨some 7, [], [], none, true⟩,
  ⟨some 7, [], [], none, true⟩,
  ⟨none, [], [], none, true⟩,
  ⟨none, [], [], none, true⟩]

def eventsBlock (block : Nat) : Array (BorrowSchedule.Event) := (if block < 4 then (if block < 2 then (if block < 1 then eventsPart0 else eventsPart1) else (if block < 3 then eventsPart2 else eventsPart3)) else (if block < 6 then (if block < 5 then eventsPart4 else eventsPart5) else (if block < 7 then eventsPart6 else eventsPart7)))

def events (i : Nat) : BorrowSchedule.Event := ((eventsBlock (i / 32))[i % 32]?).getD default

def positionsPart0 : Array (Nat) := #[
  1,
  2,
  3,
  6,
  7,
  10,
  13,
  14,
  17,
  20,
  23,
  24,
  27,
  30,
  33,
  36,
  37,
  40,
  43,
  46,
  49,
  52,
  53,
  56,
  59,
  62,
  65,
  68,
  69,
  72,
  75,
  78]

def positionsPart1 : Array (Nat) := #[
  81,
  84,
  87,
  90,
  93,
  94,
  97,
  100,
  103,
  106,
  109,
  110,
  113,
  123,
  126,
  129,
  132,
  135,
  136,
  146,
  149,
  152,
  155,
  158,
  159,
  169,
  172,
  175,
  178,
  179,
  189,
  192]

def positionsPart2 : Array (Nat) := #[
  195,
  196,
  206,
  209,
  210,
  220,
  221,
  231]

def positionsBlock (block : Nat) : Array (Nat) := (if block < 1 then positionsPart0 else (if block < 2 then positionsPart1 else positionsPart2))

def positions (i : Nat) : Nat := ((positionsBlock (i / 32))[i % 32]?).getD default

def boundsPart0 : Array (Nat × Nat) := #[
  (0, 4),
  (5, 11),
  (0, 4),
  (5, 11),
  (0, 21),
  (22, 34),
  (0, 21),
  (22, 34),
  (0, 50),
  (51, 70),
  (0, 50),
  (51, 70),
  (12, 114),
  (12, 114),
  (35, 115),
  (35, 115),
  (71, 116),
  (71, 116),
  (0, 8),
  (9, 18),
  (0, 8),
  (9, 18),
  (0, 31),
  (32, 47),
  (0, 31),
  (32, 47),
  (0, 66),
  (67, 88),
  (0, 66),
  (67, 88),
  (19, 137),
  (19, 137)]

def boundsPart1 : Array (Nat × Nat) := #[
  (48, 138),
  (48, 138),
  (89, 139),
  (89, 139),
  (0, 15),
  (16, 28),
  (0, 15),
  (16, 28),
  (0, 44),
  (45, 63),
  (0, 44),
  (45, 63),
  (0, 85),
  (86, 107),
  (0, 85),
  (86, 107),
  (29, 160),
  (29, 160),
  (64, 161),
  (64, 161),
  (108, 162),
  (108, 162),
  (0, 25),
  (26, 41),
  (0, 25),
  (26, 41),
  (0, 60),
  (61, 82),
  (0, 60),
  (61, 82),
  (0, 104),
  (105, 133)]

def boundsPart2 : Array (Nat × Nat) := #[
  (0, 104),
  (105, 133),
  (42, 180),
  (42, 180),
  (83, 181),
  (83, 181),
  (134, 182),
  (134, 182),
  (0, 38),
  (39, 57),
  (0, 38),
  (39, 57),
  (0, 79),
  (80, 101),
  (0, 79),
  (80, 101),
  (0, 130),
  (131, 156),
  (0, 130),
  (131, 156),
  (58, 197),
  (58, 197),
  (102, 198),
  (102, 198),
  (157, 199),
  (157, 199),
  (0, 54),
  (55, 76),
  (0, 54),
  (55, 76),
  (0, 98),
  (99, 127)]

def boundsPart3 : Array (Nat × Nat) := #[
  (0, 98),
  (99, 127),
  (0, 153),
  (154, 176),
  (0, 153),
  (154, 176),
  (77, 211),
  (77, 211),
  (128, 212),
  (128, 212),
  (177, 213),
  (177, 213),
  (0, 73),
  (74, 95),
  (0, 73),
  (74, 95),
  (0, 124),
  (125, 150),
  (0, 124),
  (125, 150),
  (0, 173),
  (174, 193),
  (0, 173),
  (174, 193),
  (96, 222),
  (96, 222),
  (151, 223),
  (151, 223),
  (194, 224),
  (194, 224),
  (0, 91),
  (92, 111)]

def boundsPart4 : Array (Nat × Nat) := #[
  (0, 91),
  (92, 111),
  (0, 147),
  (148, 170),
  (0, 147),
  (148, 170),
  (0, 190),
  (191, 207),
  (0, 190),
  (191, 207),
  (112, 232),
  (112, 232),
  (171, 233),
  (171, 233),
  (208, 234),
  (208, 234)]

def boundsBlock (block : Nat) : Array (Nat × Nat) := (if block < 2 then (if block < 1 then boundsPart0 else boundsPart1) else (if block < 3 then boundsPart2 else (if block < 4 then boundsPart3 else boundsPart4)))

def bounds (i : Nat) : Nat × Nat := ((boundsBlock (i / 32))[i % 32]?).getD default

def trace : BorrowSchedule.Trace where
  count := 242
  event := fun p => events (p - 1)
  callPosition := positions
  bounds := bounds

theorem call_certificate :
    checkRange (BorrowSchedule.checkCall witness trace stagePair) 0 72 = true := by decide

theorem window_chunk_0 : checkRange (BorrowSchedule.checkWindow witness trace) 0 18 = true := by decide
theorem window_chunk_1 : checkRange (BorrowSchedule.checkWindow witness trace) 18 18 = true := by decide
theorem window_chunk_2 : checkRange (BorrowSchedule.checkWindow witness trace) 36 18 = true := by decide
theorem window_chunk_3 : checkRange (BorrowSchedule.checkWindow witness trace) 54 18 = true := by decide
theorem window_chunk_4 : checkRange (BorrowSchedule.checkWindow witness trace) 72 18 = true := by decide
theorem window_chunk_5 : checkRange (BorrowSchedule.checkWindow witness trace) 90 18 = true := by decide
theorem window_chunk_6 : checkRange (BorrowSchedule.checkWindow witness trace) 108 18 = true := by decide
theorem window_chunk_7 : checkRange (BorrowSchedule.checkWindow witness trace) 126 18 = true := by decide

theorem window_chunks (r : Nat) (h : r < 8) :
    checkRange (BorrowSchedule.checkWindow witness trace) (r * 18) 18 = true := by
  match r with
  | 0 => exact window_chunk_0
  | 1 => exact window_chunk_1
  | 2 => exact window_chunk_2
  | 3 => exact window_chunk_3
  | 4 => exact window_chunk_4
  | 5 => exact window_chunk_5
  | 6 => exact window_chunk_6
  | 7 => exact window_chunk_7
  | n + 8 => omega

theorem separation_chunk_0 : checkRange (BorrowSchedule.checkSeparations witness trace) 0 18 = true := by decide
theorem separation_chunk_1 : checkRange (BorrowSchedule.checkSeparations witness trace) 18 18 = true := by decide
theorem separation_chunk_2 : checkRange (BorrowSchedule.checkSeparations witness trace) 36 18 = true := by decide
theorem separation_chunk_3 : checkRange (BorrowSchedule.checkSeparations witness trace) 54 18 = true := by decide
theorem separation_chunk_4 : checkRange (BorrowSchedule.checkSeparations witness trace) 72 18 = true := by decide
theorem separation_chunk_5 : checkRange (BorrowSchedule.checkSeparations witness trace) 90 18 = true := by decide
theorem separation_chunk_6 : checkRange (BorrowSchedule.checkSeparations witness trace) 108 18 = true := by decide
theorem separation_chunk_7 : checkRange (BorrowSchedule.checkSeparations witness trace) 126 18 = true := by decide

theorem separation_chunks (r : Nat) (h : r < 8) :
    checkRange (BorrowSchedule.checkSeparations witness trace) (r * 18) 18 = true := by
  match r with
  | 0 => exact separation_chunk_0
  | 1 => exact separation_chunk_1
  | 2 => exact separation_chunk_2
  | 3 => exact separation_chunk_3
  | 4 => exact separation_chunk_4
  | 5 => exact separation_chunk_5
  | 6 => exact separation_chunk_6
  | 7 => exact separation_chunk_7
  | n + 8 => omega

/-- Calls, exact borrowing windows, and same-lane window separation are certified. -/
theorem accepted : BorrowSchedule.Accepted witness trace stagePair := by
  refine ⟨?_, ?_, ?_⟩
  · intro t ht
    exact range_sound _ 0 72 t call_certificate (by omega) ht
  · intro g hg
    exact chunks_sound (BorrowSchedule.checkWindow witness trace) 18 8
      (by decide) window_chunks g hg
  · intro g hg
    exact chunks_sound (BorrowSchedule.checkSeparations witness trace) 18 8
      (by decide) separation_chunks g hg

/-- The controller establishes the declared exclusion from active data. -/
theorem controller_windows_avoid_data : WindowsAvoidData witness stagePair :=
  BorrowSchedule.windows_avoid_data witness trace stagePair accepted

/-- Each selected window has its traced deadline, untouched interior and exact call set. -/
theorem every_window_realized (g : Nat) (hg : g < BorrowSchedule.windowCount witness) :
    BorrowSchedule.WindowFacts witness trace g :=
  BorrowSchedule.accepted_window witness trace stagePair accepted g hg

/-- Two pending children of the same physical lane have separated windows. -/
theorem same_lane_windows_separated (g h : Nat)
    (hg : g < BorrowSchedule.windowCount witness) (hh : h < BorrowSchedule.windowCount witness) :
    BorrowSchedule.Separate witness trace g h :=
  BorrowSchedule.accepted_separation witness trace stagePair accepted g h hg hh

end OwnerTransport.PR531Controller
