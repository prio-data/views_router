
import unittest
from . import paths

class TestPaths(unittest.TestCase):
    def test_remotes(self):
        try:
            rmt = paths.Remotes(trf="http://foo",base="http://bar")
        except TypeError:
            self.fail()

        fails = lambda: paths.Remotes(trf="http://foo")
        self.assertRaises(TypeError,fails)

    def test_path_validation(self):
        cases = [
                ("a/base/b/c",False),
                ("a/trf/b/c/base/d/e",False),
                ("a/base/b/c/trf/d/e",True),
                ("a/base/b/c/base/d/e",True),
                ("a/base/c",True),
            ]
        for case,raises in cases:
            fn = lambda: paths.Path.parse(case)

            try:
                if raises:
                    self.assertRaises(ValueError,fn)
                else:
                    try:
                        fn()
                    except ValueError:
                        self.fail()

            except AssertionError:
                self.fail(f"{case} was{' not' if not raises else ''} validated, but is "
                        f"{'in' if raises else ''}valid"
                        )
    def test_path_url(self):
        cases = [
                ("root/base/a/b","http://base/root/a/b"),
                ("root/trf/a/b/base/c/d","http://trf/root/a/b/base/c/d"),
            ]

        remotes = paths.Remotes(base="http://base",trf="http://trf")

        for case,expected in cases:
            url = (paths.Path.parse(case)
                .url(remotes)
                )
            self.assertEqual(url,expected)
