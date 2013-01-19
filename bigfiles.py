#!/usr/bin/env python


def traceit(fn):
    import sys
    def new_fn(*a,**kw):
        ret = fn(*a,**kw)
        sys.stderr.write("Fn: %s; a=%s; kw=%s\nRet: %s\n"
                         % (fn,a,kw,ret))
        return ret
    return new_fn


import sys
import os
import os.path
import stat
import fnmatch

from optparse import OptionParser
from operator import itemgetter, attrgetter
from stat     import ST_MODE,S_ISDIR,S_ISREG,S_ISLNK,ST_SIZE
from heapq    import heappush, heappop





def humanize(bytes):
  """Turns a byte count into a human readable string."""
  if bytes > 1099511627776:
    value = bytes / 1099511627776.0
    units = "TB"
  elif bytes > 1073741824:
    value = bytes / 1073741824.0
    units = "GB"
  elif bytes > 1048576:
    value = bytes / 1048576.0
    units = "MB"
  elif bytes > 1024:
    value = bytes / 1024.0
    units = "kB"
  else:
    value = float(bytes)
    units = "bytes"
  return "%.2f %s" % (value, units)


usage = "usage: %prog [options] arg"
parser = OptionParser(usage)

parser.add_option("-n", "--num", "--number",
                dest="num",
                type="int",
                default=10,
                action="store",
                help="Display <count> results"
                )

parser.add_option("-B", "--bytes",
                dest="human",
                action="store_false",
                default=True,
                help="display file sizes in bytes, opposed to a human readable format (kB/MB/GB)"),

parser.add_option("-d", "--directories",
                dest="check_dirs",
                action="store_true",
                default=False,
                help="report the largest directories, determined by summing the filesize of each directories' immediate children",)

parser.add_option("--filter", "-f",
                dest="filter_pattern",
                type="string",
                action="store",
                default="*")

parser.add_option("--maxdepth", "--depth",
                dest="maxdepth",
                type="int",
                action="store",
                default="0",
                help="Do not recurse more than <depth> levels deep")

parser.add_option("--EXPERIMENTAL", "--EXP", "--test", "--dev",
                dest="EXPERIMENTAL",
#                type="",
                action="store_true",
                default=False,
                help="Experimenta"),

(options, args) = parser.parse_args()

#print options,args
num=options.num
human=options.human
filter_pattern=options.filter_pattern
check_dirs=options.check_dirs
maxdepth=options.maxdepth
EXPERIMENTAL=options.EXPERIMENTAL

if len(args) == 0:
    args.append(".")




def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = len([x for x in some_dir if x == os.path.sep])
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = len([x for x in root if x == os.path.sep])
        if num_sep + level <= num_sep_this:
            del dirs[:]


def walk_level(some_dir,maxdepth=0,group_directories=0):
    level=maxdepth
    if maxdepth == 0:
        level=999

    for root,dirs,files in walklevel(some_dir, level):
        rootsize=os.stat(root)[ST_SIZE]
        for f in files:
            try:
                fn = os.path.join(root, f)
                ss=os.stat(fn)
                rootsize+=ss[ST_SIZE]
                if not group_directories:
                    yield (ss[ST_SIZE], fn)
            except:
#                print "fail..%s" % fn
                pass
        if group_directories:
            yield (rootsize,root)


def search(path):
    heap=[]
    ordered=[]

    if EXPERIMENTAL:
        from collections import defaultdict
        heaps=defaultdict(list)
        heapsizes=defaultdict(int)
        ordered=defaultdict(list)
        for item in walk_level(os.path.normpath(path),maxdepth,group_directories=check_dirs):
            [base,ext]=os.path.splitext(item[1])
            heapsizes[ext]+=item[0]
            heappush(heaps[ext],item)

        sortedheaps=sorted(heapsizes.items(),reverse=True,key=itemgetter(1))
        for hh in sortedheaps:
            print hh[0],"\t",humanize(hh[1])
        for k,myheap in heaps.items():
            ordered=[]
            print "%s\t%d" % (k,heapsizes[k])
            while myheap:
                ordered.append(heappop(myheap))
            for element in ordered[:-num-1:-1]:
                if human:
                    print humanize(element[0]),element[1]
                else:
                    print element[0],element[1]
            print ""



    for item in walk_level(os.path.normpath(path),maxdepth,group_directories=check_dirs):
        heappush(heap,item)

    while heap:
        ordered.append(heappop(heap))
    for element in ordered[:-num-1:-1]:
        if human:
            print "%s\t%s" % (humanize(element[0]), element[1])
        else:
            print "%s\t%s" % (element[0], element[1])

#search=traceit(search)

if __name__ == '__main__':
    for path in args:
        search(path)
    #    traceit(search(path))
        print "\n"

