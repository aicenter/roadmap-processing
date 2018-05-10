from roadmaptools.util import filter_dict


def test_filter_dict():

    d = {'alpha' : 12, 'beta' : {1, 'two'}, 'gamma' : 'dog'}

    assert filter_dict(d, {'beta', 'gamma'}) == {'beta': {1, 'two'}, 'gamma': 'dog'}

    assert filter_dict(d, {'beta', 'zeta'}) == {'beta': {1, 'two'}}



if __name__ == '__main__':
    pass