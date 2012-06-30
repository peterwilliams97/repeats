Finding Longest Repeated Substring in Documents
===============================================
This project explores some methods for finding the longest substring that is repeated a
specified number of times in each of the documents in a corpus. 

    Find longest substring that occurs >= num[d] times in documents doc[d] for d = 1..D 
    Each doc[d] is size[d] bytes long.
    
This problem comes up often in my work. I am given some documents, or strings if you prefer, 
that are known to encode some objects that are repeated some number of times. If I can
find some string of bytes that identifies each repetition of the object in the documents then
I can work on the objects, find the number objects in new documents and do other useful
things.

While there are many [highly efficient methods](http://bit.ly/OKukL3) for many types of 
string searching, I have not seen a method for this particular problem.   

The Basic Idea
--------------
The naive solution for finding the longest substring that occurs >= num[d] times in 
documents doc[d] for d = 1..D  will be hopelessly inefficient.

The naive solution is 

    for all documents doc[d], d = 1..D 
        for all substrings of length 1..size[d]/num[d] in doc[d]
            record the longest substring that occurs num[e] times in doc[e] for e = 1..D

This would take time proportional to 

    D * (size[d]/num[d])^2 * (size of corpus) 

For a corpus of 20 x 10 MB documents with 5 repeats per document and, say, one innermost 
operation (a single byte comparison in a string search) of 10^-9 sec this would be

    20 * (2*10^7)^2 * 2*10^8 * 10^-9 sec
    = 10^24 * 10^-9
    = 10^15 sec
    = 10^8 years        

We can do much better than this by observing that for each substring s of length m
that occurs >= num[d] times, all substrings of s must also occur at least num[d] times. 

Therefore we can build a list of strings recursively as follows
  
    valid_strings[m] = strings of length m that occur required number of times 
    Compute valid_strings[1] by checking number of occurrences of each byte in the docs 
    for m = 1 .. 
        construct valid_strings[m+1] as s + b for all strings s in valid_strings[n] and all 
            strings b in allowed_bytes
        remove from valid_strings[m+1] all strings that do not end in a string from valid_strings[m] 
        remove from valid_strings[m+1] all strings that do not occur required number of times 
        if len(valid_strings[m+1]) == 0 
            return valid_strings[m]          

Implementation
--------------
This is implemented in the python files in this directory. 
[fr.py](https://github.com/peterwilliams97/repeats/blob/master/fr.py) is a terse implementation 
of the above pseudo-code while
[find_repeated.py](https://github.com/peterwilliams97/repeats/blob/master/find_repeats.py) is
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
The above code typical runtimes with the documents I work on because I choose documents with the 
following properties

* small repeat size (size of document / number of repeats).
* great variety, which tend to make it hard for a substring to occur the allowed number of times by accident.

Typical behavior is

* len(valid_strings[1]) tends to be 50 - 100 (compared to a possible maxium of 256)
* len(valid_strings[m]) m > 1 tends not to increase much. It tends to stay < 1000 for m = 2..5 then decrease
* once len(valid_strings[m]) starts to decrease with increasing m, convergence follows fast

The python solution spends most of its time searching for substrings in documents (longer strings) so 
its running time is proportional to the number of bytes searched:

* typical bad case <= 5 * 1000 * (number of bytes in all documents) 
* typical good case <= 3 * 200 * (number of bytes in all documents) 

Running times like this turn out to be from under a minute to up a minute for well-chosen documents of 
a few MBytes each where corpora are from, say. 10 to 100 MByte total and string searching runs at, say, 
500 MB/sec

    typical bad case (100 MByte) : 5 * 1000 * 10^8 / (5 * 10^8) = 1000 seconds = 17 minutes
    typical good case (100 MByte) : * 200 * 10^8 / (5 * 10^8) = 120 seconds = 2 minutes  
    typical good case (10 MByte): 3 * 200 * 10^7 / (5 * 10^8) = 12 seconds  

Problems with the Basic Solution
--------------------------------
While [fr.py](https://github.com/peterwilliams97/repeats/blob/master/fr.py) performs well for 
well-chosen documents, its worst case performance is bad.

Worst case performance happens on large documents with little structure outside the repeated patterns. 
In this case  

    len(allowed_bytes) is ~ 256
    len(valid_strings[m]) to grow at 256^m to its limit of doc.size / m / num.repeats, 
    e.g 30^7/3/10 = 1,000,000 for a 30 MByte document with 10 repeats where it reaches 
        its maximum at n = 3 for a corpus of 10 x 30 MByte documents, 
        300 MBytes of data would   need to be seached 1,000,000 times which is 
        approx 3*10^14 bytes of searching which would take months on today's computers.

A Solution with Better Worst-Case Performance
---------------------------------------------
The big problem with the basic solution is that the number of substring searches grows too fast. 
This doesn't have to happen. 

After all, each of occurrences of the strings in valid_strings[m] in each document start with a 
string from valid_strings[m] by construction. Therefore the total number of occurrences of the 
of the strings in valid_strings[m+1] in each document must be less than or equal to the total 
number of occurrences of the of the strings in valid_strings[m].

The problem seems to be that our basic solution searches all of each document for each substring. 
We should be able to achieve search times proportional to document size if we stored the offsets of 
all occurrences of each substring in in each document, then searched only from there.  

A well-known way of storing documents in this way is an 
[inverted index](http://en.wikipedia.org/wiki/Inverted_index). 
There is a c++ implementation of an inverted index specialized for matching repeated substrings in
[inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp)

In inverted_index.cpp, 

    inverted_index._postings_map[s]_offsets_map[d]
    is a vector of offsets of substring s in document number d

Thus the inverted_index of strings of length 1, or bytes, stores the entire contents of the corpus 
of documents. Each offset is 4 bytes long so the inverted index takes 4 bytes to store every byte 
in the corpus.    

This 4-fold increase in storage size gives us a big advantage. As we run our algorithm of constructing
valid_strings[m+1] from valid_strings[m], the worst case amount of searching does not increase 
exponentially with n as before. In fact it does not increase much at all.

To go from valid_strings[m] to valid_strings[m+1], we 

    construct all valid substrings of length m+1
        inverted_index._postings_map[s1]_offsets_map[d] for all s1 in valid_strings[m+1]
    from all valid substrings of length m
        inverted_index._postings_map[s]_offsets_map[d] for all s in valid_strings[m]
    by appending all valid substrings of length 1 (bytes)
        inverted_index._postings_map[b]_offsets_map[d] for all b in valid_strings[1]
    
This is the same algorithm from _Basic Solution_ converted to inverted indexes. In this solution 
we also need to update the inverted index as we increase the substring length m. 

As the substring lengths increase, the number of allowed substrings increase, so 
* the number of vectors of offsets (number elements of inverted_index._postings_map[s]) increase, but 
* the length of each vector of offsets (each inverted_index._postings_map[s]_offsets_map[b]) decreases as well, so 
* the total number of offsets stored does not increase!

(There will be some implementation-dependent overhead required for tracking each vectors of offsets
that we will ignore for now).   

The growth in processing time with the length of the substrings being checked depends 
on long it takes to construct the vectors of offsets of all valid length m+1 substrings from 
the vectors of offsets of all valid length m substrings. 

We construct the vectors of offsets of the length m+1 substrings from the vectors of offsets 
of the length m substrings by 
"[merging](http://www.sorting-algorithms.com/merge-sort)" 
([German version](http://bit.ly/MZaHJ0)) the sorted 
inverted_index._postings_map[s]_offsets_map[d] with the sorted 
inverted_index._postings_map[1]_offsets_map[d]. These vectors are sorted because 
vectors of offsets of the length 1 substrings is constructed in sorted order as it is built 
by scanning documents and merging preserves order (see the above references or get_sb_offsets()
in [inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp)).   

Worst-Case Performance of the Merge Solution
--------------------------------------------
    Assume a document has length n with r repeats
    It will take O(n) time to read the document and construct the inverted index.
    The mth merges n/256 bytes with n/(256^m) strings x 256^m times 
        = O(n*(1/256+1/(256^m))*256^m)  
        = O(m*(256^(m-1)))  

This is still exponential in m, the length of the substrings being tested for repeats! 

Does this matter?
    
Clearly it matters for if m is large. Therefore we must estimate the largest m we will see in
real problems. 

This is straightforward to calculate for our worst case which is the maximum number of unique
substrings m: 256^m == size of repeat == n/r or m == log256(n/r) 

    10 MByte document with 10 repeats ==> m=3
    100 MByte document with 100 repeats ==> m=3.2

The documents that I test are usually less than 10 MByte so n*(256^(m-1)) is n*(256^2) which 
is not too bad. Therefore simple merging should work reasonably well. This is marked as 
INNER_LOOP==1 in 
[inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp)  

However we can do better.

Recall that we are merging n/256 bytes with n/(256^m) strings x 256^m times. The stepping through
the n/(256^m) strings x 256^m times takes constant time with respect to m. The problem is the
stepping through the constant number of bytes x 256^m. 

The byte offsets are sorted so we don't need to step linearly. We can step in a 
the bytes offsets in INNER_LOOP==1. We can divide the bytes offsets into a number equal regions of
of the length of the number of strings then linearly step through the string offsets and after each 
one, binary search region. The length of each byte offset region is 
(1/256) / (1/(256^m)) = 256^(m-1), so the binary search time is O(log(256^(m-1))) = O(m)

The total search time is  

    O(n*(S+Bm)) where S and B are some constants. 
        S for stepping through the substring offsets and 
        B for stepping through the byte offsets.
    = O(nm)

This growth stops when the maximum number of valid unique substrings is reached at 
m = log256(n/r), so there is linear growth in search time with the lengths of substring up until 
the peak is reached which will be at m = 4 for documents with 4 GByte per repeat. 

4 GByte per repeat is bigger than I ever expect to see so this should be more than adequate
    
TODO
----
Binary search on strings, linear search on bytes

Raw binary search

Multi-thread
Try http://dlib.net/

Test for substrings that are repeated more times that required

Construct worst case of the maximum number of unique _valid_ substrings