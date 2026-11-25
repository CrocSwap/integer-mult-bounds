"""Regression checks for inherited host limits; never modify real limits."""
import resource
import unittest
from unittest.mock import patch

from verify import inherited_stack_limits


class InheritedStackTests(unittest.TestCase):
    def test_host_defaults_are_preserved(self):
        for limits in [(8388608, -1), (16777216, -1), (-1, -1),
                       (8388608, 16777216)]:
            with self.subTest(limits=limits), \
                 patch.object(resource, 'getrlimit', return_value=limits), \
                 patch.object(resource, 'setrlimit') as setter:
                self.assertEqual(inherited_stack_limits(), limits)
                self.assertEqual(inherited_stack_limits(limits), limits)
                setter.assert_not_called()

    def test_changed_limit_is_rejected(self):
        with patch.object(resource, 'getrlimit', return_value=(16777216, -1)):
            with self.assertRaisesRegex(RuntimeError, 'changed during verification'):
                inherited_stack_limits((8388608, -1))

    def test_invalid_limits_are_rejected(self):
        for limits in [(0, -1), (-2, -1), (-1, 8388608),
                       (16777216, 8388608)]:
            with self.subTest(limits=limits), \
                 patch.object(resource, 'getrlimit', return_value=limits):
                with self.assertRaisesRegex(RuntimeError, 'Invalid inherited'):
                    inherited_stack_limits()


if __name__ == '__main__':
    unittest.main()
