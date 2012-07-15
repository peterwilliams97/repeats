Generalized Suffix Tree Solution 
================================
.. to 

    Find longest substring that occurs >= num[d] times in documents doc[d] for d = 1..D 
    Each doc[d] is size[d] bytes long.
    
This recognizable as a variant of the 
[longest repeated substring problem](http://en.wikipedia.org/wiki/Longest_repeated_substring_problem)

The algorithm is rougly

    Build the generalized suffix tree of the D documents.
    Do depth first search
    On way back up, add a count of descendants for each document to each in internal node
    Stop and move on to siblings if
        a) if node has > num[d] descendents for any d = 1..D, or
        b) node has == num[d] descendents for all d = 1..D
        In case b) add substring from root to node to list of substrings
        Remove all but longest substring(s) from list    
    