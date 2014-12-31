#include <fstream>
#include <iostream>
#include <limits>

#include "utils.h"
#include "timer.h"
#include "inverted_index.h"
#include "trie.h"
#include "sa.h"

using namespace std;

struct CodeComment {
    string _code;
    string _comment;
};

CodeComment
get_code_comment(const string &line) {
    stringstream ss(line);
    string item;
    CodeComment code_comment;
    if (getline(ss, item, '#')) {
        code_comment._code = trim(item);
    }
    if (getline(ss, item)) {
        code_comment._comment = trim(item);
    }
    return code_comment;
}

static vector<string>
get_filenames(const string &filelist) {
    ifstream f(filelist);
    if (!f.is_open()) {
        cerr << "Unable to open '%s'" << filelist << endl;
        return vector<string>();
    }

    vector<string> filenames;
    while (f.good()) {
        string line;
        getline(f, line);
        CodeComment code_comment = get_code_comment(line);
        if (code_comment._code.size()) {
            filenames.push_back(code_comment._code);
        }
        if (code_comment._comment.size()) {
            cout << "# " << code_comment._comment << endl;
        }
    }
    f.close();

    return filenames;
}

static
double
test_inverted_index(const vector<string> &filenames) {

    reset_elapsed_time();

    InvertedIndex *inverted_index = create_inverted_index(filenames);
    if (inverted_index == NULL) {
        return -1.0;
    }
    show_inverted_index("initial", inverted_index);

    RepeatsResults repeats_results = get_all_repeats(inverted_index);

    bool converged = repeats_results._converged;
    vector<string> exacts = repeats_results._exact;
    vector<string> repeats = repeats_results._longest;

    cout << "--------------------------------------------------------------------------" << endl;
    cout << "converged = " << converged << endl;
    cout << "--------------------------------------------------------------------------" << endl;
    if (repeats.size() > 0) {
        cout << "Found " << repeats.size() << " repeated strings";
        if (repeats.size() > 0) {
            cout << " of length " << repeats.front().size();
        }
        cout << endl;
       // print_vector("Repeated strings", repeats);
    }

    cout << "--------------------------------------------------------------------------" << endl;
    if (exacts.size() > 0) {
        cout << "Found " << exacts.size() << " exactly repeated strings";
        if (exacts.size() > 0) {
            cout << " of length " << exacts.front().size();
        }
        cout << endl;
        print_vector("Exactly repeated strings", exacts);

    }

    delete_inverted_index(inverted_index);

    double duration = get_elapsed_time();
    cout << "duration = " << duration << endl;
    return duration;
}

static
double
test_trie(const vector<string> &filenames) {

    reset_elapsed_time();

    int max_len = 50;
    Trie *trie = create_trie(filenames, max_len);

    RepeatsResults repeats_results = get_all_repeats_trie(trie);

    bool converged = repeats_results._converged;
    vector<string> exacts = repeats_results._exact;
    vector<string> repeats = repeats_results._longest;

    cout << "--------------------------------------------------------------------------" << endl;
    cout << "converged = " << converged << endl;
    cout << "--------------------------------------------------------------------------" << endl;
    if (repeats.size() > 0) {
        cout << "Found " << repeats.size() << " repeated strings"
             << " of length " << repeats.front().size()
            << endl;
       // print_vector("Repeated strings", repeats);
    }

     if (exacts.size() > 0) {
        cout << "Found " << exacts.size() << " exact strings"
             << " of length " << exacts.front().size()
            << endl;
       // print_vector("Repeated strings", repeats);
    }

    delete_trie(trie);

    double duration = get_elapsed_time();
    cout << "duration = " << duration << endl;
    return duration;
}

#if 0
static
double
test_sa(const vector<string> &filenames) {

    reset_elapsed_time();

    int max_len = 50;
    SA *sa = create_sa(filenames, max_len);

    RepeatsResults repeats_results = get_all_repeats_sa(sa);

    bool converged = repeats_results._converged;
    vector<string> exacts = repeats_results._exact;
    vector<string> repeats = repeats_results._longest;

    cout << "--------------------------------------------------------------------------" << endl;
    cout << "converged = " << converged << endl;
    cout << "--------------------------------------------------------------------------" << endl;
    if (repeats.size() > 0) {
        cout << "Found " << repeats.size() << " repeated strings"
             << " of length " << repeats.front().size()
            << endl;
       // print_vector("Repeated strings", repeats);
    }

     if (exacts.size() > 0) {
        cout << "Found " << exacts.size() << " exact strings"
             << " of length " << exacts.front().size()
            << endl;
       // print_vector("Repeated strings", repeats);
    }

    delete_sa(sa);

    double duration = get_elapsed_time();
    cout << "duration = " << duration << endl;
    return duration;
}
#endif

void
show_stats(const vector<double> &d) {

    double min_d = numeric_limits<double>::max();
    double max_d = numeric_limits<double>::min();
    double total = 0.0;
    for (vector<double>::const_iterator it = d.begin(); it != d.end(); it++) {
        min_d = min(min_d, *it);
        max_d = max(max_d, *it);
        total += *it;
    }
    unsigned int n = d.size();
    double ave = total / (double)n;
    double med = d[n/2];
    cout << "min="<< min_d << ", max="<< max_d << ", ave=" << ave << ", med=" << med << endl;
}

void
multi_test(const string &filelist, int n) {
    vector<string> filenames = get_filenames(filelist);
    vector<double> durations;
    for (int i = 0; i < n; i++) {
        cout << "========================== test " << i << " of " << n << " ==============================" << endl;
        durations.push_back(test_inverted_index(filenames));
        show_stats(durations);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " filelist" << endl;
        return 1;
    }

    string filelist(argv[1]);
    vector<string> filenames = get_filenames(filelist);
    if (filenames.size() == 0) {
        cerr << "No filenames in " << filelist << endl;
        return 1;
    }

    double duration = test_inverted_index(filenames);
    //test_sa(filenames);

    if (duration < 0.0) {
        cerr << "FAILED" << endl;
        return 1;
    }

    cout << "SUCCEEDED" << endl;
    return 0;
}
