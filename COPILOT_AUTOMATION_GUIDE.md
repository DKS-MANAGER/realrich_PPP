# ACTIONABLE EXECUTION GUIDE: VS CODE + COPILOT AUTOMATION

## PART 1: SETUP YOUR ENVIRONMENT (5 MINUTES)

### Step 1: Install Required VS Code Extensions

Install these extensions in VS Code (Cmd+Shift+X or Ctrl+Shift+X):

1. **Python (Microsoft)**
   - ID: `ms-python.python`
   - Provides: Python environment management, debugging, testing

2. **Jupyter (Microsoft)**
   - ID: `ms-toolsai.jupyter`
   - Provides: Notebook support, cell execution

3. **GitHub Copilot**
   - ID: `github.copilot`
   - Provides: AI code generation, suggestions

4. **Python Test Explorer**
   - ID: `littlefoxteam.vscode-python-test-adapter`
   - Provides: Run tests directly in VS Code

5. **Code Runner (optional, for quick execution)**
   - ID: `formulahendry.code-runner`

### Step 2: Verify Python Installation

```bash
# In VS Code terminal:
python --version  # Should show 3.8+
pip --version

# Install required libraries:
pip install jupyter numpy pandas matplotlib scikit-learn pytest
```

### Step 3: Create Project Structure

```bash
# Create folder structure:
mkdir python_exercises
cd python_exercises

# Create subdirectories:
mkdir solutions
mkdir tests
mkdir data

# Create notebook:
touch exercises.ipynb
touch README.md
```

---

## PART 2: COPILOT INTEGRATION WORKFLOW (DETAILED)

### Workflow 1: Basic Exercise + Solution Generation

**Scenario:** You want to generate Exercise 2.2 (Type Conversion) with solution

#### Step A: Open Copilot Chat

```
In VS Code:
  Cmd+I (Mac) or Ctrl+I (Windows/Linux)
  → Opens inline Copilot chat
  
  OR
  
  Cmd+Shift+I → Opens Copilot Chat panel (separate window)
```

#### Step B: Paste Exercise Template

```
Copy-paste the following into Copilot:

---START PROMPT---

Create a complete Python exercise with solution:

EXERCISE TITLE: Type Conversion Robustness
DIFFICULTY: Intermediate
TOPIC: Variables & Data Types
LEARNING OBJECTIVE: Handle mixed types, graceful error handling

EXERCISE DESCRIPTION:
Challenge: Create a "data type converter" function:
  Input: A mixed list [10, "20.5", True, "error", None]
  Output:
    - Convert valid values to float
    - Replace None with 0
    - Count conversion errors
    
  Constraint: Use try-except blocks; return tuple(results, error_count)

REQUEST:
1. Provide complete solution with docstring
2. Add 4 test cases (normal, edge cases, errors)
3. Explain the approach
4. Note time complexity

---END PROMPT---
```

#### Step C: Review Copilot Output

Copilot will generate:

```python
def clean_sensor_data(raw_data: list) -> tuple[list[float], int]:
    """
    Sanitizes raw sensor data streams by converting to float and handling errors.
    
    Args:
        raw_data (list): A list of mixed-type inputs (int, float, str, None).
    
    Returns:
        tuple[list[float], int]: Cleaned floats and count of discarded values.
    """
    valid_data = []
    discarded = 0
    
    for x in raw_data:
        if x is None or (isinstance(x, str) and x.strip() == ""):
            valid_data.append(0.0)
            continue
        
        try:
            valid_data.append(float(x))
        except (ValueError, TypeError):
            discarded += 1
    
    return valid_data, discarded

# Test Cases
def test_clean_sensor_data():
    # Test 1: Normal mixed types
    result, errors = clean_sensor_data([10, "20.5", True, None])
    assert result == [10.0, 20.5, 1.0, 0.0]
    assert errors == 0
    
    # Test 2: With errors
    result, errors = clean_sensor_data([10, "error", "abc"])
    assert result == [10.0]
    assert errors == 2
    
    # Test 3: All errors
    result, errors = clean_sensor_data(["x", "y", "z"])
    assert result == []
    assert errors == 3
    
    # Test 4: Empty input
    result, errors = clean_sensor_data([])
    assert result == []
    assert errors == 0
    
    print("✅ All tests passed!")

# Complexity:
# Time:  O(n) - iterate through all elements once
# Space: O(n) - store results
```

#### Step D: Copy to Notebook

```
1. Select all Copilot output (Cmd+A in chat)
2. Copy (Cmd+C)
3. Open exercises.ipynb
4. Create new cell (Cmd+Shift+A)
5. Paste (Cmd+V)
6. Add markdown cell above with:
   ## Exercise 2.2: Type Conversion
   **Challenge**: [copy challenge description]
   **Constraint**: Use try-except only
```

#### Step E: Run & Validate

