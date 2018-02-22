# code from https://stackoverflow.com/questions/46170577/find-closest-line-to-each-point-on-big-dataset-possibly-using-shapely-and-rtree

from rtree import index

def get_rtree(lines):
    def generate_items():
        sindx = 0
        for lid, l in lines:
            for i in xrange(len(l)-1):
                a, b = l[i]
                c, d = l[i+1]
                segment = ((a,b), (c,d))
                box = (min(a, c), min(b,d), max(a, c), max(b,d))
                #box = left, bottom, right, top
                yield (sindx, box, (lid, segment))
                sindx += 1
    return index.Index(generate_items())