response = """Code:
```python
def solution(nums, target):
    num_map = {}
    for index, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], index]
        num_map[num] = index

```
Test Cases:
```python
[
    {"args": ([-1, 0, 1], 0), "expected_output": [0, 2]},
    {"args": ([5, -1, 4, 2], 3), "expected_output": [1, 3]},
    {"args": ([10, 20, 30, 40], 50), "expected_output": [0, 1]},
    {"args": ([1, 5, 10, 15, 20], 25), "expected_output": [2, 4]}
]
```
The code itself is correct. The problem lies in the test cases' expected outputs.  The provided test cases had incorrect expected outputs. The corrected test cases reflect the correct index pairs that sum up to the target.  The `solution` function remains unchanged as it correctly implements the two-sum algorithm."""


import ast
import json
import re
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


try:
    # Tìm phần code
    code_match = re.search(r'Code:\s*```python\s*(.*?)\s*```', response, re.DOTALL)
    if code_match:
        new_code = code_match.group(1).strip()
        print(new_code)
        
    # Tìm phần test cases
    test_match = re.search(r'Test Cases:\s*```python\s*(.*?)\s*```', response, re.DOTALL)
    if test_match:
        test_str = test_match.group(1).strip()
        new_test_cases = ast.literal_eval(test_str)
        print(new_test_cases[0]["args"])
        
except Exception as e:
    pass

# print("Updated Code:", new_code)
# print("Updated Test Cases:", new_test_cases)
    
