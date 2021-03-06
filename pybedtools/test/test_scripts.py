import pybedtools
from pybedtools.scripts import annotate, venn_mpl, venn_gchart
from nose.tools import assert_raises
import os
import sys


def test_annotate_main():
    # exits after printing help when sys.argv is not as it should be.
    orig_stderr = sys.stderr
    sys.stderr = open('tmp','w')
    assert_raises(SystemExit, annotate.main)
    sys.stderr = orig_stderr
    os.unlink('tmp')

def test_annotate_closest():
    a = pybedtools.example_bedtool('m1.bed')
    b = pybedtools.example_bedtool('mm9.bed12')
    c = annotate.add_closest(a, b)
    assert len(a) == len(c), (len(a), len(c), str(c))
    assert a.field_count() == c.field_count() - 2
    # in this test-case, the final column should be exon;intron
    # since m1 completely contains both an exon and an intron.
    f = iter(c).next()
    # waiting for fix to bedtools:
    #assert f.fields[-1] == "exon;intron", f.fields[-1]


def test_annotate_xstream():
    a = pybedtools.example_bedtool('m1.bed')
    b = pybedtools.example_bedtool('mm9.bed12')
    c = annotate.add_xstream(a, b, dist=1000, updown="up")
    assert a.field_count() == c.field_count() - 1
    assert len(a) == len(c)
    d = annotate.add_xstream(c, b, dist=1000, updown="down")
    assert a.field_count() == d.field_count() - 2


def test_venn_mpl():
    """
    compares output image to expected
    """
    try:
        import matplotlib
    except ImportError:
        import sys
        sys.stderr.write('Need matplotlib installed to test venn_mpl')
        return

    here = os.path.dirname(__file__)
    expected_fn = os.path.join(here, 'mpl-expected.png')

    pybedtools.bedtool.random.seed(1)
    a = pybedtools.example_bedtool('rmsk.hg18.chr21.small.bed')
    b = a.random_subset(100).shuffle(genome='hg19', seed=1)
    b = b.cat(a.random_subset(100, seed=1))
    c = a.random_subset(200).shuffle(genome='hg19', seed=2)
    c = c.cat(b.random_subset(100, seed=1))

    outfn = 'mplout.png'
    venn_mpl.venn_mpl(a=a.fn, b=b.fn, c=c.fn, colors=['r','b','g'], outfn=outfn, labels=['a','b','c'])

    # On a different machine, the created image is not visibly different but is
    # numerically different.  Not sure what a reasonable tolerance is, but this
    # seems to work for now....
    o = matplotlib.image.imread(outfn)
    e = matplotlib.image.imread(expected_fn)

    TOLERANCE = 25
    assert abs((o - e).sum()) < TOLERANCE

    os.unlink(outfn)



def test_venn_gchart():
    here = os.path.dirname(__file__)
    expected = open(os.path.join(here, 'gchart-expected.png')).read()


    pybedtools.bedtool.random.seed(1)
    a = pybedtools.example_bedtool('rmsk.hg18.chr21.small.bed')
    b = a.random_subset(100).shuffle(genome='hg19', seed=1)
    b = b.cat(a.random_subset(100, seed=1))
    c = a.random_subset(200).shuffle(genome='hg19', seed=2)
    c = c.cat(b.random_subset(100, seed=1))
    colors='00FF00,FF0000,0000FF'
    outfn = 'out.png'
    labels = 'a,b,c'

    expected_data = {'chco': '00FF00,FF0000,0000FF',
                     'chd': 't:1.0,0.2,0.3,0.104,0.048,0.1,0.048',
                     'chs': '300x300',
                     'cht': 'v',
                     'chdl': 'a|b|c'}

    data = venn_gchart.venn_gchart(a=a.fn,
                            b=b.fn,
                            c=c.fn,
                            colors=colors.split(','),
                            labels=labels.split(','),
                            size='300x300')

    print data
    for key in expected_data.keys():
        e = expected_data[key]
        o = data[key]
        print 'key:', key
        print 'expected:', e
        print 'observed:', o
        assert e == o

    venn_gchart.gchart(data, outfn)

    assert open(outfn).read() == expected
    os.unlink(outfn)

def test_venn_mpl_main():
    orig_stderr = sys.stderr
    sys.stderr = open('tmp','w')
    assert_raises(SystemExit, venn_mpl.main)
    sys.stderr = orig_stderr
    os.unlink('tmp')

def test_venn_gchart_main():
    orig_stderr = sys.stderr
    sys.stderr = open('tmp','w')
    assert_raises(SystemExit, venn_gchart.main)
    sys.stderr = orig_stderr
    os.unlink('tmp')

def teardown():
    pybedtools.cleanup()
