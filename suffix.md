Generalized Suffix Tree Solution 
================================
.. to 

    Find longest substring that occurs num[d] times in documents doc[d] for d = 1..D 
    Each doc[d] is size[d] bytes long.
    
This recognizable as a variant of the 
[longest repeated substring problem](http://en.wikipedia.org/wiki/Longest_repeated_substring_problem)

The algorithm is roughly:

    Build the generalized suffix tree for the D documents.
    Do a depth first search of the generalized suffix tree
    On way back up, add a count of descendants for each document to each internal node
    Stop and move on to a node's siblings if
        a) node has > num[d] descendents for any d = 1..D, or
        b) node has == num[d] descendents for all d = 1..D
        In case b) add substring from root to node to list of substrings
        Remove all but longest substring(s) from list   
        
This solution is O(size of corpus) in time and space. I am avoiding it for now as 

* all the suffix tree implementations I know take up too much space. 
* I don't need the nice asymptotic speed as the [ solution](https://github.com/peterwilliams97/repeats) 
works well for corpora I work on. 
      