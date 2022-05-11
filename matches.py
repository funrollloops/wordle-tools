#!/usr/bin/env python3
# usage: ./matches.py guess1 guess2 guess3 answer

import os
from collections import defaultdict
from typing import Iterable

from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_bool('limit', True, 'Truncate long lists of matches')

HINT_GREEN = 'g'
HINT_YELLOW = 'y'
HINT_GRAY = '.'


def print_annotated_guess(guess: str, result: str):
  """Pretty print an annotated guess."""
  from sys import stdout
  if not stdout.isatty():
    print(f'## {guess} ({result})')
    return
  s = '\033[1;38;2;255;255;255m'
  for c, r in zip(guess, result):
    if r == HINT_GREEN:
      s += '\033[48;2;106;170;100m'
    elif r == HINT_YELLOW:
      s += '\033[48;2;201;180;88m'
    else:
      s += '\033[48;2;120;124;126m'
    s += ' ' + c + ' '
  print(s + '\033[0m')


def load_dictionary() -> Iterable[str]:
  dir = os.path.dirname(__file__)
  path = os.path.join(dir, 'words.txt')
  with open(path) as f:
    for word in f:
      yield word.strip()


class WordleConstraint:
  def __init__(self):
    self.min = defaultdict(lambda: 0)
    self.max = defaultdict(lambda: 5)
    self.positional_constraints = tuple(
        set(map(chr, range(ord('a'),
                           ord('z') + 1))) for _ in range(5))

  def update(self, word: str, result: str):
    assert len(word) == len(result) == 5 and word.islower() and word.isalpha()
    word_min = defaultdict(lambda: 0)
    saw_gray = set()
    for i, (char, hint) in enumerate(zip(word, result)):
      assert char >= 'a' and char <= 'z'
      if hint == HINT_GREEN:
        assert char in self.positional_constraints[i]
        self.positional_constraints[i].intersection_update(set(char))
        word_min[char] += 1
      elif hint == HINT_YELLOW:
        self.positional_constraints[i].discard(char)
        word_min[char] += 1
      else:
        assert hint == HINT_GRAY, 'Unexpected hint "%s"' % hint
        word_min[char] += 0
        saw_gray.add(char)
    for char, new_min in word_min.items():
      if char in saw_gray:
        assert self.min[char] <= new_min
        self.max[char] = new_min
      if self.min[char] < new_min:
        self.min[char] = new_min

  def match(self, word: str) -> bool:
    lcount = defaultdict(lambda: 0)
    for i, chr in enumerate(word):
      if chr not in self.positional_constraints[i]:
        return False
      lcount[chr] += 1
    for chr, min_cnt in self.min.items():
      if lcount.get(chr, 0) < min_cnt:
        return False
    for chr, max_cnt in self.max.items():
      if lcount.get(chr, 0) > max_cnt:
        return False
    return True


def print_matches(dictionary: Iterable[str], constraints: WordleConstraint):
  num_matches = 0
  for word in filter(constraints.match, dictionary):
    num_matches += 1
    if not FLAGS.limit or num_matches <= 13 * 5:
      print(word, end='\n' if num_matches % 13 == 0 else ' ')
    elif num_matches == 13 * 5 + 1:
      print("…", end='')
  print(f"\n{num_matches} match{'es' if num_matches != 1 else ''}")


def guess_result(guess: str, answer: str) -> str:
  """Generates a result string for guess.

  The result uses the characters in HINT_GREEN, HINT_YELLOW, and HINT_GRAY."""
  assert (len(guess) == 5 and len(answer) == 5)

  result = [HINT_GRAY] * 5
  lcount = defaultdict(lambda: 0)
  for i in range(5):
    if guess[i] == answer[i]:
      result[i] = HINT_GREEN
    else:
      lcount[answer[i]] += 1
  for i in range(5):
    if result[i] != HINT_GREEN and lcount[guess[i]] > 0:
      result[i] = HINT_YELLOW
      lcount[guess[i]] -= 1
  return ''.join(result)


def replay_with_hints(guesses_with_hints: list[str]):
  dictionary = list(load_dictionary())
  constraints = WordleConstraint()
  for guess, result in (i.split(':') for i in guesses_with_hints):
    print_annotated_guess(guess, result)
    constraints.update(guess, result)
    print_matches(dictionary, constraints)
    print()

def replay_with_answer(guesses: list[str]):
  """Prints possible matches at each step from unannotated guesses."""
  dictionary = list(load_dictionary())
  constraints = WordleConstraint()
  for guess in guesses[:-1]:
    result = guess_result(guess, guesses[-1])
    print_annotated_guess(guess, result)
    constraints.update(guess, result)
    print_matches(dictionary, constraints)
    print()
  print_annotated_guess(guesses[-1], 'g' * 5)
  print()


def main(argv):
  args = argv[1:]
  arg_sizes = set(map(len, args))
  if arg_sizes == set([5]):
    replay_with_answer(args)
  elif arg_sizes == set([11]):
    replay_with_hints(args)
  else:
    print(f"usage: ./{argv[0]} guess1 guess2 ... answer OR ./{argv[0]} guess1:result1 guess2:result2 ...")


if __name__ == "__main__":
  app.run(main)
