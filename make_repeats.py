from __future__ import division
"""
    Make test files for  https://github.com/peterwilliams97/repeats
    

"""
import random, os

def make_random_string(size):
    return ''.join(chr(random.randint(ord('A'),ord('Z'))) for _ in range(size))

def uniquify_string(string):
    return '%06d%s' % (random.randint(0,10**6), string) 
    
def get_random_list(size):
    return [random.randint(ord('0'),ord('9')) for _ in range(size)]    
    
    
# REPEATED_STRING is the string the repeated string finder are supposed to find
REPEATED_STRING = 'the long long long repeated string that keeps on going and going and going'
#REPEATED_STRING = '0123456789'

NUM_LONGER_STRINGS_1 = 2
NUM_LONGER_STRINGS_2 = 3
BASE_STRING = [make_random_string(len(REPEATED_STRING)+5) for _ in range(NUM_LONGER_STRINGS_1)]
LONGER_STRINGS = BASE_STRING * NUM_LONGER_STRINGS_2
COUNFOUNDERS = 'ABCD'
CONFOUNDING_PREFIXES = [([ord(c)] * 11) for c in COUNFOUNDERS]

print LONGER_STRINGS

count = 0
def make_payload():
    global count
    # Some strings that will be repeated too many times 
    longer_strings = (uniquify_string(s) for s in LONGER_STRINGS)

    prefix = ''.join(chr(x) for x in CONFOUNDING_PREFIXES[count])

    count = (count + 1) % len(CONFOUNDING_PREFIXES)
    # The payload that is to be inserted once per repeat
    payload = prefix + REPEATED_STRING + ''.join(longer_strings)
    return payload

def make_random_lists(size, num_unique, gap):
    """Make <num_unique> random lists of sufficient size to fill a string of 
        <size> bytes
    """
    unique_size = len(REPEATED_STRING)//4 - gap 

    def make_list():
        return [random.randint(0,255) for _ in range(unique_size)]

    return [make_list() for _ in range(num_unique)]        
    
# Gap between unique strings    
JOIN_SIZE = 5    
    
def make_repeats(size, num_repeats, method, num_unique, random_lists):
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
        # num_unique unique strings ordered
        for i in range(size//4):
            r = i % num_unique
            data.append((r // 0x1000000) % 0xff)
            data.append((r // 0x10000) % 0xff)
            data.append((r // 0x100) % 0xff)
            data.append(r % 0xff)
            
    elif method == 4:   
        # num_unique unique strings unordered
        for _ in range(size//4):
            r = random.randint(1,num_unique)
            data.append((r // 0x1000000) % 0xff)
            data.append((r // 0x10000) % 0xff)
            data.append((r // 0x100) % 0xff)
            data.append(r % 0xff)        
    
    elif method == 5:   
        # num_unique truly unique strings 
        assert num_unique == len(random_lists)
        unique_size = len(random_lists[0])
        for _ in range(size//unique_size):
            data += random_lists[random.randint(0,num_unique-1)]
                    
    elif method == 6:   
        # Like 5 but no repeated string constructed from
        #  adjoining unique strings
        # num_unique truly unique strings 
        assert num_unique == len(random_lists)
        unique_size = len(random_lists[0])
        for _ in range(size//unique_size):
            data += random_lists[random.randint(0,num_unique-1)] + get_random_list(JOIN_SIZE)
                    
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

    for _ in range(num_repeats * 10):
        for cnfd in CONFOUNDING_PREFIXES:
            n = random.randint(0, size - len(cnfd) - 1)
            for i in range(len(cnfd)):
                data[n+i] = cnfd[i]

    #assert all(x <= 255 for x in data)                
    # Add the repeated strings payload once per repeat
    for i in range(num_repeats):
        # Payload is random value that differs on each call
        payload = make_payload()    
        offset = max(0, (repeat_size - len(payload))//2 ) 
        for j in range(len(payload)):
            #assert i*repeat_size+j < len(data), 'i=%d repeat_size=%d j=%d i*repeat_size+j=%d len(data)=%d' % (
            #        i, repeat_size, j, i*repeat_size+j, len(data))
            data[i*repeat_size + offset + j] = ord(payload[j])  

    # Put a heading at the start        
    for i,c in enumerate('THIS IS A FILE FOR TESTING FINDING REPEATED STRINGS\n'):
        data[i] = ord(c)        
    #assert all(x <= 255 for x in data)         
    # Convert list to string and return string            
    result = ''.join([chr(x) for x in data]) 
    assert result.count(REPEATED_STRING) == num_repeats
    return result

def make_repeats_file(directory, size, num_repeats, method, num_unique, random_lists):
    path = os.path.join(directory, 'repeats=%d.txt' % num_repeats)
    #print 'make_repeats_file(%d, %d) name="%s"' % (size, num_repeats, path)
    file(path, 'wb').write(make_repeats(size, num_repeats, method, num_unique, random_lists))
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
    parser.add_option('-u', '--uniquw', dest='unique', default='100000', help='Number of unique substrings')
    parser.add_option('-d', '--directory', dest='directory', default='.', help='Directory to create file in')

    (options, args) = parser.parse_args()

    size = int(float(options.size)*MBYTE)
    min_repeats = int(options.min)
    num_documents = int(options.num)
    method = int(options.method)
    num_unique = int(options.unique)
    directory = options.directory

    print '# size = %.3f Mbyte' % (size/MBYTE)
    print '# min_repeats = %d' % min_repeats 
    print '# num_documents = %d' % num_documents 
    print '# method = %d' % method
    print '# num_unique = %d' % num_unique    
    print '# directory = "%s"' % directory 
    print '# REPEATED_STRING = "%s"' % REPEATED_STRING
    print '# %s' % ('-' * 80)
    
    random_lists = None
    if method == 5:
        random_lists = make_random_lists(size, num_unique, 0)
    elif method == 6:
        random_lists = make_random_lists(size, num_unique, JOIN_SIZE)        
        
    
    entries = []
    for num_repeats in range(min_repeats, min_repeats + num_documents):
        
        path = make_repeats_file(directory, size, num_repeats, method, num_unique, random_lists)
        print '%s  # %2d repeats' % (path, num_repeats) 
    

main()

