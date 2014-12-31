#include <fstream>
#include <iostream>
#include <sys/stat.h>
#include "mytypes.h"
#include "utils.h"

using namespace std;

int
string_to_int(const string s) {
    int x;
    return from_string(s, x);
}

int
get_file_size(const string filename) {
    struct stat filestatus;
    if (stat(filename.c_str(), &filestatus) < 0) {
        cerr << "could not open '" << filename << "'" << endl;
        return -1;
    }

    return (int)filestatus.st_size;
}

byte *
read_file(const string filename) {
    size_t size = get_file_size(filename);
    byte *data = new byte[size];
    if (data == NULL) {
        cerr << "could not allocate " << size << " bytes" << endl;
        return 0;
    }

    ifstream f;
    f.open(filename, ios::in | ios::binary);
    if (!f.is_open()) {
        cerr << "could not open " << filename << endl;
        delete[] data;
        return NULL;
    }

    f.read((char *)data, size);

    if (f.gcount() < size) {
        cerr << "could not read " << filename << endl;
        delete[] data;
        data = NULL;
    }

    f.close();
    return data;
}
