// Independent dense interpreter for local four-symbol graphs.
// Prepared for CubeJerry with OpenAI assistance. Apache-2.0.
// This does not use the author Machine or its compiled interpreter.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct Instruction { int op, tape, value; std::array<int,4> branch; };
int symbol(char c) {
    const std::string alphabet="_01|";
    auto p=alphabet.find(c);
    if(p==std::string::npos) throw std::runtime_error("bad input symbol");
    return static_cast<int>(p);
}
int main(int argc,char **argv) {
  try {
    if(argc!=2) throw std::runtime_error("one encoded test file required");
    std::ifstream in(argv[1]);
    int n,nt,cases; std::int64_t capacity;
    in>>n>>nt>>capacity>>cases;
    if(!in || n<1 || nt<2 || capacity<128 || cases<1) throw std::runtime_error("bad dimensions");
    std::vector<Instruction> code(n);
    for(auto &a:code) {
      in>>a.op>>a.tape>>a.value;
      for(auto &d:a.branch) in>>d;
      if(!in || a.op<0 || a.op>4) throw std::runtime_error("bad instruction");
      if(a.op<3 && (a.tape<0 || a.tape>=nt)) throw std::runtime_error("bad tape");
      if(a.op==0) for(int d:a.branch) if(d < -1 || d>=n) throw std::runtime_error("bad local edge");
      if(a.op==1 && (a.value<0 || a.value>3)) throw std::runtime_error("bad write");
      if(a.op==2 && a.value!=1 && a.value!=-1) throw std::runtime_error("nonunit move");
      if(a.op==3 && (a.value<0 || a.value>=n)) throw std::runtime_error("bad fixed goto");
    }
    std::vector<std::vector<unsigned char>> row(nt,std::vector<unsigned char>(capacity,0));
    std::vector<std::int64_t> origin(nt),head(nt),low(nt),high(nt);
    for(int t=0;t<nt;t++) {
      origin[t]=head[t]=low[t]=high[t]=19+2*t;
      for(int k=0;k<4;k++) { row[t][origin[t]-6+k]=std::array<int,4>{2,1,3,2}[k]; row[t][capacity-5+k]=std::array<int,4>{1,2,3,1}[k]; }
    }
    for(int c=0;c<cases;c++) {
      std::string header,payload,expected; in>>header>>payload>>expected;
      if(!in || head!=origin) throw std::runtime_error("bad clean entry");
      bool expected_halt=expected!="REJECT";
      std::array<std::string,2> fields={header,payload};
      for(int t=0;t<2;t++) {
        auto &s=fields[t]; if(s=="EMPTY")s.clear();
        if(origin[t]+s.size()+8>=static_cast<std::size_t>(capacity)) throw std::runtime_error("observer capacity");
        std::fill(row[t].begin()+origin[t],row[t].end()-6,0);
        for(std::size_t j=0;j<s.size();j++) row[t][origin[t]+j]=symbol(s[j]);
        for(int k=0;k<4;k++)row[t][origin[t]+s.size()+1+k]=std::array<int,4>{1,2,3,1}[k];
      }
      auto before=row;
      std::vector<std::array<std::uint64_t,3>> counts(nt,{0,0,0});
      std::uint64_t steps=0; int pc=0; bool halt=false;
      while(pc>=0 && steps<10000000000ULL) {
        if(pc>=n)throw std::runtime_error("escaped graph");
        const auto &a=code[pc++];++steps;
        if(a.op==0) { ++counts[a.tape][0]; pc=a.branch[row[a.tape][head[a.tape]]]; }
        else if(a.op==1) { ++counts[a.tape][1]; row[a.tape][head[a.tape]]=a.value; }
        else if(a.op==2) {
          ++counts[a.tape][2]; auto &h=head[a.tape]; h+=a.value;
          if(h<0 || h>=capacity)throw std::runtime_error("observer capacity exceeded");
          low[a.tape]=std::min(low[a.tape],h);high[a.tape]=std::max(high[a.tape],h);
        } else if(a.op==3) pc=a.value;
        else { halt=true;break; }
      }
      if(steps>=10000000000ULL)throw std::runtime_error("bounded observer budget");
      bool public_unchanged=row[0]==before[0] && row[1]==before[1];
      bool result=true;
      if(expected_halt) {
        if(expected.size()!=fields[1].size())throw std::runtime_error("wrong expected extent");
        for(std::size_t j=0;j<expected.size();j++)before[1][origin[1]+j]=symbol(expected[j]);
        result=row==before;
      }
      std::uint64_t history=0;
      for(int t=2;t<nt;t++)history+=high[t]-low[t]+1;
      std::cout<<"{\"case\":"<<c<<",\"steps\":"<<steps<<",\"halt\":"<<(halt?"true":"false")
        <<",\"exact_rows\":"<<(result?"true":"false")<<",\"heads\":"<<(head==origin?"true":"false")
        <<",\"failure_public_unchanged\":"<<(public_unchanged?"true":"false")<<",\"history\":"<<history
        <<",\"data_counts\":["<<counts[1][0]<<","<<counts[1][1]<<","<<counts[1][2]<<"]}"<<std::endl;
      if(!halt && c+1<cases)throw std::runtime_error("failure reuse excluded");
    }
  } catch(const std::exception &e) { std::cerr<<e.what()<<std::endl;return 2; }
}
