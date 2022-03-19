import functools


# Decorates a test case to run it as a set of subtests.
def sub_test(param_list):

    def decorator(f):
        @functools.wraps(f)
        def wrapped(self):
            for param in param_list:
                with self.subTest(**param):
                    f(self, **param)

        return wrapped

    return decorator

