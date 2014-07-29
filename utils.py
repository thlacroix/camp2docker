def mustach_dict(d):
    res = {}

    def rec(rest, end_value, current = None):
        try:
            elem = rest.pop(0)
        except:
            return end_value

        if current is None:
            return {elem: rec(rest, end_value, None)}
        elif type(current) is dict and current.has_key(elem):
            return rec(rest, end_value, current[elem])
        else:
            current[elem] = rec(rest, end_value, None)

    for k, v in d.iteritems():
        exploded_key = k.split('.')
        rec(exploded_key, v, res)

    return res

if __name__ == "__main__":
    a = {'a.a':1, 'a.b': 2, 'a.c':3, 'd.e':4, 'd.f.q': 5, 'd.f.r':6}
    print mustach_dict(a)
