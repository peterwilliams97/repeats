Finding Longest Repeated Substring in Documents
===============================================

Background
----------
There is a problem that comes up often in my work:

- There are some documents in an unknown language, usually some simple computer language of the
complexity of XML or JSON.
- The document contains some sub-units. e.g. Page, records.
- We want to be able to detect the number of these sub-units in all documents written in this
language.
- We are able to create documents and can set the number of sub-units when we create them.

If a [subsequence](http://en.wikipedia.org/wiki/Subsequence) of bytes that identifies each
instance of a sub-unit in a document can be found then it possible to deduce the number sub-units in
new documents by counting the number of instances of the subsequence in those documents.

The first step towards finding these subsequences is to find the
[substrings](http://en.wikipedia.org/wiki/Substring) they contain.

The Problem
-----------

This project looks at some methods for finding the longest substring that is repeated a
specified number of times in each document in a corpus. Formally:

    Find the longest substring that occurs num[d] times in documents doc[d] for d = 1..D

There are many [highly efficient methods](http://bit.ly/OKukL3) for finding substrings. I will be
starting out by trying some simple methods here in order to:

- Get a feel for the difficulty of the problem first-hand and
- To create a benchmark to compare other methods to.

In particular I am avoiding
[generalized suffix tree](https://github.com/peterwilliams97/repeats/tree/master/suffix.md)
methods for now. I look at these later.

- `|s|` is the number of bytes in document s in the following.
- string and document are used interchangibly

The Basic Idea
--------------
The naive solution for finding the longest substring that occurs >= num[d] times in documents
doc[d] for d = 1..D is hopelessly inefficient.

    longest_s = ''
    for d in 1..D:
        for all substrings s of length 1..|doc[d]| / num[d] in doc[d]:
            for e in 1..D:
                if s occurs num[e] times in doc[e] and |s| > |longest_s|:
                    longest_s = s


This would take time proportional to

    D * (|doc[d]| / num[d])^2 * corpus_size
    where corpus_size = sum(|doc[d]|: d in 1..D)

For a corpus of 20 x 10 MB documents with 5 repeats per document and, say, one innermost
compute operation (a single byte comparison in a string search) of 10^-9 sec this would be

    20 * (2 * 10^7)^2 * 2 * 10^8 * 10^-9 sec
    = 10^24 * 10^-9
    = 10^15 sec
    = 10^8 years

We can do much better than this by observing that for each substring s of length m
that occurs >= num[d] times, all substrings of s must also occur >= num[d] times.

Therefore we can build a list of substrings recursively with the following
[branch and bound](http://en.wikipedia.org/wiki/Branch_and_bound) procedure.

    valid_strings[m] = strings of length m that occur required number of times

    # Compute valid_strings[1] by checking number of occurrences of each byte in the docs
    for m in 1..|doc[d]| / num[d]:
        valid_strings[m + 1] = [s + b: for s in valid_strings[m] for b in valid_strings[1]]
                             + [b + s: for s in valid_strings[m] for b in valid_strings[1]]
        remove duplicate strings from valid_strings[m + 1]
        remove strings that do not occur required number of times from valid_strings[m + 1]l
        if len(valid_strings[m + 1]) == 0:
            # At this point the longest substring(s) that occured >= sufficient times was length m
            Back-track through valid_strings[k] k = m, m - 1,.. to find longest substring(s) that
            occured exactly num[d] times in doc[d] for d in 1..D
            return valid_strings[k]

Implementation
--------------
This is implemented in the Python files in this directory.
[fr.py](https://github.com/peterwilliams97/repeats/blob/master/fr.py) is a terse implementation
of the above pseudo-code while
[find_repeats.py](https://github.com/peterwilliams97/repeats/blob/master/find_repeats.py) is
 more verbose but otherwise works exactly the same.

    Usage:
        python fr.py <file mask>
        python find_repeated.py <file mask>

This directory also contains a script
[make_repeats.py](https://github.com/peterwilliams97/repeats/blob/master/make_repeats.py)
to make sample documents with repeated substrings

    Usage:
        python make_repeats.py

Performance of the Basic Solution
---------------------------------
The above code usually runs fast enough enough for me with the documents I work on because I
choose documents that have:

* small repeat size (size of document / number of repeats).
* a lot of variety between documents.

The variety of documents reduces the number and size of substrings that occur the required
number of times in all the documents by chance.

The typical behavior I see is

* |valid_strings[1]| tends to be 50 - 100 (compared to a possible maxium of 256)
* |valid_strings[m]| m > 1 tends not to increase much with m. It tends to stay < 1000 for m = 2..5
then decrease
* once |valid_strings[m]| starts to decrease with increasing m, convergence follows fast

The Python solution spends most of its time searching for substrings in documents so
its running time is proportional to the number of bytes searched:

    typical bad case <= 5 * 1000 * (number of bytes in all documents)
    typical good case <= 3 * 200 * (number of bytes in all documents)

This gives the follow estimated running times on the typical corpora that I use which have sizes of
10 to 100 MByte for the whole corpus. String searching is assumed to run at 500 MByte/sec
which is within factor of 2 of the actual speed.

    typical bad case (100 MByte) : 5 * 1000 * 10^8 / (5 * 10^8) = 1000 seconds = 17 minutes
    typical good case (100 MByte) : 5 * 200 * 10^8 / (5 * 10^8) = 120 seconds = 2 minutes
    typical good case (10 MByte): 3 * 200 * 10^7 / (5 * 10^8) = 12 seconds

These are in fact the sort of running times I see.

Problems with the Basic Solution
--------------------------------
While [fr.py](https://github.com/peterwilliams97/repeats/blob/master/fr.py) performs well for
well-chosen documents, its worst case performance is bad.

Worst case performance happens on large documents with little structure outside the repeated
patterns. In this case

    len(valid_strings[1]) is ~ 256
    len(valid_strings[m]) grows at 256^m to its limit of doc.size / m / num.repeats,
    e.g 30^7 /3 /10 = 1,000,000 for a 30 MByte document with 10 repeats where it reaches
        its maximum at m = 3 for a corpus of 10 x 30 MByte documents,
        300 MBytes of data would need to be searched 1,000,000 times which is
        approx 3 * 10^14 bytes of searching.
    This would take days or weeks on my PC which can do < 10^9 string comparisons/sec
    for data that is too big to fit in cache.

A Solution with Better Worst-Case Performance
---------------------------------------------
The big problem with the basic solution is that the number of substring searches grows too fast.
This doesn't have to happen.

After all, every occurrence of every string in valid_strings[m + 1] in each document starts with
a string from valid_strings[m] by construction. Therefore the total number of occurrences of
every string in valid_strings[m + 1] in each document must be less than or equal to the total
number of occurrences of the string in valid_strings[m] that it was based on.

The problem with our basic solution is that it searches all of each document for every substring
which takes time proportional to |valid_strings[m + 1]| * |doc|
It is possible to do this search by scanning each document only once if we store the offsets
of all occurrences of every substring from valid_strings[m + 1] in each document then search only
from the start or end of that
substring. This removes the |valid_strings[m + 1]| multiplier from the search time.

A well-known way of storing documents in this way is an
[inverted index](http://en.wikipedia.org/wiki/Inverted_index).
There is a c++ implementation of an inverted index specialized for matching repeated substrings in
[inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp)

In inverted_index.cpp,

    inverted_index._postings_map[s]._offsets_map[d]
    is a vector of offsets of substring s in document number d

The inverted_index of strings of length 1 stores the entire contents of the corpus
of documents. Each offset is 4 bytes long so the inverted index takes 4 bytes to store every byte
in the corpus.

This 4-fold increase in storage size gives us a big advantage. As we construct
valid_strings[m + 1] from valid_strings[m], the worst case search time does not increase
exponentially with m as before. In fact it does not increase much at all.

To go from valid_strings[m] to valid_strings[m + 1]:

    construct all valid substrings of length m + 1
        inverted_index._postings_map[s1]_offsets_map[d] for all s1 in valid_strings[m + 1]
    from all valid substrings of length m
        inverted_index._postings_map[s]_offsets_map[d] for all s in valid_strings[m]
    by appending all valid substrings of length 1 (bytes)
        inverted_index._postings_map[b]_offsets_map[d] for all b in valid_strings[1]

This is the algorithm from _Basic Solution_ above converted to inverted indexes with
the additional overhead of updating the inverted index in each step of increasing `m`, the
length substrings being checked.

Since the number of substrings of length `m` in a document of length `n` is `<= n - m + 1`

* The total number of offsets stored for each document `d` is `<= |doc[d]| - m + 1`

Therefore

* The length of each vector of offsets decreases as m increases

(There is some implementation-dependent overhead required for tracking each vector of offsets:
number of valid substrings x cost of storing each vector of offsets. We will ignore this for now.)

The growth in processing time with `m` depends on how long it takes to construct the vector of
offsets of valid length `m + 1` substrings from the vector of offsets of valid length `m` substrings.

We construct the vectors of offsets of the length `m + 1` substrings from the vectors of offsets
of the length `m` substrings by
"[merging](http://www.sorting-algorithms.com/merge-sort)" the sorted
length `m` substrings with the sorted length `1` substrings. These vectors are sorted because the
vector of offsets of the length `1` substrings is constructed in sorted order as it is built
by scanning documents and merging preserves order (see the above references or get_sb_offsets()
in [inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp)).

Worst-Case Performance of the Merge Solution
--------------------------------------------
    Assume a document has length n with r repeats
    It will take O(n) time to read the document and construct the inverted index.
    The mth merge joins n / 256 bytes with n / (256^m) strings * 256^m times
        = O(n * (1 / 256 +1 / (256^m)) * 256^m)
        = O(m * (256^(m - 1)))

This is still exponential in `m`, the length of the substrings being tested for repeats!

Does this matter?

Clearly it matters if `m` is large. Therefore we need to estimate the largest `m` we will see in
real problems.

This is straightforward to calculate for our worst case which is the maximum number of unique
substrings `m: 256^m == size of repeat == n/r or m == log256(n / r)`

    10 MByte document with 10 repeats ==> m = 3
    100 MByte document with 100 repeats ==> m = 3.2

The documents that I test are usually less than 10 MByte so `n * (256^(m - 1)) is n * (256^2) =
n * 6500` gives a processing time of seconds on a 3 GHz computer. Therefore simple merging should
work reasonably well. This is marked as `INNER_LOOP==1` in
[inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp)

However we can do better.

Recall that we are merging `n / 256` bytes with `n / (256^m)` strings `256^m` times. Stepping through
the `n / (256^m)` strings `256^m` times takes constant time with respect to `m` because the `256^m`
factors cancel out. The problem is the stepping through the constant number of bytes `256^m` times.

The byte offsets are sorted so we don't need to step linearly. We can

* divide the bytes offsets into equal regions each the length of the number of substrings then
* linearly step through the string offsets and
* binary search the region of bytes.

(See `INNER_LOOP==4` in
[inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp)
which does this in a slightly cleverer way.)

    The length of each byte offset region is
        (1/256) / (1/(256^m)) = 256^(m - 1),
    so the binary search time is
        O(log(256^(m - 1))) = O(m)

The total search time is

    O(n * (S + B * m)) where S and B are constants.
        S = time for stepping through the substring offsets and
        B = time for stepping through the byte offsets.
    = O(nm)

* The search time for substrings of length `m` stops growing when `m` reaches the maximum number of
valid unique substrings at `m = log256(n / r)`
* Do there is linear growth in search time with the lengths of substring until the peak is reached.
* This happens at `m = 4` for documents with 4 GByte per repeat.

4 GByte per repeat is bigger than I ever expect to see so this should be more than adequate

[Results](https://github.com/peterwilliams97/repeats/tree/master/results)
-------
A simple worst case of single file of 30 MByte and 5 repeats

<table>
    <tr>
        <th>Stage</th><th>Number substrings</th><th>Time (sec)</th>
    </tr>
    <tr>
        <td>Make inverted index m=1</td><td>256</td><td>0.6</td>
    </tr>
    <tr>
        <td>m=2 from m=1</td><td>65,536</td><td>78.0</td>
    </tr>
    <tr>
        <td>m=3 from m=2</td><td>16,777,216</td><td>1049</td>
    </tr>
    <tr>
        <td>m=4 from m=3</td><td>27,496,780</td><td>165</td>
    </tr>
</table>

After the m=4 round, the number of valid substrings started decreasing rapidly and convergence
followed in 0.3 seconds.

The large number of offsets vectors uses a lot of memory, around 1 GByte for 27 million vectors.
We could reduce memory usage by replacing stl vectors with our own custom data structures.
In practice I never see worst-case corpora of this size so I am not going to make that change
now.

Conclusion
----------

The practical value of the solutions discussed above is:

* The naive solution for finding repeated substrings is impractical.
* The basic Python branch and bound solution has worked well for most corpora that I
have tested but I have had to be careful about constructing each corpus.
* The c++ inverted index solution with linear merging processes badly constructed
corpora of the sizes that I am currently using in acceptable times.
* The c++ inverted index solution with binary merging should process badly constructed
corpora of any size that I am likely to use in the future in acceptable times.
