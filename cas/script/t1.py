

class V1:
    def __call__(self, *args, **kwargs):
        print args, kwargs


v = V1()

v(111)