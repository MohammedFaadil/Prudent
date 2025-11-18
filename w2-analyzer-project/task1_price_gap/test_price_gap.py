import unittest
from price_gap import find_price_gap_pair

class TestPriceGapPair(unittest.TestCase):
    
    def test_basic_example(self):
        nums = [4, 1, 6, 3, 8]
        k = 2
        result = find_price_gap_pair(nums, k)
        self.assertEqual(result, (0, 2))
    
    def test_duplicates_k_zero(self):
        nums = [5, 5, 5]
        k = 0
        result = find_price_gap_pair(nums, k)
        self.assertEqual(result, (0, 1))
    
    def test_negatives_and_positives(self):
        nums = [-3, 7, 1, -1, 4]
        k = 2
        result = find_price_gap_pair(nums, k)
        self.assertEqual(result, (0, 3))
    
    def test_no_solution(self):
        nums = [10, 20, 30]
        k = 25
        result = find_price_gap_pair(nums, k)
        self.assertIsNone(result)
    
    def test_multiple_valid_pairs(self):
        nums = [1, 3, 1, 3, 1]
        k = 2
        result = find_price_gap_pair(nums, k)
        self.assertEqual(result, (0, 1))
    
    def test_single_element(self):
        nums = [5]
        k = 0
        result = find_price_gap_pair(nums, k)
        self.assertIsNone(result)
    
    def test_empty_list(self):
        nums = []
        k = 5
        result = find_price_gap_pair(nums, k)
        self.assertIsNone(result)
    
    def test_lexicographic_order(self):
        nums = [1, 4, 2, 5, 3]
        k = 1
        result = find_price_gap_pair(nums, k)
        # Possible pairs: (0,2), (2,4) - (0,2) is lexicographically smallest
        self.assertEqual(result, (0, 2))

if __name__ == '__main__':
    unittest.main()