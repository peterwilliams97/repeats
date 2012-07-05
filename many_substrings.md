The Many Substrings Problem
===========================
After all the optimizations in our [main solution](https://github.com/peterwilliams97/repeats)  
it is still possible for an adversary to construct documents that our solution does 
not handle well.

Our adversary (me! Hi there) can constrcut documents that require our solution to store 
many unique substrings. 
[make_repeats.py](https://github.com/peterwilliams97/repeats/blob/master/make_repeats.py)
methods 5 and 6 show how to do this.    

The implementation-dependent overhead required for tracking a string in 
[inverted_index.cpp](https://github.com/peterwilliams97/repeats/blob/master/repeats/inverted_index.cpp))
is sizeof(Postings) = 44 bytes _check this!_ + number of bytes taken by a 
[string](http://social.msdn.microsoft.com/forums/en-US/vclanguage/thread/9a59970d-c7bf-4ed5-8267-e482c4e461a7/) 
= 32 + memory. In this 
implementation the single document corpus gives
the worst storage because the offsets of all documents are stored for each substring in a
Postings.

With, say, 20M unique substrings for 1 x 100MB document, 

    offsets storage = 4 x 100M = 400M
    substrings storage = (76+ mem(m)) x 20M = 1600M 
      where mem(m) is the amount of memory allocated for an m character string
        
    
It should be possible to bound the substrings storage

    for each document d of size[d] for substrings of length m
    total number of offsets n <= size[d] - m + 1
    total number of unique substrings k <= size[d] - m + 1
    space for offsets = 4 * n
    space for k * length m substrings = k * m (array of bytes, kth substring at offset m*k)
    space for associating substring with offsets =
        k * 8 (offset + length into offsets array = 4 + 4 bytes)
        
    We would store substrings for all docs in one place
    Reduce this to intersection of valid substrings in all docs
    For each doc, store offsets of substrings
        
        
    
    