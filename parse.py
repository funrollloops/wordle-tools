#!/usr/bin/env python3

with open('main.4d41d2be.js') as f:
  d = f.read()


def extract_array(prefix):
  begin = d.find(prefix)
  end = d.find(']', begin)
  return eval(d[begin + len(prefix) : end + 1])


ANSWERS="var Ma="
GUESSES= ",Oa="

with open('words.txt', 'w') as f:
  f.write('\n'.join(
    sorted(extract_array("var Ma=") + extract_array(",Oa="))
  ))
