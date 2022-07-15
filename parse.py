#!/usr/bin/env python3
import re
import os

import requests
from typing import Callable

HTML_CACHE_PATH = 'cache/index.html'
JS_CACHE_PATH = 'cache/wordle.js'


def disk_cache(path: str, fn: Callable[[], str]) -> str:
  try:
    os.mkdir('cache')
  except FileExistsError:
    pass
  if os.path.exists(path):
    print('Using cached', path)
    with open(path) as f:
      return f.read()
  data = fn()
  with open(path, 'w') as f:
    f.write(data)
  return data


def fetch_wordle_html() -> str:
  URL = 'https://www.nytimes.com/games/wordle/index.html'
  return disk_cache('data/index.html', lambda: requests.get(URL).text)


def fetch_main_js() -> str:
  def fetch():
    html = fetch_wordle_html()
    js_filename_match = re.search(r'src="([^"]*wordle\.[^.]*\.js)"', html)
    assert js_filename_match, "Failed to extract path to JS from HTML"
    js_full_path = js_filename_match.group(1)
    print("Extracted js path", js_full_path)
    return requests.get(js_full_path).text

  return disk_cache(JS_CACHE_PATH, fetch)


def parse_main_js():
  js = fetch_main_js()
  arrays = re.findall(r'\["[a-z]{5}"(?:,"[a-z]{5}"){100,}]', js)
  assert len(
      arrays
  ) == 2, "found %s arrays of five letter words instead of two!" % len(arrays)
  answers, guesses = map(eval, arrays)
  print(f"Parsed {len(answers)} answers and {len(guesses)} guesses")
  return sorted(eval(arrays[0]) + eval(arrays[1]))


def main():
  words = parse_main_js()
  print("Writing %s words to words.txt" % len(words))
  with open('words.txt', 'w') as f:
    f.write('\n'.join(words))


if __name__ == "__main__":
  main()
