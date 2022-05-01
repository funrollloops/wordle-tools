#!/usr/bin/env python3
import re
import os

import requests


def fetch_wordle_html() -> str:
  return requests.get('https://www.nytimes.com/games/wordle/index.html').text


def fetch_main_js() -> str:
  for file in os.listdir():
    if file.startswith('main') and file.endswith('.js'):
      print("Using %s instead of fetching from nytimes.com" % file)
      with open(file) as f:
        return f.read()
  html = fetch_wordle_html()
  js_filename_match = re.search(r'src="(main\.[^.]*\.js)"', html)
  assert js_filename_match, "Failed to extract path to JS from HTML"
  js_filename = js_filename_match.group(1)
  js_full_path = 'https://www.nytimes.com/games/wordle/' + js_filename
  print("Extracted js path", js_full_path)
  js_content = requests.get(js_full_path).text
  with open(js_filename, 'w') as f:
    f.write(js_content)
  print("Downloaded", js_filename)
  return js_content


def parse_main_js():
  js = fetch_main_js()
  arrays = re.findall(r'\["[a-z]{5}"(?:,"[a-z]{5}"){100,}]', js)
  assert len(arrays)==2, "found %s arrays of five letter words instead of two!" % len(arrays)
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
