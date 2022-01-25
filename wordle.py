#!/usr/bin/env python3

import re

# Inputs
# Guesses -- lowercase for yellow, uppercase for green, . for unmatched.
guesses = [
  'ar.s.',
  '...u.',
  #'.ett.',
]
# Put other letters here.
not_present_letters = 'iedont'

assert(all(len(g) == 5 for g in guesses))

pno = [set(not_present_letters) for _ in range(5)]

for i in range(5):
  for g in guesses:
    if g[i].islower():
      pno[i].add(g[i])

r = [f'[^{"".join(s)}]' for s in pno]
for i in range(5):
  for g in guesses:
    if g[i].isupper():
      r[i] = g[i].lower()
pat = re.compile(''.join(r))

req = set(c for g in guesses for c in g if c.islower()).difference(set(
  c.lower() for g in guesses for c in g if c.isupper()))

with open('/usr/share/dict/words') as f:
  for word in (l.strip() for l in f):
    if word.islower() and pat.fullmatch(word) and all(r in word for r in req):
      print(word)
