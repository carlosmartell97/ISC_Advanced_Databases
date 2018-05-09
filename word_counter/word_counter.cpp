#include <cstdio>
#include <fstream>
#include <iostream>
#include <string>
#include <map>
#include <algorithm>
using namespace std;

int main(){
  ifstream input("input.txt");
  ifstream odyssey("odyssey.txt");
  ofstream output; output.open("resultados_1.4.txt");
  map<string, int> dictionary;
  map<string, int> ocurrences;
  char ignore[] = {',', '-', '.', '(', ')', '!', '?', '#', ';', ':', '"'};
  string read;
  while(odyssey >> read){
    transform(read.begin(), read.end(), read.begin(), ::tolower);
    for(char c : ignore){
      read.erase(remove(read.begin(), read.end(), c), read.end());
    }
    if(read==""){
      continue;
    }
    if(dictionary.find(read) != dictionary.end()){
      dictionary[read] = dictionary[read]+1;
    } else {
      dictionary[read] = 1;
    }
  }
  while (input >> read){
    transform(read.begin(), read.end(), read.begin(), ::tolower);
    for(char c : ignore){
      read.erase(remove(read.begin(), read.end(), c), read.end());
    }
    if(dictionary.find(read)==dictionary.end() || read==""){
      continue;
    }
    else if(ocurrences.find(read) != ocurrences.end()){
      ocurrences[read] = ocurrences[read]+1;
    } else {
      ocurrences[read] = 1;
    }
  }
  for (map<string, int>::iterator it=ocurrences.begin(); it!=ocurrences.end(); it++ ){
    printf("%s,%d\n", it->first.c_str(), it->second);
    output << it->first.c_str() << "," << it->second << "," << endl;
  }
  output.close();
  return 0;
}
