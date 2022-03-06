#!/usr/bin/env python3
from collections import defaultdict
import os
import re

words3 = set()
words4 = set()
words5 = set()

dir = os.path.dirname(__file__)
path = os.path.join(dir, 'words.txt')
with open(path) as f:
  for word in map(str.strip, f):
    if len(word) == 3:
      words3.add(word)
    if len(word) == 4:
      words4.add(word)
    elif len(word) == 5:
      words5.add(word)

freqs = defaultdict(lambda: 0)
freqsi = [defaultdict(lambda: 0) for _ in range(5)]
nwords = 0
nplurals = 0
nonwords = 0
npast = 0

for word in words5:
  if not re.match('[a-z]{5}', word):
    #print('skipping invalid word', word)
    nonwords += 1
    continue
  if word[-2:] == 'ed' and word[:3] in words3:
    npast += 1
    continue
  if word[4] == 's' and word[:4] in words4:
    #print('skipping', word)
    nplurals += 1
    continue
  nwords += 1
  for i, c in enumerate(word):
    freqsi[i][c] += 1
  for c in set(word):
    freqs[c] += 1

def most_common(d):
  freq_order = sorted([(v, k) for k, v in d.items()], reverse=True)
  return freq_order

mc = most_common(freqs)
mci = [most_common(f) for f in freqsi]

print()
print("5-letter words (before filtering):", len(words5))
print("skipped nonwords:", nonwords)
print("skipped past tense:", npast)
print("skipped plurals:", nplurals)
print("valid words:", nwords)
print()
print(' '.join('%6s' % c for c in '*01234'))
for t in zip(mc, *mci):
  print(' '.join(f'{f:4} {c}' for f, c in t))
