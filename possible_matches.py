#!/usr/bin/env python3
# usage: ./possible_matches guess1 guess2 guess3 answer

import os
import re
from collections import defaultdict
from typing import Optional, Iterable

def isvalid(word: str) -> bool:
  return len(word) == 5 and word.isalpha() and word.islower()

def print_annotated_guess(guess: str, result: str):
  """Pretty print an annotated guess."""
  from sys import stdout
  if not stdout.isatty():
    print(f'## {guess} ({result})')
    return
  s = '\033[1;38;2;255;255;255m'
  for c, r in zip(guess, result):
    if r == 'g':
      s += '\033[48;2;106;170;100m'
    elif r == 'y':
      s += '\033[48;2;201;180;88m'
    else:
      s += '\033[48;2;120;124;126m'
    s += ' ' + c + ' '
  print(s + '\033[0m')

def load_dictionary_approx() -> Iterable[str]:
  w4 = set()
  w3 = set()
  with open('/usr/share/dict/words') as f:
    for word in (l.strip() for l in f):
      if not word.isalpha() or not word.islower():
        continue
      if isvalid(word) and not (word.endswith('ed') and
                                (word[:4] in w4 or word[:3] in w3)) and not (
                                    word[-1] == 's' and word[:4] in w4):
        yield word
      elif len(word) == 4:
        w4.add(word)
      elif len(word) == 3:
        w3.add(word)


def load_dictionary() -> Iterable[str]:
  dir = os.path.dirname(__file__)
  path = os.path.join(dir, 'words.txt')
  with open(path) as f:
    for word in f:
      yield word.strip()

def print_possible_matches(guesses: list[str], dictionary: Iterable[str]):
  """Prints out the possible matches given a sequence of guesses+results.

  guesses: alternating guess and result strings
  dictionary: list of valid words
  """
  not_in_word = set()
  in_word_pos_unknown = set()
  in_word_pos_known = set()
  not_at_pos = [set() for _ in range(5)]
  at_pos: list[Optional[str]] = [None] * 5

  for word, result in zip(guesses[::2], guesses[1::2]):
    for i in range(5):
      if result[i] == 'y':
        in_word_pos_unknown.add(word[i])
        not_at_pos[i].add(word[i])
      elif result[i] == 'g':
        in_word_pos_known.add(word[i])
        assert(at_pos[i] in (None, word[i]))
        at_pos[i] = word[i]
      else:
        not_in_word.add(word[i])

  r = ''.join(
    at_pos[i] or f"[^{''.join(not_at_pos[i].union(not_in_word))}]"
    for i in range(5))

  pat = re.compile(''.join(r))
  # pat will ensure that letters with a known position are present.
  also_require = in_word_pos_unknown.difference(in_word_pos_known)

  num_matches = 0
  for word in dictionary:
    if pat.fullmatch(word) and set(word).issuperset(also_require):
      num_matches += 1
      print(word, end='\n' if num_matches % 13 == 0 else ' ')
  print(f"\n{num_matches} match{'es' if num_matches != 1 else ''}")

def print_possible_matches_at_each_guess(guesses: list[str]):
  """Prints out possible matches at each step of seqeunce of guesses.
  guesses: alternating guesses and results
  """

  dictionary = list(load_dictionary())
  for i in range(2, len(guesses) + 1, 2):
    if i>2: print()
    print_annotated_guess(guesses[i-2], guesses[i-1])
    print_possible_matches(guesses[:i], dictionary)

def guess_result(guess: str, answer: str):
  """Generates a result string for guess: _ (gray), y (yellow), g(green)."""
  assert(len(guess) == 5 and len(answer) == 5)

  result = ['.']*5
  lcount = defaultdict(lambda: 0)
  for i in range(5):
    if guess[i] == answer[i]:
      result[i] = 'g'
    else:
      lcount[answer[i]] += 1
  for i in range(5):
    if result[i] != '.':
      continue
    if lcount[guess[i]] > 0:
      result[i] = 'y'
      lcount[guess[i]] -= 1
  return ''.join(result)

def replay_with_possible_matches(guesses: list[str]):
  """Prints possible matches at each step from unannotated guesses."""
  annotated_guesses = []
  for guess in guesses[:-1]:
    annotated_guesses.append(guess)
    annotated_guesses.append(guess_result(guess, guesses[-1]))
  print_possible_matches_at_each_guess(annotated_guesses)
  print()
  print_annotated_guess(guesses[-1], 'g'*5)

def main(args):
  if not args:
    print_possible_matches_at_each_guess(GUESSES)
  else:
    replay_with_possible_matches(args)

if __name__ == "__main__":
  from sys import argv
  main(argv[1:])
