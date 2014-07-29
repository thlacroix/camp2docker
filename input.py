from yaml import load
from plan import Plan

class Planfile(object):
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'r') as f:
            self._planfile = load(f)
    @property
    def config(self):
        return self._planfile

    def __repr__(self):
        return str(self._planfile)

    def create_plan(self):
        if not self._planfile.has_key("name"):
            self._planfile["name"] = filename
        return Plan(**(self._planfile))

if __name__ == "__main__":
    import sys
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    try:
        filename = sys.argv[1]
    except:
        filename = "camp/app.yaml"
    config = Planfile(filename)
    print "Config\n"+pp.pformat(planfile)
    x = config.parse()
    print "Plan:"+pp.pformat(x)
