from __future__ import division, print_function
import glob, os, re, sys, fnmatch
from itertools import product


def s2l(word):
    return [ord(c) for c in word]


def l2s(lst):
    return ''.join(chr(x) for x in lst)


def c_array(word):
    return '{%s}' % str(' ,'.join(['0x%02X' % ord(c) for c in word])).replace("'", '')


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


PATTERN = r'_(\d+)page.*_(\d+)cop.*\.(spl|content)$'
RE_PATH = re.compile(PATTERN, re.IGNORECASE)

assert len(sys.argv) > 1, 'Usage: python %s <file pattern>' % sys.argv[0]
path_pattern = sys.argv[1]
all_files = [fn for fn in recursive_glob(path_pattern) if RE_PATH.search(fn)]
assert all_files, r'No files in "%s" matching "%s"' % (path_pattern, PATTERN)


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

corpus = [(num_copies(RE_PATH.search(fn)),
           trim_header(file(fn, 'rb').read()),
           fn
           )
          for fn in all_files]

# Small repeat sizes should filter strings faster so move them to start of list
corpus.sort(key=lambda x: -len(x[1]) / x[0])

BAD_WORDS = {
    '\xd1\x80',
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

good_words = set()

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
        for w in words:
            good_words.add(w)

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
        for w in words:
            assert w in good_words
        return tuple(sorted(words))


if True:
    word_list = []

    word_list.extend(analyze_files(all_files))

    if False:
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

    good_words = sorted(good_words, key=lambda w: (-len(w), w))
    good_words_list = [s2l(w) for w in good_words]
    with open('good.words', 'wt') as f:
        f.write(repr(good_words_list))


def get_subwords(base_words):

    subwords = set()
    for base_word in base_words:
        n = len(base_word)
        for b in xrange(n):
            for e in xrange(b + 1, n + 1):
                subwords.add(base_word[b:e])
    return subwords


if False:
    base_word = 'ABC'
    base_words = [
        '\x04\x47\xE8\xA5',
        '\xE1\x01\xD7\xA0'
        ]
    subwords = get_subwords(base_words)
    for i, word in enumerate(sorted(subwords, key=lambda w: (-len(w), w))):
        print(i, c_array(word))
    subwords = sorted(subwords, key=lambda w: (-len(w), w))
    subword_pairs = list(product(subwords, subwords))

    def key_pair(s1, s2):
        return -(len(s1) + len(s2)), -len(s1), s1, s2

    subword_pairs.sort(key=lambda k: key_pair(*k))

    for i, (s1, s2) in enumerate(subword_pairs):
        print('%3d: %s' % (i, (c_array(s1), c_array(s2))))
    exit()


def find_sequence(corpus, base_words):
    """
        Build sequences from substrings of work
    """

    def is_allowed(s1, n, s2):
        regex = re.compile('%s.{%d}%s' % (s1, n, s2))
        good = all(len(regex.findall(text)) == n for n, text, _ in corpus)
        part = all(len(regex.findall(text)) >= n for n, text, _ in corpus)
        return good, part

    subwords = get_subwords(base_words)
    subwords = sorted(subwords, key=lambda w: (-len(w), w))
    sequences = [(s1, n, s2)
                 for n in xrange(0, 50)
                 for s1, s2 in product(subwords, subwords)]

    def key_sequence(s1, n, s2):
        return -(len(s1) + len(s2)), n, -len(s1), s1, s2

    sequences.sort(key=lambda k: key_sequence(*k))

    good_sequences = []
    part_sequences = []

    for seq in sequences:
        good, part = is_allowed(*seq)
        if good:
            good_sequences.append(seq)
        if part:
            part_sequences.append(seq)

    print('good', len(good_sequences))
    for i, seq in enumerate(good_sequences):
        print(i, seq)
    print('part', len(part_sequences))
    for i, (s1, n, s2),  in enumerate(part_sequences):
        print(i, len(s1) + len(s2), c_array(s1), n, c_array(s2))


def s_seq3(s1, n2, s2, n3, s3):
    return s1 + '.' * n2  + s2 + '.' * n3 + s3


def get_regex3(s1, n2, s2, n3, s3):
    e1, e2, e3 = [re.escape(s) for s in s1, s2, s3]

    if s3:
        pattern = '%s.{%d}%s.{%d}%s' % (e1, n2, e2, n3, e3)
    elif s2:
        pattern = '%s.{%d}%s' %  (e1, n2, e2)
    else:
        pattern = s1

    try:
        return re.compile(pattern)
    except:
        print('pattern="%s"' % pattern, file=sys.stderr)
        raise


def find_sequence3(corpus, base_words, max_gap=20, fuzz=0):
    """
        Build sequences from substrings of work
    """

    def is_allowed3(s1, n2, s2, n3, s3):
        regex = get_regex3(s1, n2, s2, n3, s3)
        _part = all(len(regex.findall(text)) >= n for n, text, _ in corpus)
        _good = _part and all(len(regex.findall(text)) == n for n, text, _ in corpus)
        # return good, part

        counts = {}
        n_part = 0
        is_part = True
        for i, (n, text, path) in enumerate(corpus):
            assert n > 0, path
            counts[i] = len(regex.findall(text))
            if counts[i] >= n:
                n_part += 1
            if i + 1 > n_part + fuzz:
                is_part = False
                assert not _part, (i, (n_part, i + 1), fuzz, counts)
                break
        if is_part:
            assert n_part >= len(corpus) - fuzz, (n_part, (len(corpus), i), fuzz, )

        if fuzz == 0:
            assert is_part == _part, (is_part, _part)
        elif _part:
            assert is_part, (is_part, _part)


        n_good = 0
        is_good = is_part
        if is_good:
            for i, (n, text, path) in enumerate(corpus):
                assert n > 0, path
                counts[i] = counts.get(i, len(regex.findall(text)))
                if counts[i] == n:
                    n_good += 1
                if i + 1 > n_good + fuzz:
                    is_good = False
                    break
        if is_good:
            assert n_good >= len(corpus) - fuzz

        if fuzz == 0:
            assert is_good == _good, (is_good, _good)
        elif _good:
            assert is_good, (is_good, _good)

        if is_good:
            assert is_part
            print('@!@', n_part, n_good)
            print('@@@', counts)
            for i, (n, text, path) in enumerate(corpus):
                print(i, n, counts[i], len(regex.findall(text)))
            assert False
            # print('good', c_array(s_seq3(s1, n2, s2, n3, s3)),
            #                       s_seq3(s1, n2, s2, n3, s3))
            # assert False

        return is_good, is_part

    print('%d base_words' % len(base_words))
    subwords = get_subwords(base_words)
    print('%d subwords' % len(subwords))
    subwords = sorted(subwords, key=lambda w: (-len(w), w))
    max_word = max(len(w) for w in subwords)
    subwordsb = subwords + ['']
    subword_product = [(s1, s2, s3)
                       for s1, s2, s3 in product(subwords, subwordsb, subwordsb)
                       if len(s1) + len(s2) + len(s3) >= max_word + 1
                      ]
    # s1       or
    # s1 s2    or
    # s1 s2 s3
    subword_product = [(s1, s2, s3) for s1, s2, s3 in subword_product if s2 != '' or s3 == '']
    for s1, s2, s3 in subword_product:
        if s3:
            assert s2
        assert s1
    # bw2 = {s1 for s1, s2, s3 in subword_product if s2 == '' and s3 == ''}
    # for w in base_words:
    #     assert w in bw2, c_array(w)

    print('%d=%.3fM subword_product' % (len(subword_product), len(subword_product) * 1e-6))

    n_product = [(n2, n3) for n2, n3 in product(xrange(1, max_gap + 1), xrange(1, max_gap + 1)) if n2 + n3]
    print('%d n_product' % len(n_product))

    sequences = [(s1, n2, s2, n3, s3)
                 for (n2, n3), ( s1, s2, s) in product(n_product, subword_product)]

    print('%d=%.3fM sequences 1' % (len(sequences), len(sequences) * 1e-6))

    sequences = [(s1, n2, s2, n3, s3) for s1, n2, s2, n3, s3 in sequences if n2 + n3]
    print('%d=%.3fM sequences 2' % (len(sequences), len(sequences) * 1e-6))

    for seq in sequences:
        assert len(seq) == 5, seq

    # for i, (s1, n2, s2, n3, s3) in enumerate(sequences):
    for i, seq in enumerate(sequences):
        assert len(seq) == 5, (i, seq)
        (s1, n2, s2, n3, s3) = seq
        if not s3:
            sequences[i] = s1, n2, s2, 0, s3
        if not s2:
            sequences[i] = s1, 0, s2, n3, s3

    for seq in sequences:
        assert len(seq) == 5, seq

    sequences = list(set(sequences))
    for seq in sequences:
        assert len(seq) == 5, seq

    print('%d=%.3fM sequences 3' % (len(sequences), len(sequences) * 1e-6))

    def key_sequence(s1, n2, s2, n3, s3):
        return -(len(s1) + len(s2) + len(s3)), n2 + n3, -len(s1), n2, s1, s2, s3

    print('%d=%.3fM sequences 4' % (len(sequences), len(sequences) * 1e-6))
    sequences.sort(key=lambda k: key_sequence(*k))
    print('%d=%.3fM sequences 5' % (len(sequences), len(sequences) * 1e-6))

    good_sequences = []
    part_sequences = []

    n_shown = 0
    for seq in sequences:
        good, part = is_allowed3(*seq)
        if good:
            # print(good)
            # assert False
            good_sequences.append(seq)
        if part:
            part_sequences.append(seq)
            if n_shown <= len(part_sequences) < 20:
                for i, (s1, n2, s2, n3, s3) in enumerate(part_sequences[n_shown:20]):
                    print(i + len(part_sequences) - 1,
                          len(s1) + len(s2) + len(s3),
                         c_array(s1),
                         n2, c_array(s2),
                         n3, c_array(s3))
                n_shown = len(part_sequences)
            break # !@#$
        if good:
            break

    print('good', len(good_sequences))
    for i, (s1, n2, s2, n3, s3) in enumerate(good_sequences[:20]):
        print(i,
             len(s1) + len(s2) + len(s3),
             c_array(s1),
             n2, c_array(s2),
              n3, c_array(s3))
    print('part', len(part_sequences))
    for i, (s1, n2, s2, n3, s3) in enumerate(part_sequences[:20]):
        print(i,
             len(s1) + len(s2) + len(s3),
             c_array(s1),
             n2, c_array(s2),
             n3, c_array(s3))

    return good_sequences, part_sequences


# base_words = [
#     '\x04\x47\xE8\xA5',
#     '\xE1\x01\xD7\xA0'
#     ]

good_sequences, part_sequences = find_sequence3(corpus, good_words)


def print_sequences3(name, sequence_list):
    good_sequences = part_sequences = None

    print('%s sequence matches=%d' % (name, len(sequence_list)))
    for i, seq in enumerate(sequence_list[:3]):
        print('%2d: %s %s' % (i, c_array(s_seq3(*seq)), s_seq3(*seq)))
        # for i, ((n, text), path) in enumerate(zip(corpus, files)):
        #     n_found = text.count(word)
        #     print('%5d: %3d - %3d: %s' % (i, n, n_found, path))
        regex = get_regex3(*seq)

        i_n_found_path = [(i, n, len(regex.findall(text)), len(text), path)
                          for i, (n, text, path) in enumerate(corpus)]
        i_n_found_path.sort(key=lambda k: (-k[2], -k[1], -k[2], k[0]))
        for i, n, n_found, tsize, path in i_n_found_path:
            print('%5d: %3d - %4d - %5d: %s' % (i, n, n_found, tsize, path))


print_sequences3('good', good_sequences)
print_sequences3('part', part_sequences)


