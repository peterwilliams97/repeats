from __future__ import division
"""
    Make test files for  https://github.com/peterwilliams97/repeats
    

"""
import random, os

def make_unique_string(size):
    return ''.join(chr(random.randint(ord('A'),ord('Z'))) for _ in range(size))

def repeat_string(string, num_repeats):
    return ''.join(string + '%d' % i for i in range(num_repeats)) 
   
def make_repeated_unique(size, num_repeats):
    string = make_unique_string(size)
    return repeat_string(string, num_repeats)
   
# REPEATED_STRING is the string the repeated string finder are supposed to find
REPEATED_STRING = 'the long long long repeated string'
#REPEATED_STRING = '0123456789'

def make_payload(num_repeats):
    # Some strings that will be repeated too many times 
    longer_strings = [make_repeated_unique(len(REPEATED_STRING)+10, num_repeats) for _ in range(10)]

    # The payload that is to be inserted once per repeat
    payload = REPEATED_STRING + ''.join(longer_strings)
    return payload

def make_repeats(size, num_repeats, method):
    """Make a string of length <size> containing REPEATED_STRING 
        <num_repeats> times, and other data to test the repeated 
        string finding code.
        <method> sets the difficulty of string finding
            0: All bytes the same. Worst case for some string finding algos
            1: Random bytes of all bytes value. Worst case for other string 
                finding algos
    """
    repeat_size = size//num_repeats
    data = []
    
    if method == 0:
        # All bytes same
        for _ in range(size):
            data.append('x')
    
    elif method == 1:   
        # Random bytes
        for _ in range(size):
            data.append(random.randint(0, 255))
    
    elif method == 2:    
        # Maximize number of strings that are repeated num_repeats times
        # Also many repeats of 2 and 3 bytes strings    
        for r in range(repeat_size//4):
            for _ in range(num_repeats): 
                data.append((r // 0x1000000) % 0xff)
                data.append((r // 0x10000) % 0xff)
                data.append((r // 0x100) % 0xff)
                data.append(r % 0xff)
    
    elif method == 3:   
        # MAX_UNIQUE unique strings
        for r in range(size//MAX_UNIQUE*3):
            for _ in range(MAX_UNIQUE): 
                data.append((r // 0x10000) % 0xff)
                data.append((r // 0x100) % 0xff)
                data.append(r % 0xff)
        
    elif method == 3:
        # Random letters
        for _ in range(size):
            data.append(random.randint(ord('a'),ord('z')))      
            
    elif method == 4:
        # All variants of '[a-z][A-Z]\d.' 
        for _ in range(size//4):
            data.append(random.randint(ord('a'),ord('z')))
            data.append(random.randint(ord('A'),ord('Z')))
            data.append(random.randint(ord('0'),ord('9')))
            data.append(random.randint(0, 255))
     
    elif method == 5:    
        # All variants of '[a-z][A-Z]\d'
        for _ in range(size//3):
            data.append(random.randint(ord('a'),ord('z')))
            data.append(random.randint(ord('A'),ord('Z')))
            data.append(random.randint(ord('0'),ord('9')))
            
    elif method == 6:
        # Random upper-case letters
        for _ in range(size):
            data.append(random.randint(ord('A'),ord('Z')))
    
    payload = make_payload(num_repeats)    
            
    # Add the repeated strings payload once per repeat      
    for i in range(num_repeats):
        for j in range(len(payload)):
            assert i*repeat_size+j < len(data), 'i=%d repeat_size=%d j=%d i*repeat_size+j=%d len(data)=%d' % (
                    i, repeat_size, j, i*repeat_size+j, len(data))
            n = ord(payload[j])
            data[i*repeat_size+j] = n  

    # Convert list to string and return string            
    result = ''.join([chr(x) for x in data]) 
    assert result.count(REPEATED_STRING) == num_repeats
    return result

def make_repeats_file(directory, size, num_repeats, method):
    path = os.path.join(directory, 'repeats=%d.txt' % num_repeats)
    #print 'make_repeats_file(%d, %d) name="%s"' % (size, num_repeats, path)
    file(path, 'wb').write(make_repeats(size, num_repeats, method))
    return os.path.abspath(path)

KBYTE = 1024
MBYTE = KBYTE ** 2
GBYTE = KBYTE ** 3

def main():
    # The Nelson! 
    random.seed(111)
    
    import optparse, sys

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' [options]')
    parser.add_option('-r', '--min-repeats', dest='min', default='11',  help='min num of repeats')
    parser.add_option('-n', '--number', dest='num', default='5', help='number of documents')
    parser.add_option('-s', '--size', dest='size', default='1.0', help='size of each document in MBytes')
    parser.add_option('-m', '--method', dest='method', default='1', help='Method used to documents')
    parser.add_option('-d', '--directory', dest='directory', default='.', help='Directory to create file in')

    (options, args) = parser.parse_args()

    size = int(float(options.size)*MBYTE)
    min_repeats = int(options.min)
    num_documents = int(options.num)
    method = int(options.method)
    directory = options.directory

    print '# size = %.3f Mbyte' % (size/MBYTE)
    print '# method = %d' % method 
    print '# min_repeats = %d' % min_repeats 
    print '# num_documents = %d' % num_documents  
    print '# directory = "%s"' % directory  
    print '# %s' % ('-' * 80)
    
    entries = []
    for num_repeats in range(min_repeats, min_repeats + num_documents):
        
        path = make_repeats_file(directory, size, num_repeats, method)
        print '%s  # %2d repeats' % (path, num_repeats) 
    

main()

