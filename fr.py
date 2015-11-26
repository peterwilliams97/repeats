from __future__ import division, print_function
import glob, os, re, sys, fnmatch


def recursive_glob(path_pattern):
    """Like glob.glob() except that it sorts directories and
        recurses through subdirectories.
    """
    dir_name, mask = os.path.split(path_pattern)
    if not dir_name:
        dir_name = '.'
    print('!!', dir_name, mask)
    for root, dirs, files in os.walk(dir_name):
        # print(root, dirs, len(files))
        # print(fnmatch.filter(files, mask))
        path_list = sorted(fnmatch.filter(files, mask), key=lambda s: (s.lower(), s))
        for path in path_list:
            full_path = os.path.join(root, path)
            if not os.path.isdir(full_path):
                # print(full_path)
                yield(full_path)


def c_array(word):
    return '{%s}' % str(' ,'.join(['0x%02X' % ord(c) for c in word])).replace("'", '')


PATTERN = r'_(\d+)page.*_(\d+)cop.*\.(spl|content)$'
RE_PATH = re.compile(PATTERN, re.IGNORECASE)

assert len(sys.argv) > 1, 'Usage: python %s <file pattern>' % sys.argv[0]
path_pattern = sys.argv[1]
all_files = [fn for fn in recursive_glob(path_pattern) if RE_PATH.search(fn)]
assert all_files, r'No files in "%s" matching "%s"' % (path_pattern, PATTERN)

BAD_WORDS = {'\xd1\x80',
             '\x00\x00\x00',
             '\xcd\xca\x10',
             '\x00\x00\x18\x00',
             '\x10\x00\x00\x18\x00',
             '\xca\x10\x00\x00\x18',

            '\x80\x00\xD2\x80\x04',
              '\x00\x00\x00',
              '\xd2\x80',
             '\x80'
               }

HEADER = '\xcd\xca\x10\x00\x00\x18'

def trim_header(text):
    header = text.rfind(HEADER)
    if header >= 0:
        # print(text[header:header + 10])
        # assert False
        return text[header:]
    return text


def num_copies(m):
    # return int(m.group(1))
    return int(m.group(1)) * int(m.group(2))


def analyze_files(files):
    # for path in files:
    #     print('%2d %s' % (num_copies(RE_PATH.search(path)), path))
    # exit()
    # Each corpus element is (R, file contents) for file in file name repeats=<R>
    corpus = [(num_copies(RE_PATH.search(fn)),
               trim_header(file(fn, 'rb').read()),
               fn
               )
              for fn in files]

    # Small repeat sizes should filter strings faster so move them to start of list
    corpus.sort(key=lambda x: -len(x[1]) / x[0])

    if False:
        for i, ((n, _), path) in enumerate(zip(corpus, files)):
            print('%3d: %3d: %s' % (i, n, path))

    def valid(words):
        return [w for w in words if all(text.count(w) >= n for n, text, _ in corpus)]

    # words = strings that are repeated >= M times in file name repeats=<M>
    words = chars = valid([chr(i) for i in range(256)])
    while True:
        words1 = set([w + c for w in words for c in chars]
                   + [c + w for w in words for c in chars])
        words1 = {w for w in words1 if not any(b in w for b in BAD_WORDS)}
        words1 = valid([w for w in words1 if w[1:] in words and w[:-1] in words])
        if not words1:
            break
        words = words1

    # exact_words = strings that are repeated exactly R times in file name repeats=<R>
    exact_words = [w for w in words if all(text.count(w) == n for n, text, _ in corpus)]

    # print results
    if exact_words:
        print('exact matches=%d,%d' % (len(exact_words), len(exact_words[0])))
        for i, word in enumerate(exact_words):
            print('%2d: %s' % (i, c_array(word)))
        assert False
    else:
        print('part matches=%d,%d' % (len(words), len(words[0])))
        for i, word in enumerate(words):
            print('%2d: %s %s' % (i, c_array(word), word))
            # for i, ((n, text), path) in enumerate(zip(corpus, files)):
            #     n_found = text.count(word)
            #     print('%5d: %3d - %3d: %s' % (i, n, n_found, path))

            i_n_found_path = [(i, n, text.count(word), len(text), path)
                              for i, (n, text, path) in enumerate(corpus)]
            i_n_found_path.sort(key=lambda k: (-k[2], -k[1], -k[2], k[0]))
            for i, n, n_found, tsize, path in i_n_found_path:
                print('%5d: %3d - %4d - %5d: %s' % (i, n, n_found, tsize, path))
        return tuple(sorted(words))



word_list = []

word_list.extend(analyze_files(all_files))

if True:
    for discard in all_files:
        all_files2 = [path for path in all_files if path != discard]
        for discard2 in all_files2:
            files = [path for path in all_files2 if path != discard2]
            word_list.extend(analyze_files(files))

word_list = sorted(set(word_list))
max_len = max(len(w) for w in word_list)
best_words = [w for w in word_list if len(w) == max_len]
print('-' * 80)
print('%d words. %d best' % (len(word_list), len(best_words)))
for i, word in enumerate(word_list):
     print('%2d: %s %s' % (i, c_array(word), word))




