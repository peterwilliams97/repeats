# -*- coding: latin-1 -*-
"""
    Make test files for  https://github.com/peterwilliams97/repeats

"""
from __future__ import division, print_function
import random
import os
import sys


def make_random_string(size):
    return ''.join(chr(random.randint(ord('a'), ord('z'))) for _ in xrange(size))


# REPEATED_STRING is the string the repeated string finder are supposed to find
REPEATED_STRING = 'THE LONG LONG LONG REPEATED STRING THAT KEEPS ON GOING AND GOING AND GOING'
assert '"' not in REPEATED_STRING, 'REPEATED_STRING cannot contain "'

count = 0


def repeated_string():
    global count
    s = '^%d%s%d$' % (count, REPEATED_STRING, count + 1)
    count += 2
    return s


def make_page(page_size):
    background = make_random_string(page_size)
    pattern = repeated_string()
    b = (page_size - len(pattern)) // 2
    e = b + len(pattern)
    assert 0 <= b < e <= page_size
    text = background[:b] + pattern + background[e:-1] + '\n'
    assert len(text) == page_size
    return text


def make_repeats_doc(doc_size, n_repeats):
    size = doc_size
    pages = []
    for n in xrange(n_repeats, 0, -1):
        page_size = size // n
        pages.append(make_page(page_size))
        size -= page_size
    return ''.join(pages)


def make_repeats_file(directory, doc_size, n_repeats):
    path = os.path.join(directory, 'repeats=%d.txt' % n_repeats)
    path = os.path.abspath(path)
    repeats_doc = make_repeats_doc(doc_size, n_repeats)
    file(path, 'wb').write(repeats_doc)
    return path

KBYTE = 1024
MBYTE = KBYTE ** 2
GBYTE = KBYTE ** 3


def main():
    # The Nelson!
    random.seed(111)

    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' [options]')
    parser.add_option('-r', '--min-repeats', dest='min', default='11', help='min num of repeats')
    parser.add_option('-n', '--number', dest='num', default='5', help='number of documents')
    parser.add_option('-s', '--size', dest='size', default='1.0',
                      help='size of each document in MBytes')
    parser.add_option('-d', '--directory', dest='directory', default='.',
                      help='Directory to create file in')

    options, args = parser.parse_args()

    doc_size = int(float(options.size) * MBYTE)
    min_repeats = int(options.min)
    n_documents = int(options.num)
    directory = options.directory

    print('# size = %.3f Mbyte' % (doc_size / MBYTE))
    print('# min_repeats = %d' % min_repeats)
    print('# n_documents = %d' % n_documents)
    print('# directory = "%s"' % directory)
    print('# REPEATED_STRING = "%s", len=%d' % (REPEATED_STRING, len(REPEATED_STRING)))
    print('# %s' % ('-' * 80))

    for n_repeats in xrange(min_repeats, min_repeats + n_documents):
        path = make_repeats_file(directory, doc_size, n_repeats)
        print('%s  # %2d repeats' % (path, n_repeats))

main()

