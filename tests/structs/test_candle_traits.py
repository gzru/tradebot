import unittest
from structs.candle_traits import CandleTraits


class TestMethods(unittest.TestCase):
    def test_init_by_fields(self):
        traits = CandleTraits(["a", "b"])
        self.assertEqual(len(traits.fields), 2);
        self.assertEqual(traits.fields[0], "a");
        self.assertEqual(traits.fields[1], "b");
        self.assertEqual(len(traits.fields_index), 2);
        self.assertEqual(traits.fields_index["a"], 0);
        self.assertEqual(traits.fields_index["b"], 1);
        self.assertEqual(traits.fields_count, 2);

    def test_join(self):
        traits1 = CandleTraits(["a"])
        traits2 = CandleTraits(["c"])
        traits1.join(traits2)
        self.assertEqual(len(traits1.fields), 2);
        self.assertEqual(len(traits2.fields), 1);
        self.assertEqual(traits1.fields[0], "a");
        self.assertEqual(traits1.fields[1], "c");
        self.assertEqual(traits1.fields_index["a"], 0);
        self.assertEqual(traits1.fields_index["c"], 1);

    def test_rename_prefix(self):
        traits = CandleTraits(["a", "b"])
        traits.rename(prefix="x")
        self.assertEqual(len(traits.fields), 2);
        self.assertEqual(traits.fields[0], "xa");
        self.assertEqual(traits.fields[1], "xb");
        self.assertEqual(len(traits.fields_index), 2);
        self.assertEqual(traits.fields_index["xa"], 0);
        self.assertEqual(traits.fields_index["xb"], 1);
