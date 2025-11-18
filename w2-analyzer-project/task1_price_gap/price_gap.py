from typing import List, Tuple, Optional

def find_price_gap_pair(nums: List[int], k: int) -> Optional[Tuple[int, int]]:
    """
    Return indices (i, j) with i < j and abs(nums[i] - nums[j]) == k.
    If multiple exist, return the lexicographically smallest pair.
    If none, return None.
    """
    if not nums or len(nums) < 2:
        return None
    
    # Dictionary to store the first occurrence of each value
    value_to_index = {}
    
    # Initialize with a large j value to find smallest pairs
    best_pair = None
    
    for j, num in enumerate(nums):
        # Check for two possible differences: num - target = k or target - num = k
        # Which means target = num - k or target = num + k
        
        # Check for num - k
        target1 = num - k
        if target1 in value_to_index:
            i = value_to_index[target1]
            candidate = (i, j)
            if best_pair is None or candidate < best_pair:
                best_pair = candidate
        
        # Check for num + k  
        target2 = num + k
        if target2 in value_to_index:
            i = value_to_index[target2]
            candidate = (i, j)
            if best_pair is None or candidate < best_pair:
                best_pair = candidate
        
        # Store the first occurrence of this number
        if num not in value_to_index:
            value_to_index[num] = j
    
    return best_pair