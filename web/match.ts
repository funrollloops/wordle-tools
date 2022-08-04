import { WORDS } from "./words";

function assert(b: boolean, msg: string) {
  if (!b) {
    throw msg;
  }
}

const HINT_GREEN = 2;
const HINT_YELLOW = 1;
const HINT_GRAY = 0;
const CHAR_CODE_A = "a".charCodeAt(0);

const PACKED_WORDS: Uint32Array = (function () {
  var buf = new Uint32Array(WORDS.length / 5);
  for (var wi = 0, bi = 0; wi < WORDS.length; wi += 5, bi++) {
    buf[bi] =
      ((WORDS.charCodeAt(wi) - CHAR_CODE_A) << 0) |
      ((WORDS.charCodeAt(wi + 1) - CHAR_CODE_A) << 5) |
      ((WORDS.charCodeAt(wi + 2) - CHAR_CODE_A) << 10) |
      ((WORDS.charCodeAt(wi + 3) - CHAR_CODE_A) << 15) |
      ((WORDS.charCodeAt(wi + 4) - CHAR_CODE_A) << 20);
  }
  return buf;
})();

function decode_word(word: number): string {
  return String.fromCharCode(
    CHAR_CODE_A + (word & 0x1f),
    CHAR_CODE_A + ((word >>> 5) & 0x1f),
    CHAR_CODE_A + ((word >>> 10) & 0x1f),
    CHAR_CODE_A + ((word >>> 15) & 0x1f),
    CHAR_CODE_A + ((word >>> 20) & 0x1f)
  );
}

class Matcher {
  min = new Uint8Array(26);
  max = new Uint8Array(26);
  // One 32-bit int per position; each entry is a bitset representing the set
  // of disallowed characters.
  disallowed_at = new Uint32Array(5);
  local_min = new Uint8Array(26);
  local_saw_gray = new Uint32Array(1);

  constructor() {
    this.max.fill(5);
  }

  update(this: Matcher, word: string, result: Uint8Array) {
    assert(word.length == 5 && result.length == 5, "inputs have wrong len");
    this.local_min.fill(0);
    this.local_saw_gray.fill(0);
    for (var i = 0; i < 5; ++i) {
      const chr = word.charCodeAt(i) - CHAR_CODE_A;
      assert(chr >= 0 && chr < 26, "word has invalid chars");
      if (result[i] == HINT_GREEN) {
        assert(
          (this.disallowed_at[i] & (1 << chr)) == 0,
          "green hint but position disallowed"
        );
        this.disallowed_at[i] = ~(1 << chr);
        this.local_min[chr] += 1;
      } else if (result[i] === HINT_YELLOW) {
        this.disallowed_at[i] |= 1 << chr;
        this.local_min[chr] += 1;
      } else {
        assert(result[i] == HINT_GRAY, "bad hint " + result[i]);
        this.local_saw_gray[0] |= 1 << chr;
      }
    }
    for (var chr = 0; chr < 26; ++chr) {
      if (this.local_saw_gray[0] & (1 << chr)) {
        assert(this.min[chr] <= this.local_min[chr], "min increased?");
        this.max[chr] = this.local_min[chr];
      }
      if (this.min[chr] < this.local_min[chr])
        this.min[chr] = this.local_min[chr];
    }
  }

  match(this: Matcher, word: number): boolean {
    var local_count = this.local_min;
    local_count.fill(0);
    for (var i = 0; i < 5; ++i) {
      const chr = word & 0x1f;
      if (this.disallowed_at[i] & (1 << chr)) return false;
      local_count[chr] += 1; // Count occurrences of character.
      word = word >>> 5;
    }
    // Check non-positional character count constraints.
    for (var chr = 0; chr < 26; ++chr)
      if (local_count[chr] < this.min[chr] || local_count[chr] > this.max[chr])
        return false;
    return true;
  }
}

function print_annotated_guess(guess: string, result: Uint8Array) {
  var s = "\x1b[1;38;2;255;255;255m";
  for (var i = 0; i < 5; ++i) {
    if (result[i] == HINT_GREEN) s += "\x1b[48;2;106;170;100m";
    else if (result[i] == HINT_YELLOW) s += "\x1b[48;2;201;180;88m";
    else s += "\x1b[48;2;120;124;126m";
    s += " " + guess[i] + " ";
  }
  console.log(s + "\x1b[0m");
}
function print_matches(matcher: Matcher, limit: boolean) {
  var num_matches = 0;
  var line = "";
  for (var i = 0; i < PACKED_WORDS.length; i++) {
    if (!matcher.match(PACKED_WORDS[i])) continue;
    num_matches += 1;
    if (!limit || num_matches <= 13 * 5) {
      line += decode_word(PACKED_WORDS[i]);
      if (num_matches % 13 == 0) {
        console.log(line);
        line = "";
      } else {
        line += " ";
      }
    } else if (num_matches == 13 * 5 + 1) {
      console.log("…");
    }
  }
  if (line.length > 0) {
    console.log(line);
  }
  console.log(num_matches, "matches");
}

function generate_hint(guess: string, answer: string): Uint8Array {
  assert(guess.length == 5 && answer.length == 5, "incorrect length");
  var hint = new Uint8Array(5);
  var ans_count = new Uint8Array(26);
  for (var i = 0; i < 5; ++i) {
    const code = answer.charCodeAt(i);
    if (guess.charCodeAt(i) == code) hint[i] = HINT_GREEN;
    ans_count[code - CHAR_CODE_A]++;
  }
  for (var i = 0; i < 5; ++i) {
    const chr = guess.charCodeAt(i) - CHAR_CODE_A;
    if (hint[i] != HINT_GREEN && ans_count[chr] > 0) {
      hint[i] = HINT_YELLOW;
      ans_count[chr]--;
    }
  }
  return hint;
}

function replay_with_answer(guesses: Array<string>) {
  var m = new Matcher();
  var answer = guesses[guesses.length - 1];
  guesses.slice(0, -1).forEach((guess) => {
    const hint = generate_hint(guess, answer);
    print_annotated_guess(guess, hint);
    m.update(guess, hint);
    print_matches(m, true);
    console.log();
  });
  print_annotated_guess(answer, generate_hint(answer, answer));
  console.log();
}

function main(args: string[]) {
  replay_with_answer(args);
}

main(process.argv.slice(2));
