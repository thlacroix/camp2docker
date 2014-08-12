def mustach_dict(d):
    res = {}

    def rec(rest, end_value, current = None):
        try:
            elem = rest.pop(0)
        except:
            if current is None:
                return end_value
            else:
                raise Exception("Rewriting a key")

        if current is None:
            return {elem: rec(rest, end_value, None)}
        elif type(current) is not dict:
            raise Exception("Rewriting of the key {elem}".format(elem=elem))
        elif current.has_key(elem):
            return rec(rest, end_value, current[elem])
        else:
            current[elem] = rec(rest, end_value, None)

    for k, v in d.iteritems():
        exploded_key = k.split('.')
        rec(exploded_key, v, res)

    return res
