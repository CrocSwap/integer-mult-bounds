// Dense interpreter for the literal table; observer fields never feed control.
// Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
// Apache-2.0. This is test infrastructure, not the mathematical tape program.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct Instruction { int op, tape, value; std::array<int,4> next; };
int symbol(char c) {
  if(c=='_') return 0; if(c=='0') return 1;
  if(c=='1') return 2; if(c=='|') return 3;
  throw std::runtime_error("fixture symbol");
}

int main(int argc,char**argv) {
 try {
  if(argc!=4) throw std::runtime_error("table, packet, output required");
  std::ifstream table(argv[1]), packet(argv[2]);
  int count; table>>count;
  std::vector<Instruction> code(count);
  for(auto &i:code) table>>i.op>>i.tape>>i.value>>i.next[0]>>i.next[1]>>i.next[2]>>i.next[3];
  if(!table) throw std::runtime_error("table parse");
  std::array<int,27> origin,head,cap,low,high;
  std::array<std::vector<unsigned char>,27> row;
  std::array<uint64_t,27> writes{};
  for(auto &n:origin) packet>>n;
  for(auto &n:cap) packet>>n;
  std::string header,data; packet>>header>>data;
  if(!packet) throw std::runtime_error("packet parse");
  for(int t=0;t<27;++t) {
    head[t]=low[t]=high[t]=origin[t];
    row[t].assign(origin[t]+cap[t]+3,0);
    row[t][origin[t]-3]=2; row[t][origin[t]-2]=3;
    if(t<2) row[t][origin[t]-1]=2;
    row[t][origin[t]+cap[t]+1]=1; row[t][origin[t]+cap[t]+2]=3;
  }
  for(size_t j=0;j<header.size();++j) row[0][origin[0]+j]=symbol(header[j]);
  for(size_t j=0;j<data.size();++j) row[1][origin[1]+j]=symbol(data[j]);
  auto old_header=row[0];
  uint64_t steps=0; int pc=0; bool accepted=false,rejected=false;
  while(!accepted && !rejected) {
    if(pc<0 || pc>=count) throw std::runtime_error("pc range");
    if(++steps>6000000000ULL) throw std::runtime_error("test instruction cap");
    const auto &i=code[pc++];
    switch(i.op) {
      case 0: pc=i.next[row[i.tape][head[i.tape]]]; if(pc<0) rejected=true; break;
      case 1: row[i.tape][head[i.tape]]=i.value; ++writes[i.tape]; break;
      case 2:
        head[i.tape]+=i.value;
        low[i.tape]=std::min(low[i.tape],head[i.tape]);
        high[i.tape]=std::max(high[i.tape],head[i.tape]);
        if(head[i.tape]<origin[i.tape]-(i.tape>=2) ||
           head[i.tape]>origin[i.tape]+cap[i.tape]) throw std::runtime_error("proved visit cap escaped");
        break;
      case 3: pc=i.value; break;
      case 4: accepted=true; break;
      default: throw std::runtime_error("opcode");
    }
  }
  bool returned=true,clean=true,exterior=true;
  uint64_t history=0;
  for(int t=0;t<27;++t) {
    returned=returned && head[t]==origin[t];
    exterior=exterior && row[t][origin[t]-3]==2 && row[t][origin[t]-2]==3;
    if(t<2) exterior=exterior && row[t][origin[t]-1]==2;
    exterior=exterior && row[t][origin[t]+cap[t]+1]==1 && row[t][origin[t]+cap[t]+2]==3;
    if(t>=2) {
      history+=high[t]-low[t]+1;
      for(int j=origin[t]-1;j<=origin[t]+cap[t];++j) clean=clean && row[t][j]==0;
    }
  }
  std::ofstream output(argv[3],std::ios::binary);
  const char*alphabet="_01|";
  for(size_t j=0;j<data.size();++j) output.put(alphabet[row[1][origin[1]+j]]);
  if(!output) throw std::runtime_error("output file");
  std::cout<<"{\"accepted\":"<<(accepted?"true":"false")
           <<",\"steps\":"<<steps<<",\"heads_returned\":"<<(returned?"true":"false")
           <<",\"private_blank\":"<<(clean?"true":"false")
           <<",\"header_preserved\":"<<((row[0]==old_header)?"true":"false")
           <<",\"exteriors_preserved\":"<<(exterior?"true":"false")
           <<",\"data_writes\":"<<writes[1]<<",\"header_writes\":"<<writes[0]
           <<",\"private_history\":"<<history<<"}\n";
  return 0;
 } catch(const std::exception& e) { std::cerr<<e.what()<<"\n"; return 1; }
}
