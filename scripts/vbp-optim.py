from vsvbp import container, solver
import argparse, sys, os, re

def parse(inputfile):
    """ Parse a file using format from
    Brandao et al. [Bin Packing and Related Problems: General Arc-flow Formulation with Graph Compression (2013)]
    Format:
        d (number of dimensions)
        C_1 ... C_d             capacities of the bins in each dimension
        n                       number of different items
        w^1_1 ... w^d_1 d_1     requirements of item 1 + {demand = number of such items}
        ...
        w^1_n ... w^p_n d_n

    Return: a list of items and a typical bin
    """

    inp = inputfile
    #inp = open(filename, 'r')

    dim = int(inp.readline())
    #if dim > 50: return False, False
    cap = map(int, inp.readline().split())
    assert dim == len(cap)

    nitems = int(inp.readline())
    items = []
    i = 0
    for line in inp:
        req = map(int, line.split())
        dem = req.pop()
        assert len(req) == dim
        items.extend([container.Item(req) for j in xrange(dem)])
        i += 1
    assert i == nitems

    inp.close()

    return items, container.Bin(cap)


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


def get_subdirectories(directory):
    dirs = [os.path.join(directory,name) for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]
    return natural_sort(dirs)


def get_files(directory):
    files = [os.path.join(directory,name) for name in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, name))]
    files.sort()
    return natural_sort(files)


def optim_dir(directory, level=0):
    files = get_files(directory)
    for f in files:
        optimize(f, level)


def optim_rec(directory, level=0):
    subdir = get_subdirectories(directory)

    print "   "*level+ "|"+"- "+directory.split('/').pop()

    if not subdir:
        return optim_dir(directory, level+1)
    for d in subdir:
        optim_rec(d, level+1)


def optimize(filename, level=0):
    fl = open(filename)
    items, tbin = parse(fl)
    if not items:
        fl.close()
        return

    opt = len(solver.optimize(items, tbin, optimize.dp, optimize.seed).bins)

    template = "{0:50}{1:10}"
    if level == 0:
        st = filename.split('/').pop()
        print template.format(st, str(opt))
    else:
        st = "   "*level+"| "+filename.split('/').pop()
        print template.format(st, str(opt))

    fl.close()
    sys.stdout.flush()

def run():
    parser = argparse.ArgumentParser(description="Run VSVBP heuristics on given instances")
    parser.add_argument('-f', type=argparse.FileType('r'),
            help="The path to a file containing the bin packing problem to optimize")
    parser.add_argument('-d', help="A directory containing (only) files modeling\
            bin packing problems to optimize. Optimize all files in the directory.")
    parser.add_argument('-r', action='store_true', help="Recursive. If a directory is provided,\
            optimize all files in all final subdirectories.")
    parser.add_argument('-u', action='store_true', help="If activated, use dot product heuristics")
    parser.add_argument('-s', type=int, help="Set seed to specified value")

    args = parser.parse_args()
    if not (args.f or args.d):
        parser.error('No action requested, add -f or -d')
    if args.f and args.d:
        parser.error('Too many actions requested, add only -f or -d')
    if args.r and not args.d:
        sys.stderr.write("Warning recursive argument was specified but")
        sys.stderr.write(" no directory was provided. Argument ignored.\n")

    if args.d and not os.path.isdir(args.d):
        parser.error('Invalid directory')

    optimize.dp = args.u
    optimize.seed = args.s

    if args.f:
        items, tbin = parse(args.f)
        opt = len(solver.optimize(items, tbin, args.u, args.s).bins)
        template = "{0:50}{1:10}"
        st = args.f.name.split('/').pop()
        print template.format(st, str(opt))
    elif not args.r:
        optim_dir(args.d)
    else:
        optim_rec(args.d)

if __name__ == "__main__":
    run()
