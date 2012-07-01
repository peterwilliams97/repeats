#ifndef INVERTED_INDEX_H
#define INVERTED_INDEX_H

#include <string>
#include <vector>

/*
 * Use an inverted index to find the longest substring(s) that is repeated
 *  a specified number of times in a corpus of documents.
 *  
 * (The fact that the implementation uses an inverted index is not visiblen
 *  in this file.)
 *
 * Expected usage
 * ---------------
 *  // Create an inverted index from a list of files in filename that have 
 *  // their number of repeats encoded like "repeats=5.txt" 
 *  InvertedIndex *inverted_index = create_inverted_index(filenames);
 *
 *  // Optionally show the contents of the inverted index   
 *  show_inverted_index("initial", inverted_index);
 *
 *  // Compute the longest substrings that are repeated the specified 
 *  // number of times
 *  vector<string> repeats = get_all_repeats(inverted_index);
 * 
 *  // Free up all the resources in the InvertedIndex
 *  delete_inverted_index(inverted_index);
 */

const int MAX_SUBSTRING_LEN = 100;

// Opaque struct
struct InvertedIndex;

struct RepeatsResults {
    bool _converged; 
    std::vector<std::string> _longest;
    std::vector<std::string> _exact;
};

// Create an inverted index from a list of files in filename that have 
// their number of repeats encoded like "repeats=5.txt" 
InvertedIndex *create_inverted_index(const std::vector<std::string> &filenames);

// Free up all the resources in the InvertedIndex
void delete_inverted_index(InvertedIndex *inverted_index); 

// Show the contents of the inverted index 
void show_inverted_index(const std::string &title, const InvertedIndex *inverted_index);

// Return the longest substrings that are repeated the specified 
// number of times
RepeatsResults get_all_repeats(InvertedIndex *inverted_index, size_t max_substring_len = MAX_SUBSTRING_LEN);

#endif // #ifndef INVERTED_INDEX_H