```
In notebook:
  1. Select solution cell
  2. Ctrl+Shift+Enter → Run cell
  3. Check output for errors
  4. If error: Tell Copilot "Fix this error: [ERROR MESSAGE]"
```

---

### Workflow 2: Quick Bug Fix Using Copilot

**Scenario:** Your code has an error

```python
# In notebook cell, your code is:
def add_numbers(a, b)  # Syntax error: missing colon
    return a + b

# Error appears: SyntaxError: expected ':'
```

**Fix Process:**

```
1. Highlight problematic code
2. Cmd+I → Open Copilot chat
3. Type: "Fix this syntax error"
4. Copilot suggests: def add_numbers(a, b):
5. Hit Tab or click suggestion to accept
```

---

### Workflow 3: Batch Exercise Generation

**Scenario:** Generate all 15 exercises for Phase 1 at once

#### Step 1: Create Master Prompt

Create in file: `prompts/phase1_batch.txt`

```
---START---

BATCH REQUEST: Generate 15 Python Exercises (Phase 1: Fundamentals)

For each topic below, create 3 exercises (Basic, Intermediate, Advanced):

TOPIC 1: PRINT & COMMENTS
TOPIC 2: VARIABLES & DATA TYPES
TOPIC 3: NUMBERS (INT, FLOAT, COMPLEX)
TOPIC 4: STRINGS & STRING METHODS
TOPIC 5: BOOLEANS & LOGICAL OPERATIONS

For EACH exercise, provide:
1. Challenge description (2-3 lines)
2. Complete Python solution (with docstring)
3. 2 test cases
4. Expected output

Format each as: ## TOPIC - Exercise X.Y (DIFFICULTY)

---END---
```

#### Step 2: Use Copilot in Batch Mode

```
Option A: In Copilot Chat
  1. Cmd+Shift+I (open Copilot panel)
  2. Paste master prompt
  3. Copilot generates all 15 exercises (may take 2-3 minutes)

Option B: Use GPT-4 / Claude via Extension
  (Requires additional setup; more capable for batch generation)
```

#### Step 3: Parse & Organize Output

```python
# Use this helper to parse Copilot output into separate files:

import re
import os

raw_output = """[PASTE COPILOT RESPONSE]"""

# Split by exercise header
exercises = re.split(r'## TOPIC \d+ -', raw_output)

for i, exercise in enumerate(exercises[1:], 1):
    filename = f"solutions/exercise_{i:02d}.py"
    with open(filename, 'w') as f:
        f.write(exercise.strip())
    print(f"✅ Created {filename}")
```

---

## PART 3: AUTOMATED TESTING SETUP

### Step 1: Create Test Framework

File: `tests/test_phase1.py`

```python
import pytest
import sys
sys.path.insert(0, '../solutions')

from phase1_fundamentals import *

class TestVariablesDataTypes:
    """Tests for Exercise 2.1 & 2.2"""
    
    def test_type_conversion_basic(self):
        """Test normal type conversion"""
        result, errors = clean_sensor_data([10, "20.5", None])
        assert result == [10.0, 20.5, 0.0]
        assert errors == 0
    
    def test_type_conversion_with_errors(self):
        """Test error handling"""
        result, errors = clean_sensor_data(["invalid", "err"])
        assert result == []
        assert errors == 2
    
    def test_type_conversion_mixed(self):
        """Test mixed valid/invalid"""
        result, errors = clean_sensor_data([1, "2.5", "bad", None, True])
        assert result == [1.0, 2.5, 0.0, 1.0]
        assert errors == 1

class TestStrings:
    """Tests for Exercise 4.x"""
    
    def test_string_operations(self):
        text = "Python Programming"
        assert text.upper() == "PYTHON PROGRAMMING"
        assert text.lower() == "python programming"
        assert len(text) == 19

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
```

### Step 2: Run Tests from VS Code

#### Method 1: VS Code Test Explorer

```
1. Install "Python Test Explorer" extension (see Part 1)
2. Open test file: tests/test_phase1.py
3. Click "Run Tests" button (appears in editor)
4. Results show in "Test Explorer" panel (Cmd+Shift+D)
```

#### Method 2: Terminal Command

```bash
# In VS Code terminal:
cd python_exercises
pytest tests/test_phase1.py -v

# Expected output:
# test_type_conversion_basic PASSED
# test_type_conversion_with_errors PASSED
# test_type_conversion_mixed PASSED
# ======================== 3 passed in 0.05s ========================
```

#### Method 3: Code Runner Extension

```
1. Right-click test file
2. Select "Run Code"
3. Output appears in "Run Code Output" terminal
```

---

## PART 4: EXECUTION CHECKLIST (COPY-PASTE READY)

Use this for each exercise:

### ✅ PRE-EXERCISE CHECKLIST

