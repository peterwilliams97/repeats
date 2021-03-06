from __future__ import division, print_function
import glob
import re
import sys

PATTERN = r'repeats=(\d+)'

assert len(sys.argv) > 1, 'Usage: python %s <file pattern>' % sys.argv[0]
file_pattern = sys.argv[1]
files = [fn for fn in glob.glob(file_pattern) if re.search(PATTERN, fn)]
assert files, r'No files in "%s" matching "%s"' % (file_pattern, PATTERN)

# Each corpus element is (R, file contents) for file in file name repeats=<R>
corpus = [(int(re.search(PATTERN, fn).group(1)), file(fn, 'rb').read()) for fn in files]

# Small repeat sizes should filter strings faster so move them to start of list
corpus.sort(key=lambda x: -len(x[1]) / x[0])


def valid(words):
    return [w for w in words if all(text.count(w) >= n for (n, text) in corpus)]

# words = strings that are repeated >= M times in file name repeats=<M>
words = chars = valid([chr(i) for i in range(256)])
while True:
    words1 = set([w + c for w in words for c in chars] +
                 [c + w for w in words for c in chars])
    words1 = valid([w for w in words1 if w[1:] in words and w[:-1] in words])
    if not words1:
        break
    words = words1


# exact_words = strings that are repeated exactly R times in file name repeats=<R>
exact_words = [w for w in words if all(text.count(w) == n for (n, text) in corpus)]


def c_array(word):
    return '{%s}' % str(' ,'.join(['0x%02X' % ord(c) for c in word])).replace("'", '')

# print results
print('  all matches=%d,length=%d' % (len(words), len(words[0]) if words else -1))
print('exact matches=%d,length=%d' % (len(exact_words), len(exact_words[0]) if exact_words else -1))

for i, word in enumerate(words[:3]):
    print('%5d: %s\n"%s"' % (i, c_array(word), word))
