#include <iostream>
#include <fstream>
#include <unordered_map>
#include <cmath>

using namespace std;

double entropy(unordered_map<char, unsigned long long>& char_occurences, int char_count)
{
  double result = 0.0;
  for (const auto& el : char_occurences)
  {
    result += el.second * log2(el.second);
  }

  return log2(char_count) - (result / char_count);
}

double conditional_entropy(unordered_map<char, unsigned long long>& char_occurences, unordered_map<char, unordered_map<char, unsigned long long>>& conditional_occurences, int char_count)
{
  double result;

  for (const auto& m : conditional_occurences)
  {
    auto occurences = m.second;
    unsigned long long count = 0;
    for (const auto& el : occurences)
      count += el.second;

      result += char_occurences[m.first] * entropy(occurences, count);
  }


  return result / char_count;
}
 

int main(int argc, char* argv[])
{
  if (argc < 2) 
  {
    cerr << "no input file" << endl;
    return 1;
  }

  ifstream input(argv[1]);

  if (input.is_open())
  {
    unordered_map<char, unsigned long long> char_occurences;
    unordered_map<char, unordered_map<char, unsigned long long>> conditional_occurences;
    unsigned long long char_count = 0;

    char curr_char;
    char prev_char;

    while (input.get(curr_char))
    {
      char_occurences[curr_char]++;
      char_count++;
      conditional_occurences[prev_char][curr_char]++;
      prev_char = curr_char;
    }

    input.close();

    cout << entropy(char_occurences, char_count) << endl
         << conditional_entropy(char_occurences, conditional_occurences, char_count) << endl;

  }
  else
  {
    cerr << "could not open the file" << endl;
    return 1;
  }

  return 0;
}