```
# Exercise 2.2: Type Conversion

## Before Starting:
- [ ] Read exercise description carefully
- [ ] Understand constraints
- [ ] Identify input/output format
- [ ] Note edge cases to handle

## Learning Objective:
- [ ] Type conversion methods (int, float, str)
- [ ] Exception handling (try/except)
- [ ] Error counting and logging
```

### ✅ SOLUTION DEVELOPMENT CHECKLIST

```
## During Development:
- [ ] Write function skeleton with docstring
- [ ] Implement core logic
- [ ] Add try/except blocks
- [ ] Test with normal inputs
- [ ] Test with edge cases
- [ ] Verify error handling
```

### ✅ TESTING CHECKLIST

```
## After Solution:
- [ ] Run solution cell (Ctrl+Shift+Enter)
- [ ] Check for runtime errors
- [ ] Run test cases (pytest)
- [ ] All tests pass (green checkmarks)
- [ ] Check code style (PEP 8)
- [ ] Add inline comments
```

### ✅ DOCUMENTATION CHECKLIST

```
## Before Submitting:
- [ ] Docstring explains purpose
- [ ] Type hints included (def func(x: int) -> int:)
- [ ] Complexity noted (Time: O(n), Space: O(1))
- [ ] Usage example provided
- [ ] Edge cases documented
```

---

## PART 5: QUICK REFERENCE COPILOT PROMPTS

### Generate Solution for Exercise

```
"Create a complete, well-documented Python solution for:
[PASTE EXERCISE DESCRIPTION]

Include:
1. Full working code
2. Docstring with Args/Returns
3. 3 test cases
4. Time/space complexity"
```

### Explain Existing Code

```
"Explain this Python code in detail, line by line:
[PASTE CODE]

Focus on:
1. Purpose of each section
2. Why this approach was chosen
3. Potential improvements"
```

### Fix Bugs

```
"I'm getting this error:
[PASTE ERROR MESSAGE]

Code:
[PASTE PROBLEMATIC CODE]

Help me fix it while maintaining the original intent."
```

### Optimize Performance

```
"Optimize this code for performance without changing functionality:
[PASTE CODE]

Explain:
1. What was slow
2. How you improved it
3. Performance impact (before/after)"
```

### Generate Test Cases

```
"Generate 5 comprehensive test cases for this function:
[PASTE FUNCTION]

Include:
1. Normal operation
2. Edge cases
3. Error conditions
4. Boundary values
5. Performance stress test"
```

### Create Type Hints

```
"Add proper Python type hints to this function:
[PASTE CODE]

Use:
- typing module if needed
- Optional for nullable values
- List[T] for collections
- Callable for functions"
```

---

## PART 6: AUTOMATION SCRIPTS

### Script 1: Batch Run All Exercises

File: `run_all_exercises.py`

```python
#!/usr/bin/env python3
import subprocess
import os
import json
from datetime import datetime

def run_exercise_batch():
    """Run all exercise notebooks and collect results."""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "exercises": []
    }
    
    # Find all notebook cells with test functions
    notebooks = [
        "solutions/phase1_fundamentals.py",
        "solutions/phase2_collections.py",
        # Add more as created
    ]
    
    for nb in notebooks:
        if not os.path.exists(nb):
            continue
        
        print(f"🧪 Running {nb}...")
        
        try:
            # Execute and capture output
            result = subprocess.run(
                ["python", nb],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
            
            results["exercises"].append({
                "name": nb,
                "status": status,
                "output": result.stdout,
                "errors": result.stderr
            })
            
            print(f"  {status}")
        
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ TIMEOUT")
            results["exercises"].append({
                "name": nb,
                "status": "⏱️ TIMEOUT"
            })
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to test_results.json")
    return results

if __name__ == "__main__":
    run_exercise_batch()
```

**Run it:**

```bash
python run_all_exercises.py
```

### Script 2: Generate Exercise Template

File: `generate_template.py`

```python
#!/usr/bin/env python3

TEMPLATE = '''
"""
Exercise Template: {title}
Difficulty: {difficulty}
Topic: {topic}
"""

def solve_{exercise_id}():
    """
    {description}
    
    Returns:
        {return_type}: {return_description}
    """
    pass


def test_{exercise_id}():
    """Test cases for exercise {exercise_id}"""
    
    # Test 1: Normal case
    result = solve_{exercise_id}()
    assert result == expected, f"Test 1 failed: {{result}}"
    
    # Test 2: Edge case
    result = solve_{exercise_id}()
    assert result == expected, f"Test 2 failed: {{result}}"
    
    print("✅ All tests passed!")


if __name__ == "__main__":
    test_{exercise_id}()
'''

def generate(title, difficulty, topic, exercise_id, description, return_type, return_desc):
    return TEMPLATE.format(
        title=title,
        difficulty=difficulty,
        topic=topic,
        exercise_id=exercise_id,
        description=description,
        return_type=return_type,
        return_description=return_desc
    )

if __name__ == "__main__":
    code = generate(
        title="Type Conversion",
        difficulty="Intermediate",
        topic="Variables & Data Types",
        exercise_id="2_2",
        description="Convert mixed types to float, handle errors",
        return_type="tuple[list, int]",
        return_desc="Cleaned values and error count"
    )
    print(code)
```

