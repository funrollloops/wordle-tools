#!/usr/bin/env python3

import re
from typing import Optional, Iterable

# Guesses: word first, then five letters: y (yellow) or g (green).
GUESSES = [
  'arise',
  'yy_y_',
  'donut',
  '___y_',
]

assert(all(len(g) == 5 for g in GUESSES))
assert(len(GUESSES) % 2 == 0)

def load_dictionary() -> Iterable[str]:
  with open('/usr/share/dict/words') as f:
    for word in (l.strip() for l in f):
      if len(word) == 5 and word.islower() and word.isalpha():
        yield word

def print_possible_matches(guesses: list[str], dictionary: Iterable[str]):
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
      print(word, end='\n' if num_matches % 10 == 0 else ' ')
  print("\nnum matches =", num_matches)

def print_possible_matches_at_each_guess(guesses: list[str]):
  dictionary = list(load_dictionary())
  for i in range(2, len(guesses) + 1, 2):
    if i>2: print()
    print(f'## {guesses[i-2]} ({guesses[i-1]})')
    print_possible_matches(guesses[:i], dictionary)


if __name__ == "__main__":
  print_possible_matches_at_each_guess(GUESSES)
