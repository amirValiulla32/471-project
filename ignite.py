def binary_search(nums, target):

    left = 0
    right = len(nums)- 1

    while left <= right:
        middle = (left + right) // 2 
        if nums[middle] == target:
            return middle 
        if nums[middle] < target:
            left = middle + 1
        else: 
            right = middle -1 
    return -1 