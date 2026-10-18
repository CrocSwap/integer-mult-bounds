/-
Copyright (c) 2026 Andrey Mas and contributors.
SPDX-License-Identifier: Apache-2.0
P112 numerical instance of the unchanged PR1497/PR1610 bridge.
SOURCE ONLY / NOT YET KERNEL CHECKED. Generated deterministically by generate.py.
Proof/source assistance: GPT-6 Pro through ChatGPT (operator-selected label).
-/
import P112Sparse

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace P112Cert
open PR1497

/-- Original sparse M rows, in original row/entry order. -/
def M_entries (i : Fin 288) : List (Fin 104 × Int) :=
  if i.val < 144 then
    if i.val < 72 then
      if i.val < 36 then
        if i.val < 18 then
          if i.val < 9 then
            if i.val < 4 then
              if i.val < 2 then
                if i.val < 1 then
                  [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨4, by decide⟩, (-1 : Int)), (⟨5, by decide⟩, (1 : Int))] -- /M/0
                else
                  [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨8, by decide⟩, (-1 : Int)), (⟨9, by decide⟩, (1 : Int))] -- /M/1
              else
                if i.val < 3 then
                  [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨12, by decide⟩, (-1 : Int)), (⟨13, by decide⟩, (1 : Int))] -- /M/2
                else
                  [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨16, by decide⟩, (-1 : Int)), (⟨17, by decide⟩, (1 : Int))] -- /M/3
            else
              if i.val < 6 then
                if i.val < 5 then
                  [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨20, by decide⟩, (-1 : Int)), (⟨21, by decide⟩, (1 : Int))] -- /M/4
                else
                  [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨24, by decide⟩, (-1 : Int)), (⟨25, by decide⟩, (1 : Int))] -- /M/5
              else
                if i.val < 7 then
                  [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (-1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /M/6
                else
                  if i.val < 8 then
                    [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨32, by decide⟩, (-1 : Int)), (⟨33, by decide⟩, (1 : Int))] -- /M/7
                  else
                    [(⟨0, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨37, by decide⟩, (1 : Int))] -- /M/8
          else
            if i.val < 13 then
              if i.val < 11 then
                if i.val < 10 then
                  [(⟨0, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨41, by decide⟩, (1 : Int))] -- /M/9
                else
                  [(⟨0, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨45, by decide⟩, (1 : Int))] -- /M/10
              else
                if i.val < 12 then
                  [(⟨0, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨49, by decide⟩, (1 : Int))] -- /M/11
                else
                  [(⟨1, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨52, by decide⟩, (-1 : Int)), (⟨53, by decide⟩, (1 : Int))] -- /M/12
            else
              if i.val < 15 then
                if i.val < 14 then
                  [(⟨1, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨56, by decide⟩, (-1 : Int)), (⟨57, by decide⟩, (1 : Int))] -- /M/13
                else
                  [(⟨1, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (-1 : Int)), (⟨61, by decide⟩, (1 : Int))] -- /M/14
              else
                if i.val < 16 then
                  [(⟨1, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (-1 : Int)), (⟨65, by decide⟩, (1 : Int))] -- /M/15
                else
                  if i.val < 17 then
                    [(⟨1, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨69, by decide⟩, (1 : Int))] -- /M/16
                  else
                    [(⟨1, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨73, by decide⟩, (1 : Int))] -- /M/17
        else
          if i.val < 27 then
            if i.val < 22 then
              if i.val < 20 then
                if i.val < 19 then
                  [(⟨1, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (1 : Int))] -- /M/18
                else
                  [(⟨1, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (1 : Int))] -- /M/19
              else
                if i.val < 21 then
                  [(⟨2, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (1 : Int))] -- /M/20
                else
                  [(⟨2, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (1 : Int))] -- /M/21
            else
              if i.val < 24 then
                if i.val < 23 then
                  [(⟨2, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (1 : Int))] -- /M/22
                else
                  [(⟨2, by decide⟩, (1 : Int)), (⟨3, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (1 : Int))] -- /M/23
              else
                if i.val < 25 then
                  [(⟨4, by decide⟩, (1 : Int)), (⟨5, by decide⟩, (-1 : Int)), (⟨12, by decide⟩, (-1 : Int)), (⟨13, by decide⟩, (1 : Int))] -- /M/24
                else
                  if i.val < 26 then
                    [(⟨4, by decide⟩, (1 : Int)), (⟨5, by decide⟩, (-1 : Int)), (⟨16, by decide⟩, (-1 : Int)), (⟨17, by decide⟩, (1 : Int))] -- /M/25
                  else
                    [(⟨4, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨20, by decide⟩, (-1 : Int)), (⟨22, by decide⟩, (1 : Int))] -- /M/26
          else
            if i.val < 31 then
              if i.val < 29 then
                if i.val < 28 then
                  [(⟨4, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨24, by decide⟩, (-1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /M/27
                else
                  [(⟨4, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (-1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /M/28
              else
                if i.val < 30 then
                  [(⟨4, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨32, by decide⟩, (-1 : Int)), (⟨34, by decide⟩, (1 : Int))] -- /M/29
                else
                  [(⟨4, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨38, by decide⟩, (1 : Int))] -- /M/30
            else
              if i.val < 33 then
                if i.val < 32 then
                  [(⟨4, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨42, by decide⟩, (1 : Int))] -- /M/31
                else
                  [(⟨4, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨46, by decide⟩, (1 : Int))] -- /M/32
              else
                if i.val < 34 then
                  [(⟨4, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨50, by decide⟩, (1 : Int))] -- /M/33
                else
                  if i.val < 35 then
                    [(⟨5, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨52, by decide⟩, (-1 : Int)), (⟨54, by decide⟩, (1 : Int))] -- /M/34
                  else
                    [(⟨5, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨56, by decide⟩, (-1 : Int)), (⟨58, by decide⟩, (1 : Int))] -- /M/35
      else
        if i.val < 54 then
          if i.val < 45 then
            if i.val < 40 then
              if i.val < 38 then
                if i.val < 37 then
                  [(⟨5, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (-1 : Int)), (⟨62, by decide⟩, (1 : Int))] -- /M/36
                else
                  [(⟨5, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (1 : Int))] -- /M/37
              else
                if i.val < 39 then
                  [(⟨5, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (1 : Int))] -- /M/38
                else
                  [(⟨5, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (1 : Int))] -- /M/39
            else
              if i.val < 42 then
                if i.val < 41 then
                  [(⟨5, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (1 : Int))] -- /M/40
                else
                  [(⟨5, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (1 : Int))] -- /M/41
              else
                if i.val < 43 then
                  [(⟨6, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/42
                else
                  if i.val < 44 then
                    [(⟨6, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/43
                  else
                    [(⟨6, by decide⟩, (1 : Int)), (⟨7, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (1 : Int))] -- /M/44
          else
            if i.val < 49 then
              if i.val < 47 then
                if i.val < 46 then
                  [(⟨8, by decide⟩, (1 : Int)), (⟨9, by decide⟩, (-1 : Int)), (⟨12, by decide⟩, (-1 : Int)), (⟨13, by decide⟩, (1 : Int))] -- /M/45
                else
                  [(⟨8, by decide⟩, (1 : Int)), (⟨9, by decide⟩, (-1 : Int)), (⟨16, by decide⟩, (-1 : Int)), (⟨17, by decide⟩, (1 : Int))] -- /M/46
              else
                if i.val < 48 then
                  [(⟨8, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨20, by decide⟩, (-1 : Int)), (⟨22, by decide⟩, (1 : Int))] -- /M/47
                else
                  [(⟨8, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨24, by decide⟩, (-1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /M/48
            else
              if i.val < 51 then
                if i.val < 50 then
                  [(⟨8, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (-1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /M/49
                else
                  [(⟨8, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨32, by decide⟩, (-1 : Int)), (⟨34, by decide⟩, (1 : Int))] -- /M/50
              else
                if i.val < 52 then
                  [(⟨8, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨38, by decide⟩, (1 : Int))] -- /M/51
                else
                  if i.val < 53 then
                    [(⟨8, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨42, by decide⟩, (1 : Int))] -- /M/52
                  else
                    [(⟨8, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨46, by decide⟩, (1 : Int))] -- /M/53
        else
          if i.val < 63 then
            if i.val < 58 then
              if i.val < 56 then
                if i.val < 55 then
                  [(⟨8, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨50, by decide⟩, (1 : Int))] -- /M/54
                else
                  [(⟨9, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨52, by decide⟩, (-1 : Int)), (⟨54, by decide⟩, (1 : Int))] -- /M/55
              else
                if i.val < 57 then
                  [(⟨9, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨56, by decide⟩, (-1 : Int)), (⟨58, by decide⟩, (1 : Int))] -- /M/56
                else
                  [(⟨9, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (-1 : Int)), (⟨62, by decide⟩, (1 : Int))] -- /M/57
            else
              if i.val < 60 then
                if i.val < 59 then
                  [(⟨9, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (1 : Int))] -- /M/58
                else
                  [(⟨9, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (1 : Int))] -- /M/59
              else
                if i.val < 61 then
                  [(⟨9, by decide⟩, (1 : Int)), (⟨10, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (1 : Int))] -- /M/60
                else
                  if i.val < 62 then
                    [(⟨9, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (1 : Int))] -- /M/61
                  else
                    [(⟨9, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (1 : Int))] -- /M/62
          else
            if i.val < 67 then
              if i.val < 65 then
                if i.val < 64 then
                  [(⟨10, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/63
                else
                  [(⟨10, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/64
              else
                if i.val < 66 then
                  [(⟨10, by decide⟩, (1 : Int)), (⟨11, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (1 : Int))] -- /M/65
                else
                  [(⟨12, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨20, by decide⟩, (-1 : Int)), (⟨23, by decide⟩, (1 : Int))] -- /M/66
            else
              if i.val < 69 then
                if i.val < 68 then
                  [(⟨12, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨24, by decide⟩, (-1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /M/67
                else
                  [(⟨12, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (-1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /M/68
              else
                if i.val < 70 then
                  [(⟨12, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨32, by decide⟩, (-1 : Int)), (⟨35, by decide⟩, (1 : Int))] -- /M/69
                else
                  if i.val < 71 then
                    [(⟨12, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨39, by decide⟩, (1 : Int))] -- /M/70
                  else
                    [(⟨12, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨43, by decide⟩, (1 : Int))] -- /M/71
    else
      if i.val < 108 then
        if i.val < 90 then
          if i.val < 81 then
            if i.val < 76 then
              if i.val < 74 then
                if i.val < 73 then
                  [(⟨12, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨47, by decide⟩, (1 : Int))] -- /M/72
                else
                  [(⟨12, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨51, by decide⟩, (1 : Int))] -- /M/73
              else
                if i.val < 75 then
                  [(⟨13, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨52, by decide⟩, (-1 : Int)), (⟨55, by decide⟩, (1 : Int))] -- /M/74
                else
                  [(⟨13, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨56, by decide⟩, (-1 : Int)), (⟨59, by decide⟩, (1 : Int))] -- /M/75
            else
              if i.val < 78 then
                if i.val < 77 then
                  [(⟨13, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (-1 : Int)), (⟨63, by decide⟩, (1 : Int))] -- /M/76
                else
                  [(⟨13, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (-1 : Int)), (⟨67, by decide⟩, (1 : Int))] -- /M/77
              else
                if i.val < 79 then
                  [(⟨13, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/78
                else
                  if i.val < 80 then
                    [(⟨13, by decide⟩, (1 : Int)), (⟨14, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/79
                  else
                    [(⟨13, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/80
          else
            if i.val < 85 then
              if i.val < 83 then
                if i.val < 82 then
                  [(⟨13, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/81
                else
                  [(⟨14, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/82
              else
                if i.val < 84 then
                  [(⟨14, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/83
                else
                  [(⟨14, by decide⟩, (1 : Int)), (⟨15, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/84
            else
              if i.val < 87 then
                if i.val < 86 then
                  [(⟨16, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨20, by decide⟩, (-1 : Int)), (⟨23, by decide⟩, (1 : Int))] -- /M/85
                else
                  [(⟨16, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨24, by decide⟩, (-1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /M/86
              else
                if i.val < 88 then
                  [(⟨16, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (-1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /M/87
                else
                  if i.val < 89 then
                    [(⟨16, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨32, by decide⟩, (-1 : Int)), (⟨35, by decide⟩, (1 : Int))] -- /M/88
                  else
                    [(⟨16, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨39, by decide⟩, (1 : Int))] -- /M/89
        else
          if i.val < 99 then
            if i.val < 94 then
              if i.val < 92 then
                if i.val < 91 then
                  [(⟨16, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨43, by decide⟩, (1 : Int))] -- /M/90
                else
                  [(⟨16, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨47, by decide⟩, (1 : Int))] -- /M/91
              else
                if i.val < 93 then
                  [(⟨16, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨51, by decide⟩, (1 : Int))] -- /M/92
                else
                  [(⟨17, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨52, by decide⟩, (-1 : Int)), (⟨55, by decide⟩, (1 : Int))] -- /M/93
            else
              if i.val < 96 then
                if i.val < 95 then
                  [(⟨17, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨56, by decide⟩, (-1 : Int)), (⟨59, by decide⟩, (1 : Int))] -- /M/94
                else
                  [(⟨17, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (-1 : Int)), (⟨63, by decide⟩, (1 : Int))] -- /M/95
              else
                if i.val < 97 then
                  [(⟨17, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (-1 : Int)), (⟨67, by decide⟩, (1 : Int))] -- /M/96
                else
                  if i.val < 98 then
                    [(⟨17, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/97
                  else
                    [(⟨17, by decide⟩, (1 : Int)), (⟨18, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/98
          else
            if i.val < 103 then
              if i.val < 101 then
                if i.val < 100 then
                  [(⟨17, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/99
                else
                  [(⟨17, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/100
              else
                if i.val < 102 then
                  [(⟨18, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/101
                else
                  [(⟨18, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/102
            else
              if i.val < 105 then
                if i.val < 104 then
                  [(⟨18, by decide⟩, (1 : Int)), (⟨19, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/103
                else
                  [(⟨20, by decide⟩, (1 : Int)), (⟨21, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (-1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /M/104
              else
                if i.val < 106 then
                  [(⟨20, by decide⟩, (1 : Int)), (⟨21, by decide⟩, (-1 : Int)), (⟨32, by decide⟩, (-1 : Int)), (⟨33, by decide⟩, (1 : Int))] -- /M/105
                else
                  if i.val < 107 then
                    [(⟨20, by decide⟩, (1 : Int)), (⟨22, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨38, by decide⟩, (1 : Int))] -- /M/106
                  else
                    [(⟨20, by decide⟩, (1 : Int)), (⟨22, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨42, by decide⟩, (1 : Int))] -- /M/107
      else
        if i.val < 126 then
          if i.val < 117 then
            if i.val < 112 then
              if i.val < 110 then
                if i.val < 109 then
                  [(⟨20, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨47, by decide⟩, (1 : Int))] -- /M/108
                else
                  [(⟨20, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨51, by decide⟩, (1 : Int))] -- /M/109
              else
                if i.val < 111 then
                  [(⟨21, by decide⟩, (1 : Int)), (⟨22, by decide⟩, (-1 : Int)), (⟨53, by decide⟩, (-1 : Int)), (⟨54, by decide⟩, (1 : Int))] -- /M/110
                else
                  [(⟨21, by decide⟩, (1 : Int)), (⟨22, by decide⟩, (-1 : Int)), (⟨57, by decide⟩, (-1 : Int)), (⟨58, by decide⟩, (1 : Int))] -- /M/111
            else
              if i.val < 114 then
                if i.val < 113 then
                  [(⟨21, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨61, by decide⟩, (-1 : Int)), (⟨63, by decide⟩, (1 : Int))] -- /M/112
                else
                  [(⟨21, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨65, by decide⟩, (-1 : Int)), (⟨67, by decide⟩, (1 : Int))] -- /M/113
              else
                if i.val < 115 then
                  [(⟨22, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/114
                else
                  if i.val < 116 then
                    [(⟨22, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/115
                  else
                    [(⟨21, by decide⟩, (1 : Int)), (⟨22, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/116
          else
            if i.val < 121 then
              if i.val < 119 then
                if i.val < 118 then
                  [(⟨21, by decide⟩, (1 : Int)), (⟨22, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/117
                else
                  [(⟨21, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/118
              else
                if i.val < 120 then
                  [(⟨21, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/119
                else
                  [(⟨22, by decide⟩, (1 : Int)), (⟨23, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/120
            else
              if i.val < 123 then
                if i.val < 122 then
                  [(⟨24, by decide⟩, (1 : Int)), (⟨25, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (-1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /M/121
                else
                  [(⟨24, by decide⟩, (1 : Int)), (⟨25, by decide⟩, (-1 : Int)), (⟨32, by decide⟩, (-1 : Int)), (⟨33, by decide⟩, (1 : Int))] -- /M/122
              else
                if i.val < 124 then
                  [(⟨24, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨38, by decide⟩, (1 : Int))] -- /M/123
                else
                  if i.val < 125 then
                    [(⟨24, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨42, by decide⟩, (1 : Int))] -- /M/124
                  else
                    [(⟨24, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨47, by decide⟩, (1 : Int))] -- /M/125
        else
          if i.val < 135 then
            if i.val < 130 then
              if i.val < 128 then
                if i.val < 127 then
                  [(⟨24, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨51, by decide⟩, (1 : Int))] -- /M/126
                else
                  [(⟨25, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (-1 : Int)), (⟨53, by decide⟩, (-1 : Int)), (⟨54, by decide⟩, (1 : Int))] -- /M/127
              else
                if i.val < 129 then
                  [(⟨25, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (-1 : Int)), (⟨57, by decide⟩, (-1 : Int)), (⟨58, by decide⟩, (1 : Int))] -- /M/128
                else
                  [(⟨25, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨61, by decide⟩, (-1 : Int)), (⟨63, by decide⟩, (1 : Int))] -- /M/129
            else
              if i.val < 132 then
                if i.val < 131 then
                  [(⟨25, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨65, by decide⟩, (-1 : Int)), (⟨67, by decide⟩, (1 : Int))] -- /M/130
                else
                  [(⟨26, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/131
              else
                if i.val < 133 then
                  [(⟨26, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/132
                else
                  if i.val < 134 then
                    [(⟨25, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/133
                  else
                    [(⟨25, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/134
          else
            if i.val < 139 then
              if i.val < 137 then
                if i.val < 136 then
                  [(⟨25, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/135
                else
                  [(⟨25, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/136
              else
                if i.val < 138 then
                  [(⟨26, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/137
                else
                  [(⟨28, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨39, by decide⟩, (1 : Int))] -- /M/138
            else
              if i.val < 141 then
                if i.val < 140 then
                  [(⟨28, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨43, by decide⟩, (1 : Int))] -- /M/139
                else
                  [(⟨28, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨46, by decide⟩, (1 : Int))] -- /M/140
              else
                if i.val < 142 then
                  [(⟨28, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨50, by decide⟩, (1 : Int))] -- /M/141
                else
                  if i.val < 143 then
                    [(⟨29, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨53, by decide⟩, (-1 : Int)), (⟨55, by decide⟩, (1 : Int))] -- /M/142
                  else
                    [(⟨29, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨57, by decide⟩, (-1 : Int)), (⟨59, by decide⟩, (1 : Int))] -- /M/143
  else
    if i.val < 216 then
      if i.val < 180 then
        if i.val < 162 then
          if i.val < 153 then
            if i.val < 148 then
              if i.val < 146 then
                if i.val < 145 then
                  [(⟨29, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (-1 : Int)), (⟨61, by decide⟩, (-1 : Int)), (⟨62, by decide⟩, (1 : Int))] -- /M/144
                else
                  [(⟨29, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (-1 : Int)), (⟨65, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (1 : Int))] -- /M/145
              else
                if i.val < 147 then
                  [(⟨30, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/146
                else
                  [(⟨30, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/147
            else
              if i.val < 150 then
                if i.val < 149 then
                  [(⟨29, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/148
                else
                  [(⟨29, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/149
              else
                if i.val < 151 then
                  [(⟨29, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/150
                else
                  if i.val < 152 then
                    [(⟨29, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/151
                  else
                    [(⟨30, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/152
          else
            if i.val < 157 then
              if i.val < 155 then
                if i.val < 154 then
                  [(⟨32, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (-1 : Int)), (⟨39, by decide⟩, (1 : Int))] -- /M/153
                else
                  [(⟨32, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (-1 : Int)), (⟨43, by decide⟩, (1 : Int))] -- /M/154
              else
                if i.val < 156 then
                  [(⟨32, by decide⟩, (1 : Int)), (⟨34, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨46, by decide⟩, (1 : Int))] -- /M/155
                else
                  [(⟨32, by decide⟩, (1 : Int)), (⟨34, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨50, by decide⟩, (1 : Int))] -- /M/156
            else
              if i.val < 159 then
                if i.val < 158 then
                  [(⟨33, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨53, by decide⟩, (-1 : Int)), (⟨55, by decide⟩, (1 : Int))] -- /M/157
                else
                  [(⟨33, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨57, by decide⟩, (-1 : Int)), (⟨59, by decide⟩, (1 : Int))] -- /M/158
              else
                if i.val < 160 then
                  [(⟨33, by decide⟩, (1 : Int)), (⟨34, by decide⟩, (-1 : Int)), (⟨61, by decide⟩, (-1 : Int)), (⟨62, by decide⟩, (1 : Int))] -- /M/159
                else
                  if i.val < 161 then
                    [(⟨33, by decide⟩, (1 : Int)), (⟨34, by decide⟩, (-1 : Int)), (⟨65, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (1 : Int))] -- /M/160
                  else
                    [(⟨34, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/161
        else
          if i.val < 171 then
            if i.val < 166 then
              if i.val < 164 then
                if i.val < 163 then
                  [(⟨34, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/162
                else
                  [(⟨33, by decide⟩, (1 : Int)), (⟨34, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/163
              else
                if i.val < 165 then
                  [(⟨33, by decide⟩, (1 : Int)), (⟨34, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/164
                else
                  [(⟨33, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/165
            else
              if i.val < 168 then
                if i.val < 167 then
                  [(⟨33, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/166
                else
                  [(⟨34, by decide⟩, (1 : Int)), (⟨35, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/167
              else
                if i.val < 169 then
                  [(⟨36, by decide⟩, (1 : Int)), (⟨37, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨45, by decide⟩, (1 : Int))] -- /M/168
                else
                  if i.val < 170 then
                    [(⟨36, by decide⟩, (1 : Int)), (⟨37, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨49, by decide⟩, (1 : Int))] -- /M/169
                  else
                    [(⟨38, by decide⟩, (1 : Int)), (⟨39, by decide⟩, (-1 : Int)), (⟨54, by decide⟩, (-1 : Int)), (⟨55, by decide⟩, (1 : Int))] -- /M/170
          else
            if i.val < 175 then
              if i.val < 173 then
                if i.val < 172 then
                  [(⟨38, by decide⟩, (1 : Int)), (⟨39, by decide⟩, (-1 : Int)), (⟨58, by decide⟩, (-1 : Int)), (⟨59, by decide⟩, (1 : Int))] -- /M/171
                else
                  [(⟨37, by decide⟩, (1 : Int)), (⟨38, by decide⟩, (-1 : Int)), (⟨69, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (1 : Int))] -- /M/172
              else
                if i.val < 174 then
                  [(⟨37, by decide⟩, (1 : Int)), (⟨38, by decide⟩, (-1 : Int)), (⟨73, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (1 : Int))] -- /M/173
                else
                  [(⟨37, by decide⟩, (1 : Int)), (⟨39, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/174
            else
              if i.val < 177 then
                if i.val < 176 then
                  [(⟨37, by decide⟩, (1 : Int)), (⟨39, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/175
                else
                  [(⟨37, by decide⟩, (1 : Int)), (⟨38, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/176
              else
                if i.val < 178 then
                  [(⟨37, by decide⟩, (1 : Int)), (⟨38, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/177
                else
                  if i.val < 179 then
                    [(⟨37, by decide⟩, (1 : Int)), (⟨39, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/178
                  else
                    [(⟨37, by decide⟩, (1 : Int)), (⟨39, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/179
      else
        if i.val < 198 then
          if i.val < 189 then
            if i.val < 184 then
              if i.val < 182 then
                if i.val < 181 then
                  [(⟨38, by decide⟩, (1 : Int)), (⟨39, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/180
                else
                  [(⟨40, by decide⟩, (1 : Int)), (⟨41, by decide⟩, (-1 : Int)), (⟨44, by decide⟩, (-1 : Int)), (⟨45, by decide⟩, (1 : Int))] -- /M/181
              else
                if i.val < 183 then
                  [(⟨40, by decide⟩, (1 : Int)), (⟨41, by decide⟩, (-1 : Int)), (⟨48, by decide⟩, (-1 : Int)), (⟨49, by decide⟩, (1 : Int))] -- /M/182
                else
                  [(⟨42, by decide⟩, (1 : Int)), (⟨43, by decide⟩, (-1 : Int)), (⟨54, by decide⟩, (-1 : Int)), (⟨55, by decide⟩, (1 : Int))] -- /M/183
            else
              if i.val < 186 then
                if i.val < 185 then
                  [(⟨42, by decide⟩, (1 : Int)), (⟨43, by decide⟩, (-1 : Int)), (⟨58, by decide⟩, (-1 : Int)), (⟨59, by decide⟩, (1 : Int))] -- /M/184
                else
                  [(⟨41, by decide⟩, (1 : Int)), (⟨42, by decide⟩, (-1 : Int)), (⟨69, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (1 : Int))] -- /M/185
              else
                if i.val < 187 then
                  [(⟨41, by decide⟩, (1 : Int)), (⟨42, by decide⟩, (-1 : Int)), (⟨73, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (1 : Int))] -- /M/186
                else
                  if i.val < 188 then
                    [(⟨41, by decide⟩, (1 : Int)), (⟨43, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/187
                  else
                    [(⟨41, by decide⟩, (1 : Int)), (⟨43, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/188
          else
            if i.val < 193 then
              if i.val < 191 then
                if i.val < 190 then
                  [(⟨41, by decide⟩, (1 : Int)), (⟨42, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/189
                else
                  [(⟨41, by decide⟩, (1 : Int)), (⟨42, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/190
              else
                if i.val < 192 then
                  [(⟨41, by decide⟩, (1 : Int)), (⟨43, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/191
                else
                  [(⟨41, by decide⟩, (1 : Int)), (⟨43, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/192
            else
              if i.val < 195 then
                if i.val < 194 then
                  [(⟨42, by decide⟩, (1 : Int)), (⟨43, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/193
                else
                  [(⟨46, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int)), (⟨62, by decide⟩, (-1 : Int)), (⟨63, by decide⟩, (1 : Int))] -- /M/194
              else
                if i.val < 196 then
                  [(⟨46, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (-1 : Int)), (⟨67, by decide⟩, (1 : Int))] -- /M/195
                else
                  if i.val < 197 then
                    [(⟨45, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int)), (⟨69, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/196
                  else
                    [(⟨45, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int)), (⟨73, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/197
        else
          if i.val < 207 then
            if i.val < 202 then
              if i.val < 200 then
                if i.val < 199 then
                  [(⟨45, by decide⟩, (1 : Int)), (⟨46, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (1 : Int))] -- /M/198
                else
                  [(⟨45, by decide⟩, (1 : Int)), (⟨46, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (1 : Int))] -- /M/199
              else
                if i.val < 201 then
                  [(⟨45, by decide⟩, (1 : Int)), (⟨46, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/200
                else
                  [(⟨45, by decide⟩, (1 : Int)), (⟨46, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/201
            else
              if i.val < 204 then
                if i.val < 203 then
                  [(⟨45, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/202
                else
                  [(⟨45, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/203
              else
                if i.val < 205 then
                  [(⟨46, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/204
                else
                  if i.val < 206 then
                    [(⟨50, by decide⟩, (1 : Int)), (⟨51, by decide⟩, (-1 : Int)), (⟨62, by decide⟩, (-1 : Int)), (⟨63, by decide⟩, (1 : Int))] -- /M/205
                  else
                    [(⟨50, by decide⟩, (1 : Int)), (⟨51, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (-1 : Int)), (⟨67, by decide⟩, (1 : Int))] -- /M/206
          else
            if i.val < 211 then
              if i.val < 209 then
                if i.val < 208 then
                  [(⟨49, by decide⟩, (1 : Int)), (⟨51, by decide⟩, (-1 : Int)), (⟨69, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/207
                else
                  [(⟨49, by decide⟩, (1 : Int)), (⟨51, by decide⟩, (-1 : Int)), (⟨73, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/208
              else
                if i.val < 210 then
                  [(⟨49, by decide⟩, (1 : Int)), (⟨50, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (1 : Int))] -- /M/209
                else
                  [(⟨49, by decide⟩, (1 : Int)), (⟨50, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (1 : Int))] -- /M/210
            else
              if i.val < 213 then
                if i.val < 212 then
                  [(⟨49, by decide⟩, (1 : Int)), (⟨50, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/211
                else
                  [(⟨49, by decide⟩, (1 : Int)), (⟨50, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/212
              else
                if i.val < 214 then
                  [(⟨49, by decide⟩, (1 : Int)), (⟨51, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/213
                else
                  if i.val < 215 then
                    [(⟨49, by decide⟩, (1 : Int)), (⟨51, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/214
                  else
                    [(⟨50, by decide⟩, (1 : Int)), (⟨51, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/215
    else
      if i.val < 252 then
        if i.val < 234 then
          if i.val < 225 then
            if i.val < 220 then
              if i.val < 218 then
                if i.val < 217 then
                  [(⟨52, by decide⟩, (1 : Int)), (⟨53, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (-1 : Int)), (⟨61, by decide⟩, (1 : Int))] -- /M/216
                else
                  [(⟨52, by decide⟩, (1 : Int)), (⟨53, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (-1 : Int)), (⟨65, by decide⟩, (1 : Int))] -- /M/217
              else
                if i.val < 219 then
                  [(⟨52, by decide⟩, (1 : Int)), (⟨54, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (1 : Int))] -- /M/218
                else
                  [(⟨52, by decide⟩, (1 : Int)), (⟨54, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (1 : Int))] -- /M/219
            else
              if i.val < 222 then
                if i.val < 221 then
                  [(⟨52, by decide⟩, (1 : Int)), (⟨55, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/220
                else
                  [(⟨52, by decide⟩, (1 : Int)), (⟨55, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/221
              else
                if i.val < 223 then
                  [(⟨53, by decide⟩, (1 : Int)), (⟨54, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/222
                else
                  if i.val < 224 then
                    [(⟨53, by decide⟩, (1 : Int)), (⟨54, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/223
                  else
                    [(⟨53, by decide⟩, (1 : Int)), (⟨55, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/224
          else
            if i.val < 229 then
              if i.val < 227 then
                if i.val < 226 then
                  [(⟨53, by decide⟩, (1 : Int)), (⟨55, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/225
                else
                  [(⟨54, by decide⟩, (1 : Int)), (⟨55, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/226
              else
                if i.val < 228 then
                  [(⟨56, by decide⟩, (1 : Int)), (⟨57, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (-1 : Int)), (⟨61, by decide⟩, (1 : Int))] -- /M/227
                else
                  [(⟨56, by decide⟩, (1 : Int)), (⟨57, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (-1 : Int)), (⟨65, by decide⟩, (1 : Int))] -- /M/228
            else
              if i.val < 231 then
                if i.val < 230 then
                  [(⟨56, by decide⟩, (1 : Int)), (⟨58, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (1 : Int))] -- /M/229
                else
                  [(⟨56, by decide⟩, (1 : Int)), (⟨58, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (1 : Int))] -- /M/230
              else
                if i.val < 232 then
                  [(⟨56, by decide⟩, (1 : Int)), (⟨59, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /M/231
                else
                  if i.val < 233 then
                    [(⟨56, by decide⟩, (1 : Int)), (⟨59, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨83, by decide⟩, (1 : Int))] -- /M/232
                  else
                    [(⟨57, by decide⟩, (1 : Int)), (⟨58, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/233
        else
          if i.val < 243 then
            if i.val < 238 then
              if i.val < 236 then
                if i.val < 235 then
                  [(⟨57, by decide⟩, (1 : Int)), (⟨58, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/234
                else
                  [(⟨57, by decide⟩, (1 : Int)), (⟨59, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/235
              else
                if i.val < 237 then
                  [(⟨57, by decide⟩, (1 : Int)), (⟨59, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/236
                else
                  [(⟨58, by decide⟩, (1 : Int)), (⟨59, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/237
            else
              if i.val < 240 then
                if i.val < 239 then
                  [(⟨60, by decide⟩, (1 : Int)), (⟨63, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/238
                else
                  [(⟨60, by decide⟩, (1 : Int)), (⟨63, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/239
              else
                if i.val < 241 then
                  [(⟨60, by decide⟩, (1 : Int)), (⟨62, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (1 : Int))] -- /M/240
                else
                  if i.val < 242 then
                    [(⟨60, by decide⟩, (1 : Int)), (⟨62, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (1 : Int))] -- /M/241
                  else
                    [(⟨61, by decide⟩, (1 : Int)), (⟨62, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/242
          else
            if i.val < 247 then
              if i.val < 245 then
                if i.val < 244 then
                  [(⟨61, by decide⟩, (1 : Int)), (⟨62, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/243
                else
                  [(⟨61, by decide⟩, (1 : Int)), (⟨63, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/244
              else
                if i.val < 246 then
                  [(⟨61, by decide⟩, (1 : Int)), (⟨63, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/245
                else
                  [(⟨62, by decide⟩, (1 : Int)), (⟨63, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/246
            else
              if i.val < 249 then
                if i.val < 248 then
                  [(⟨64, by decide⟩, (1 : Int)), (⟨67, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (-1 : Int)), (⟨71, by decide⟩, (1 : Int))] -- /M/247
                else
                  [(⟨64, by decide⟩, (1 : Int)), (⟨67, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /M/248
              else
                if i.val < 250 then
                  [(⟨64, by decide⟩, (1 : Int)), (⟨66, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (1 : Int))] -- /M/249
                else
                  if i.val < 251 then
                    [(⟨64, by decide⟩, (1 : Int)), (⟨66, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨82, by decide⟩, (1 : Int))] -- /M/250
                  else
                    [(⟨65, by decide⟩, (1 : Int)), (⟨66, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/251
      else
        if i.val < 270 then
          if i.val < 261 then
            if i.val < 256 then
              if i.val < 254 then
                if i.val < 253 then
                  [(⟨65, by decide⟩, (1 : Int)), (⟨66, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/252
                else
                  [(⟨65, by decide⟩, (1 : Int)), (⟨67, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/253
              else
                if i.val < 255 then
                  [(⟨65, by decide⟩, (1 : Int)), (⟨67, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/254
                else
                  [(⟨66, by decide⟩, (1 : Int)), (⟨67, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/255
            else
              if i.val < 258 then
                if i.val < 257 then
                  [(⟨68, by decide⟩, (1 : Int)), (⟨69, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (1 : Int))] -- /M/256
                else
                  [(⟨68, by decide⟩, (1 : Int)), (⟨69, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (1 : Int))] -- /M/257
              else
                if i.val < 259 then
                  [(⟨69, by decide⟩, (1 : Int)), (⟨70, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/258
                else
                  if i.val < 260 then
                    [(⟨69, by decide⟩, (1 : Int)), (⟨70, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/259
                  else
                    [(⟨69, by decide⟩, (1 : Int)), (⟨71, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/260
          else
            if i.val < 265 then
              if i.val < 263 then
                if i.val < 262 then
                  [(⟨69, by decide⟩, (1 : Int)), (⟨71, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/261
                else
                  [(⟨70, by decide⟩, (1 : Int)), (⟨71, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/262
              else
                if i.val < 264 then
                  [(⟨72, by decide⟩, (1 : Int)), (⟨73, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (1 : Int))] -- /M/263
                else
                  [(⟨72, by decide⟩, (1 : Int)), (⟨73, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (1 : Int))] -- /M/264
            else
              if i.val < 267 then
                if i.val < 266 then
                  [(⟨73, by decide⟩, (1 : Int)), (⟨74, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨86, by decide⟩, (1 : Int))] -- /M/265
                else
                  [(⟨73, by decide⟩, (1 : Int)), (⟨74, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨90, by decide⟩, (1 : Int))] -- /M/266
              else
                if i.val < 268 then
                  [(⟨73, by decide⟩, (1 : Int)), (⟨75, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨94, by decide⟩, (1 : Int))] -- /M/267
                else
                  if i.val < 269 then
                    [(⟨73, by decide⟩, (1 : Int)), (⟨75, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨98, by decide⟩, (1 : Int))] -- /M/268
                  else
                    [(⟨74, by decide⟩, (1 : Int)), (⟨75, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (1 : Int))] -- /M/269
        else
          if i.val < 279 then
            if i.val < 274 then
              if i.val < 272 then
                if i.val < 271 then
                  [(⟨77, by decide⟩, (1 : Int)), (⟨78, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/270
                else
                  [(⟨77, by decide⟩, (1 : Int)), (⟨78, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/271
              else
                if i.val < 273 then
                  [(⟨77, by decide⟩, (1 : Int)), (⟨79, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/272
                else
                  [(⟨77, by decide⟩, (1 : Int)), (⟨79, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/273
            else
              if i.val < 276 then
                if i.val < 275 then
                  [(⟨78, by decide⟩, (1 : Int)), (⟨79, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/274
                else
                  [(⟨81, by decide⟩, (1 : Int)), (⟨82, by decide⟩, (-1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨87, by decide⟩, (1 : Int))] -- /M/275
              else
                if i.val < 277 then
                  [(⟨81, by decide⟩, (1 : Int)), (⟨82, by decide⟩, (-1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨91, by decide⟩, (1 : Int))] -- /M/276
                else
                  if i.val < 278 then
                    [(⟨81, by decide⟩, (1 : Int)), (⟨83, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (-1 : Int)), (⟨95, by decide⟩, (1 : Int))] -- /M/277
                  else
                    [(⟨81, by decide⟩, (1 : Int)), (⟨83, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (-1 : Int)), (⟨99, by decide⟩, (1 : Int))] -- /M/278
          else
            if i.val < 283 then
              if i.val < 281 then
                if i.val < 280 then
                  [(⟨82, by decide⟩, (1 : Int)), (⟨83, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/279
                else
                  [(⟨84, by decide⟩, (1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (1 : Int))] -- /M/280
              else
                if i.val < 282 then
                  [(⟨84, by decide⟩, (1 : Int)), (⟨85, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (1 : Int))] -- /M/281
                else
                  [(⟨86, by decide⟩, (1 : Int)), (⟨87, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (1 : Int))] -- /M/282
            else
              if i.val < 285 then
                if i.val < 284 then
                  [(⟨88, by decide⟩, (1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (-1 : Int)), (⟨93, by decide⟩, (1 : Int))] -- /M/283
                else
                  [(⟨88, by decide⟩, (1 : Int)), (⟨89, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (-1 : Int)), (⟨97, by decide⟩, (1 : Int))] -- /M/284
              else
                if i.val < 286 then
                  [(⟨90, by decide⟩, (1 : Int)), (⟨91, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (-1 : Int)), (⟨101, by decide⟩, (1 : Int))] -- /M/285
                else
                  if i.val < 287 then
                    [(⟨94, by decide⟩, (1 : Int)), (⟨95, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/286
                  else
                    [(⟨98, by decide⟩, (1 : Int)), (⟨99, by decide⟩, (-1 : Int)), (⟨102, by decide⟩, (-1 : Int)), (⟨103, by decide⟩, (1 : Int))] -- /M/287

def M : Mat 288 104 := fun i => Sparse.row (M_entries i)

/-- Original sparse P rows, in original row/entry order. -/
def P_entries (i : Fin 104) : List (Fin 33 × Int) :=
  if i.val < 52 then
    if i.val < 26 then
      if i.val < 13 then
        if i.val < 6 then
          if i.val < 3 then
            if i.val < 1 then
              [(⟨0, by decide⟩, (1 : Int))] -- /P/0
            else
              if i.val < 2 then
                [(⟨0, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/1
              else
                [(⟨0, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/2
          else
            if i.val < 4 then
              [(⟨0, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/3
            else
              if i.val < 5 then
                [(⟨1, by decide⟩, (1 : Int))] -- /P/4
              else
                [(⟨1, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/5
        else
          if i.val < 9 then
            if i.val < 7 then
              [(⟨1, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/6
            else
              if i.val < 8 then
                [(⟨1, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/7
              else
                [(⟨2, by decide⟩, (1 : Int))] -- /P/8
          else
            if i.val < 11 then
              if i.val < 10 then
                [(⟨2, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/9
              else
                [(⟨2, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/10
            else
              if i.val < 12 then
                [(⟨2, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/11
              else
                [(⟨3, by decide⟩, (1 : Int))] -- /P/12
      else
        if i.val < 19 then
          if i.val < 16 then
            if i.val < 14 then
              [(⟨3, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/13
            else
              if i.val < 15 then
                [(⟨3, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/14
              else
                [(⟨3, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/15
          else
            if i.val < 17 then
              [(⟨4, by decide⟩, (1 : Int))] -- /P/16
            else
              if i.val < 18 then
                [(⟨4, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/17
              else
                [(⟨4, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/18
        else
          if i.val < 22 then
            if i.val < 20 then
              [(⟨4, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/19
            else
              if i.val < 21 then
                [(⟨5, by decide⟩, (1 : Int))] -- /P/20
              else
                [(⟨5, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/21
          else
            if i.val < 24 then
              if i.val < 23 then
                [(⟨5, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/22
              else
                [(⟨5, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/23
            else
              if i.val < 25 then
                [(⟨6, by decide⟩, (1 : Int))] -- /P/24
              else
                [(⟨6, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/25
    else
      if i.val < 39 then
        if i.val < 32 then
          if i.val < 29 then
            if i.val < 27 then
              [(⟨6, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/26
            else
              if i.val < 28 then
                [(⟨6, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/27
              else
                [(⟨7, by decide⟩, (1 : Int))] -- /P/28
          else
            if i.val < 30 then
              [(⟨7, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/29
            else
              if i.val < 31 then
                [(⟨7, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/30
              else
                [(⟨7, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/31
        else
          if i.val < 35 then
            if i.val < 33 then
              [(⟨8, by decide⟩, (1 : Int))] -- /P/32
            else
              if i.val < 34 then
                [(⟨8, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/33
              else
                [(⟨8, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/34
          else
            if i.val < 37 then
              if i.val < 36 then
                [(⟨8, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/35
              else
                [(⟨9, by decide⟩, (1 : Int))] -- /P/36
            else
              if i.val < 38 then
                [(⟨9, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/37
              else
                [(⟨9, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/38
      else
        if i.val < 45 then
          if i.val < 42 then
            if i.val < 40 then
              [(⟨9, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/39
            else
              if i.val < 41 then
                [(⟨10, by decide⟩, (1 : Int))] -- /P/40
              else
                [(⟨10, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/41
          else
            if i.val < 43 then
              [(⟨10, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/42
            else
              if i.val < 44 then
                [(⟨10, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/43
              else
                [(⟨11, by decide⟩, (1 : Int))] -- /P/44
        else
          if i.val < 48 then
            if i.val < 46 then
              [(⟨11, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/45
            else
              if i.val < 47 then
                [(⟨11, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/46
              else
                [(⟨11, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/47
          else
            if i.val < 50 then
              if i.val < 49 then
                [(⟨12, by decide⟩, (1 : Int))] -- /P/48
              else
                [(⟨12, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/49
            else
              if i.val < 51 then
                [(⟨12, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/50
              else
                [(⟨12, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/51
  else
    if i.val < 78 then
      if i.val < 65 then
        if i.val < 58 then
          if i.val < 55 then
            if i.val < 53 then
              [(⟨13, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/52
            else
              if i.val < 54 then
                [(⟨13, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/53
              else
                [(⟨13, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/54
          else
            if i.val < 56 then
              [(⟨13, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/55
            else
              if i.val < 57 then
                [(⟨14, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/56
              else
                [(⟨14, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/57
        else
          if i.val < 61 then
            if i.val < 59 then
              [(⟨14, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/58
            else
              if i.val < 60 then
                [(⟨14, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/59
              else
                [(⟨15, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/60
          else
            if i.val < 63 then
              if i.val < 62 then
                [(⟨15, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/61
              else
                [(⟨15, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/62
            else
              if i.val < 64 then
                [(⟨15, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/63
              else
                [(⟨16, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/64
      else
        if i.val < 71 then
          if i.val < 68 then
            if i.val < 66 then
              [(⟨16, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/65
            else
              if i.val < 67 then
                [(⟨16, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/66
              else
                [(⟨16, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/67
          else
            if i.val < 69 then
              [(⟨17, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/68
            else
              if i.val < 70 then
                [(⟨17, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/69
              else
                [(⟨17, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/70
        else
          if i.val < 74 then
            if i.val < 72 then
              [(⟨17, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/71
            else
              if i.val < 73 then
                [(⟨18, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/72
              else
                [(⟨18, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/73
          else
            if i.val < 76 then
              if i.val < 75 then
                [(⟨18, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/74
              else
                [(⟨18, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/75
            else
              if i.val < 77 then
                [(⟨19, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/76
              else
                [(⟨19, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/77
    else
      if i.val < 91 then
        if i.val < 84 then
          if i.val < 81 then
            if i.val < 79 then
              [(⟨19, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/78
            else
              if i.val < 80 then
                [(⟨19, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/79
              else
                [(⟨20, by decide⟩, (1 : Int)), (⟨26, by decide⟩, (1 : Int))] -- /P/80
          else
            if i.val < 82 then
              [(⟨20, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/81
            else
              if i.val < 83 then
                [(⟨20, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/82
              else
                [(⟨20, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/83
        else
          if i.val < 87 then
            if i.val < 85 then
              [(⟨21, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/84
            else
              if i.val < 86 then
                [(⟨21, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/85
              else
                [(⟨21, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/86
          else
            if i.val < 89 then
              if i.val < 88 then
                [(⟨21, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/87
              else
                [(⟨22, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/88
            else
              if i.val < 90 then
                [(⟨22, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/89
              else
                [(⟨22, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/90
      else
        if i.val < 97 then
          if i.val < 94 then
            if i.val < 92 then
              [(⟨22, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/91
            else
              if i.val < 93 then
                [(⟨23, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/92
              else
                [(⟨23, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/93
          else
            if i.val < 95 then
              [(⟨23, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/94
            else
              if i.val < 96 then
                [(⟨23, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/95
              else
                [(⟨24, by decide⟩, (1 : Int)), (⟨27, by decide⟩, (1 : Int))] -- /P/96
        else
          if i.val < 100 then
            if i.val < 98 then
              [(⟨24, by decide⟩, (1 : Int)), (⟨28, by decide⟩, (1 : Int))] -- /P/97
            else
              if i.val < 99 then
                [(⟨24, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/98
              else
                [(⟨24, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/99
          else
            if i.val < 102 then
              if i.val < 101 then
                [(⟨25, by decide⟩, (1 : Int)), (⟨29, by decide⟩, (1 : Int))] -- /P/100
              else
                [(⟨25, by decide⟩, (1 : Int)), (⟨30, by decide⟩, (1 : Int))] -- /P/101
            else
              if i.val < 103 then
                [(⟨25, by decide⟩, (1 : Int)), (⟨31, by decide⟩, (1 : Int))] -- /P/102
              else
                [(⟨25, by decide⟩, (1 : Int)), (⟨32, by decide⟩, (1 : Int))] -- /P/103

def P : Mat 104 33 := fun i => Sparse.row (P_entries i)

/-- Original sparse Q rows, in original row/entry order. -/
def Q_entries (i : Fin 33) : List (Fin 104 × Int) :=
  if i.val < 16 then
    if i.val < 8 then
      if i.val < 4 then
        if i.val < 2 then
          if i.val < 1 then
            [(⟨0, by decide⟩, (1 : Int))] -- /Q/0
          else
            [(⟨4, by decide⟩, (1 : Int))] -- /Q/1
        else
          if i.val < 3 then
            [(⟨8, by decide⟩, (1 : Int))] -- /Q/2
          else
            [(⟨12, by decide⟩, (1 : Int))] -- /Q/3
      else
        if i.val < 6 then
          if i.val < 5 then
            [(⟨16, by decide⟩, (1 : Int))] -- /Q/4
          else
            [(⟨20, by decide⟩, (1 : Int))] -- /Q/5
        else
          if i.val < 7 then
            [(⟨24, by decide⟩, (1 : Int))] -- /Q/6
          else
            [(⟨28, by decide⟩, (1 : Int))] -- /Q/7
    else
      if i.val < 12 then
        if i.val < 10 then
          if i.val < 9 then
            [(⟨32, by decide⟩, (1 : Int))] -- /Q/8
          else
            [(⟨36, by decide⟩, (1 : Int))] -- /Q/9
        else
          if i.val < 11 then
            [(⟨40, by decide⟩, (1 : Int))] -- /Q/10
          else
            [(⟨44, by decide⟩, (1 : Int))] -- /Q/11
      else
        if i.val < 14 then
          if i.val < 13 then
            [(⟨48, by decide⟩, (1 : Int))] -- /Q/12
          else
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨52, by decide⟩, (1 : Int))] -- /Q/13
        else
          if i.val < 15 then
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨56, by decide⟩, (1 : Int))] -- /Q/14
          else
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨60, by decide⟩, (1 : Int))] -- /Q/15
  else
    if i.val < 24 then
      if i.val < 20 then
        if i.val < 18 then
          if i.val < 17 then
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨64, by decide⟩, (1 : Int))] -- /Q/16
          else
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (1 : Int))] -- /Q/17
        else
          if i.val < 19 then
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨72, by decide⟩, (1 : Int))] -- /Q/18
          else
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (1 : Int))] -- /Q/19
      else
        if i.val < 22 then
          if i.val < 21 then
            [(⟨0, by decide⟩, (1 : Int)), (⟨1, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (1 : Int))] -- /Q/20
          else
            [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨84, by decide⟩, (1 : Int))] -- /Q/21
        else
          if i.val < 23 then
            [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨88, by decide⟩, (1 : Int))] -- /Q/22
          else
            [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨92, by decide⟩, (1 : Int))] -- /Q/23
    else
      if i.val < 28 then
        if i.val < 26 then
          if i.val < 25 then
            [(⟨0, by decide⟩, (1 : Int)), (⟨2, by decide⟩, (-1 : Int)), (⟨96, by decide⟩, (1 : Int))] -- /Q/24
          else
            [(⟨4, by decide⟩, (1 : Int)), (⟨6, by decide⟩, (-1 : Int)), (⟨100, by decide⟩, (1 : Int))] -- /Q/25
        else
          if i.val < 27 then
            [(⟨0, by decide⟩, (-1 : Int)), (⟨1, by decide⟩, (1 : Int))] -- /Q/26
          else
            [(⟨0, by decide⟩, (-1 : Int)), (⟨2, by decide⟩, (1 : Int))] -- /Q/27
      else
        if i.val < 30 then
          if i.val < 29 then
            [(⟨0, by decide⟩, (-1 : Int)), (⟨3, by decide⟩, (1 : Int))] -- /Q/28
          else
            [(⟨4, by decide⟩, (-1 : Int)), (⟨6, by decide⟩, (1 : Int))] -- /Q/29
        else
          if i.val < 31 then
            [(⟨4, by decide⟩, (-1 : Int)), (⟨7, by decide⟩, (1 : Int))] -- /Q/30
          else
            if i.val < 32 then
              [(⟨12, by decide⟩, (-1 : Int)), (⟨14, by decide⟩, (1 : Int))] -- /Q/31
            else
              [(⟨12, by decide⟩, (-1 : Int)), (⟨15, by decide⟩, (1 : Int))] -- /Q/32

def Q : Mat 33 104 := fun i => Sparse.row (Q_entries i)

/-- Original sparse W rows, in original row/entry order. -/
def W_entries (i : Fin 104) : List (Fin 288 × Int) :=
  if i.val < 52 then
    if i.val < 26 then
      if i.val < 13 then
        if i.val < 6 then
          if i.val < 3 then
            if i.val < 1 then
              [] -- /W/0
            else
              if i.val < 2 then
                [] -- /W/1
              else
                [] -- /W/2
          else
            if i.val < 4 then
              [] -- /W/3
            else
              if i.val < 5 then
                [] -- /W/4
              else
                [(⟨0, by decide⟩, (1 : Int))] -- /W/5
        else
          if i.val < 9 then
            if i.val < 7 then
              [] -- /W/6
            else
              if i.val < 8 then
                [] -- /W/7
              else
                [] -- /W/8
          else
            if i.val < 11 then
              if i.val < 10 then
                [(⟨1, by decide⟩, (1 : Int))] -- /W/9
              else
                [(⟨26, by decide⟩, (1 : Int)), (⟨47, by decide⟩, (-1 : Int))] -- /W/10
            else
              if i.val < 12 then
                [(⟨28, by decide⟩, (1 : Int)), (⟨49, by decide⟩, (-1 : Int))] -- /W/11
              else
                [] -- /W/12
      else
        if i.val < 19 then
          if i.val < 16 then
            if i.val < 14 then
              [(⟨2, by decide⟩, (1 : Int))] -- /W/13
            else
              if i.val < 15 then
                [] -- /W/14
              else
                [] -- /W/15
          else
            if i.val < 17 then
              [] -- /W/16
            else
              if i.val < 18 then
                [(⟨3, by decide⟩, (1 : Int))] -- /W/17
              else
                [(⟨66, by decide⟩, (1 : Int)), (⟨85, by decide⟩, (-1 : Int))] -- /W/18
        else
          if i.val < 22 then
            if i.val < 20 then
              [(⟨68, by decide⟩, (1 : Int)), (⟨87, by decide⟩, (-1 : Int))] -- /W/19
            else
              if i.val < 21 then
                [] -- /W/20
              else
                [(⟨4, by decide⟩, (1 : Int))] -- /W/21
          else
            if i.val < 24 then
              if i.val < 23 then
                [(⟨26, by decide⟩, (1 : Int))] -- /W/22
              else
                [(⟨66, by decide⟩, (1 : Int))] -- /W/23
            else
              if i.val < 25 then
                [] -- /W/24
              else
                [(⟨5, by decide⟩, (1 : Int))] -- /W/25
    else
      if i.val < 39 then
        if i.val < 32 then
          if i.val < 29 then
            if i.val < 27 then
              [(⟨27, by decide⟩, (1 : Int))] -- /W/26
            else
              if i.val < 28 then
                [(⟨67, by decide⟩, (1 : Int))] -- /W/27
              else
                [] -- /W/28
          else
            if i.val < 30 then
              [(⟨6, by decide⟩, (1 : Int))] -- /W/29
            else
              if i.val < 31 then
                [(⟨28, by decide⟩, (1 : Int))] -- /W/30
              else
                [(⟨68, by decide⟩, (1 : Int))] -- /W/31
        else
          if i.val < 35 then
            if i.val < 33 then
              [] -- /W/32
            else
              if i.val < 34 then
                [(⟨7, by decide⟩, (1 : Int))] -- /W/33
              else
                [(⟨29, by decide⟩, (1 : Int))] -- /W/34
          else
            if i.val < 37 then
              if i.val < 36 then
                [(⟨69, by decide⟩, (1 : Int))] -- /W/35
              else
                [] -- /W/36
            else
              if i.val < 38 then
                [(⟨8, by decide⟩, (1 : Int))] -- /W/37
              else
                [(⟨30, by decide⟩, (1 : Int))] -- /W/38
      else
        if i.val < 45 then
          if i.val < 42 then
            if i.val < 40 then
              [(⟨70, by decide⟩, (1 : Int))] -- /W/39
            else
              if i.val < 41 then
                [] -- /W/40
              else
                [(⟨9, by decide⟩, (1 : Int))] -- /W/41
          else
            if i.val < 43 then
              [(⟨31, by decide⟩, (1 : Int))] -- /W/42
            else
              if i.val < 44 then
                [(⟨71, by decide⟩, (1 : Int))] -- /W/43
              else
                [] -- /W/44
        else
          if i.val < 48 then
            if i.val < 46 then
              [(⟨10, by decide⟩, (1 : Int))] -- /W/45
            else
              if i.val < 47 then
                [(⟨32, by decide⟩, (1 : Int))] -- /W/46
              else
                [(⟨72, by decide⟩, (1 : Int))] -- /W/47
          else
            if i.val < 50 then
              if i.val < 49 then
                [] -- /W/48
              else
                [(⟨11, by decide⟩, (1 : Int))] -- /W/49
            else
              if i.val < 51 then
                [(⟨33, by decide⟩, (1 : Int))] -- /W/50
              else
                [(⟨73, by decide⟩, (1 : Int))] -- /W/51
  else
    if i.val < 78 then
      if i.val < 65 then
        if i.val < 58 then
          if i.val < 55 then
            if i.val < 53 then
              [] -- /W/52
            else
              if i.val < 54 then
                [(⟨12, by decide⟩, (1 : Int))] -- /W/53
              else
                [(⟨0, by decide⟩, (-1 : Int)), (⟨34, by decide⟩, (1 : Int))] -- /W/54
          else
            if i.val < 56 then
              [(⟨2, by decide⟩, (-1 : Int)), (⟨74, by decide⟩, (1 : Int))] -- /W/55
            else
              if i.val < 57 then
                [] -- /W/56
              else
                [(⟨13, by decide⟩, (1 : Int))] -- /W/57
        else
          if i.val < 61 then
            if i.val < 59 then
              [(⟨0, by decide⟩, (-1 : Int)), (⟨35, by decide⟩, (1 : Int))] -- /W/58
            else
              if i.val < 60 then
                [(⟨2, by decide⟩, (-1 : Int)), (⟨75, by decide⟩, (1 : Int))] -- /W/59
              else
                [] -- /W/60
          else
            if i.val < 63 then
              if i.val < 62 then
                [(⟨14, by decide⟩, (1 : Int))] -- /W/61
              else
                [(⟨0, by decide⟩, (-1 : Int)), (⟨36, by decide⟩, (1 : Int))] -- /W/62
            else
              if i.val < 64 then
                [(⟨2, by decide⟩, (-1 : Int)), (⟨76, by decide⟩, (1 : Int))] -- /W/63
              else
                [] -- /W/64
      else
        if i.val < 71 then
          if i.val < 68 then
            if i.val < 66 then
              [(⟨15, by decide⟩, (1 : Int))] -- /W/65
            else
              if i.val < 67 then
                [(⟨0, by decide⟩, (-1 : Int)), (⟨37, by decide⟩, (1 : Int))] -- /W/66
              else
                [(⟨2, by decide⟩, (-1 : Int)), (⟨77, by decide⟩, (1 : Int))] -- /W/67
          else
            if i.val < 69 then
              [] -- /W/68
            else
              if i.val < 70 then
                [(⟨16, by decide⟩, (1 : Int))] -- /W/69
              else
                [(⟨0, by decide⟩, (-1 : Int)), (⟨38, by decide⟩, (1 : Int))] -- /W/70
        else
          if i.val < 74 then
            if i.val < 72 then
              [(⟨2, by decide⟩, (-1 : Int)), (⟨78, by decide⟩, (1 : Int))] -- /W/71
            else
              if i.val < 73 then
                [] -- /W/72
              else
                [(⟨17, by decide⟩, (1 : Int))] -- /W/73
          else
            if i.val < 76 then
              if i.val < 75 then
                [(⟨0, by decide⟩, (-1 : Int)), (⟨39, by decide⟩, (1 : Int))] -- /W/74
              else
                [(⟨2, by decide⟩, (-1 : Int)), (⟨79, by decide⟩, (1 : Int))] -- /W/75
            else
              if i.val < 77 then
                [] -- /W/76
              else
                [(⟨18, by decide⟩, (1 : Int))] -- /W/77
    else
      if i.val < 91 then
        if i.val < 84 then
          if i.val < 81 then
            if i.val < 79 then
              [(⟨0, by decide⟩, (-1 : Int)), (⟨40, by decide⟩, (1 : Int))] -- /W/78
            else
              if i.val < 80 then
                [(⟨2, by decide⟩, (-1 : Int)), (⟨80, by decide⟩, (1 : Int))] -- /W/79
              else
                [] -- /W/80
          else
            if i.val < 82 then
              [(⟨19, by decide⟩, (1 : Int))] -- /W/81
            else
              if i.val < 83 then
                [(⟨0, by decide⟩, (-1 : Int)), (⟨41, by decide⟩, (1 : Int))] -- /W/82
              else
                [(⟨2, by decide⟩, (-1 : Int)), (⟨81, by decide⟩, (1 : Int))] -- /W/83
        else
          if i.val < 87 then
            if i.val < 85 then
              [] -- /W/84
            else
              if i.val < 86 then
                [(⟨20, by decide⟩, (1 : Int))] -- /W/85
              else
                [(⟨4, by decide⟩, (-1 : Int)), (⟨26, by decide⟩, (1 : Int)), (⟨116, by decide⟩, (1 : Int))] -- /W/86
          else
            if i.val < 89 then
              if i.val < 88 then
                [(⟨6, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (1 : Int)), (⟨148, by decide⟩, (1 : Int))] -- /W/87
              else
                [] -- /W/88
            else
              if i.val < 90 then
                [(⟨21, by decide⟩, (1 : Int))] -- /W/89
              else
                [(⟨4, by decide⟩, (-1 : Int)), (⟨26, by decide⟩, (1 : Int)), (⟨117, by decide⟩, (1 : Int))] -- /W/90
      else
        if i.val < 97 then
          if i.val < 94 then
            if i.val < 92 then
              [(⟨6, by decide⟩, (-1 : Int)), (⟨28, by decide⟩, (1 : Int)), (⟨149, by decide⟩, (1 : Int))] -- /W/91
            else
              if i.val < 93 then
                [] -- /W/92
              else
                [(⟨22, by decide⟩, (1 : Int))] -- /W/93
          else
            if i.val < 95 then
              [(⟨4, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (1 : Int)), (⟨118, by decide⟩, (1 : Int))] -- /W/94
            else
              if i.val < 96 then
                [(⟨6, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (1 : Int)), (⟨150, by decide⟩, (1 : Int))] -- /W/95
              else
                [] -- /W/96
        else
          if i.val < 100 then
            if i.val < 98 then
              [(⟨23, by decide⟩, (1 : Int))] -- /W/97
            else
              if i.val < 99 then
                [(⟨4, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (1 : Int)), (⟨119, by decide⟩, (1 : Int))] -- /W/98
              else
                [(⟨6, by decide⟩, (-1 : Int)), (⟨68, by decide⟩, (1 : Int)), (⟨151, by decide⟩, (1 : Int))] -- /W/99
          else
            if i.val < 102 then
              if i.val < 101 then
                [] -- /W/100
              else
                [(⟨44, by decide⟩, (1 : Int))] -- /W/101
            else
              if i.val < 103 then
                [(⟨26, by decide⟩, (-1 : Int)), (⟨66, by decide⟩, (1 : Int)), (⟨120, by decide⟩, (1 : Int))] -- /W/102
              else
                [(⟨30, by decide⟩, (-1 : Int)), (⟨70, by decide⟩, (1 : Int)), (⟨180, by decide⟩, (1 : Int))] -- /W/103

def W : Mat 104 288 := fun i => Sparse.row (W_entries i)

/-- Provenance metadata only; no class-completeness theorem is asserted. -/
def anchors : List Nat := [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4]

def basePairRepresentatives : List (String × Nat) := [("1", 0), ("2", 0), ("3", 0), ("4", 1), ("5", 1), ("6", 3), ("7", 3)]

def coordinateLabels : List (Nat × Nat) := [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 4), (1, 5), (2, 0), (2, 1), (2, 4), (2, 5), (3, 0), (3, 1), (3, 6), (3, 7), (4, 0), (4, 1), (4, 6), (4, 7), (5, 0), (5, 2), (5, 4), (5, 6), (6, 0), (6, 2), (6, 4), (6, 6), (7, 0), (7, 2), (7, 5), (7, 7), (8, 0), (8, 2), (8, 5), (8, 7), (9, 0), (9, 3), (9, 4), (9, 7), (10, 0), (10, 3), (10, 4), (10, 7), (11, 0), (11, 3), (11, 5), (11, 6), (12, 0), (12, 3), (12, 5), (12, 6), (13, 1), (13, 2), (13, 4), (13, 7), (14, 1), (14, 2), (14, 4), (14, 7), (15, 1), (15, 2), (15, 5), (15, 6), (16, 1), (16, 2), (16, 5), (16, 6), (17, 1), (17, 3), (17, 4), (17, 6), (18, 1), (18, 3), (18, 4), (18, 6), (19, 1), (19, 3), (19, 5), (19, 7), (20, 1), (20, 3), (20, 5), (20, 7), (21, 2), (21, 3), (21, 4), (21, 5), (22, 2), (22, 3), (22, 4), (22, 5), (23, 2), (23, 3), (23, 6), (23, 7), (24, 2), (24, 3), (24, 6), (24, 7), (25, 4), (25, 5), (25, 6), (25, 7)]

def freeParameters : Nat := 33

def parameterClassCount : Nat := 26

def gPoints : List Nat := [1, 2, 3, 4, 5, 6, 7]

/-- Inherited JSON metadata, NOT a formal matrix-rank statement. -/
def rankMetadata : Nat := 71

end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.M_entries
#print axioms P112Cert.M
#print axioms P112Cert.P_entries
#print axioms P112Cert.P
#print axioms P112Cert.Q_entries
#print axioms P112Cert.Q
#print axioms P112Cert.W_entries
#print axioms P112Cert.W
#print axioms P112Cert.anchors
#print axioms P112Cert.basePairRepresentatives
#print axioms P112Cert.coordinateLabels
#print axioms P112Cert.freeParameters
#print axioms P112Cert.parameterClassCount
#print axioms P112Cert.gPoints
#print axioms P112Cert.rankMetadata