---

## PART 7: MONITORING & PROGRESS TRACKING

### Create Progress Dashboard

File: `progress.json`

```json
{
  "start_date": "2026-01-21",
  "phases": {
    "phase1_fundamentals": {
      "total": 15,
      "completed": 5,
      "completion_percent": 33.3,
      "exercises": [
        {"id": "1.1", "name": "Print & Comments", "status": "done", "date": "2026-01-21"},
        {"id": "1.2", "name": "Code Snippets", "status": "done", "date": "2026-01-21"},
        {"id": "2.1", "name": "Variable Assignment", "status": "done", "date": "2026-01-22"},
        {"id": "2.2", "name": "Type Conversion", "status": "in_progress", "date": "2026-01-23"},
        {"id": "2.3", "name": "Dynamic Type", "status": "pending", "date": null}
      ]
    }
  }
}
```

**Update Script:** `update_progress.py`

```python
import json
from datetime import datetime

def mark_complete(phase, exercise_id):
    with open("progress.json", "r") as f:
        progress = json.load(f)
    
    for ex in progress["phases"][phase]["exercises"]:
        if ex["id"] == exercise_id:
            ex["status"] = "done"
            ex["date"] = datetime.now().strftime("%Y-%m-%d")
    
    progress["phases"][phase]["completed"] += 1
    total = progress["phases"][phase]["total"]
    progress["phases"][phase]["completion_percent"] = (
        progress["phases"][phase]["completed"] / total * 100
    )
    
    with open("progress.json", "w") as f:
        json.dump(progress, f, indent=2)
    
    print(f"✅ Marked {exercise_id} complete!")

if __name__ == "__main__":
    mark_complete("phase1_fundamentals", "2.2")
```

---

## PART 8: TROUBLESHOOTING

### Problem 1: Copilot Not Working

**Solution:**
```
1. Verify GitHub login: Cmd+Shift+P → "GitHub: Sign out" → Sign in again
2. Check subscription: https://github.com/features/copilot
3. Reload VS Code: Cmd+K, Cmd+I
4. Reinstall extension: Uninstall → Reinstall
```

### Problem 2: Jupyter Not Running Cells

**Solution:**
```
1. Install Python extension (see Part 1)
2. Select Python interpreter: Cmd+Shift+P → "Python: Select Interpreter"
3. Choose: .venv or system Python (must be 3.8+)
4. Restart VS Code
```

### Problem 3: Tests Failing

**Solution:**
```
1. Run test with verbose output:
   pytest tests/test_phase1.py -v -s

2. Check error message carefully
3. Add debugging: print() statements before assert
4. Ask Copilot: "Why does this test fail? [PASTE ERROR]"
```

### Problem 4: Module Import Errors

**Solution:**
```
1. Verify file structure (notebooks in correct folders)
2. Add to sys.path: 
   import sys
   sys.path.insert(0, '../solutions')

3. Use relative imports in notebooks:
   from solutions.phase1 import *

4. Reinstall dependencies:
   pip install -r requirements.txt
```

---

## PART 9: FINAL WORKFLOW SUMMARY

### ✅ ONE-EXERCISE WORKFLOW (15 MINUTES)

```
1. [2 min] Read exercise description in exercises.ipynb
2. [1 min] Open Copilot (Cmd+I)
3. [2 min] Paste exercise → Get solution
4. [3 min] Copy solution → Paste into notebook cell
5. [2 min] Run cell (Ctrl+Shift+Enter)
6. [2 min] Fix any errors (ask Copilot)
7. [2 min] Run tests (pytest)
8. [1 min] Mark as complete in progress.json

Total: ~15 minutes per exercise
Target: 6-8 exercises per day
Result: Complete Phase 1 (15 exercises) in 2-3 days
```

### ✅ DAILY ROUTINE (60 MINUTES)

```
09:00-09:05: Check progress dashboard
09:05-09:20: Exercise #1 (15 min workflow)
09:20-09:35: Exercise #2
09:35-09:50: Exercise #3
09:50-10:00: Review, commit to git

4 exercises/day × 7 days = 28 exercises/week
```

---

## RESOURCES & LINKS

- **Python Docs:** https://docs.python.org/3/
- **W3Schools Python:** https://www.w3schools.com/python/
- **GitHub Copilot Docs:** https://github.com/features/copilot
- **Pytest Docs:** https://docs.pytest.org/
- **Real Python:** https://realpython.com/
