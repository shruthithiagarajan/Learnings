"""Count the lines of a text file that contain a word.

Usage: python word_count.py <file> <word>
"""
import sys


def count_lines_with_word(path, word, ignore_case=True):
    """Return how many lines in the file contain `word` as a substring."""
    if not word:
        raise ValueError("word must not be empty")
    needle = word.lower() if ignore_case else word
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            hay = line.lower() if ignore_case else line
            if needle in hay:
                count += 1
    return count


def main(argv):
    if len(argv) != 3:
        print("usage: word_count.py <file> <word>")
        return 2
    print(count_lines_with_word(argv[1], argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
