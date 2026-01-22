"""
Phase 1: Fundamentals - Solution File
Topics: Variables, Numbers, Strings, Booleans

This file contains solutions for beginner-level exercises.
Import solutions in the notebook or run tests independently.
"""

# ============================================================================
# Exercise 1.1: Print & Comments (Basic)
# ============================================================================

def exercise_1_1():
    """
    Challenge: Print "Hello, World!" with comments explaining print().
    """
    # The print() function outputs text to the console
    # It takes one or more arguments and displays them
    print("Hello, World!")
    
    """
    This is a multi-line comment.
    print() is a built-in function in Python.
    It automatically adds a newline at the end.
    """


# ============================================================================
# Exercise 1.2: Code Snippets (Intermediate)
# ============================================================================

def exercise_1_2():
    """
    Challenge: Demonstrate multiple print variations.
    """
    # 1. Multi-line string
    print("""This is a
multi-line
string example""")
    
    # 2. Variable concatenation
    name, age = "Alice", 30
    print("Name: " + name + ", Age: " + str(age))
    
    # 3. f-string formatting
    print(f"Name: {name}, Age: {age}")


# ============================================================================
# Exercise 1.3: Interactive Script (Advanced)
# ============================================================================

def exercise_1_3():
    """
    Challenge: Create personal summary with input validation.
    """
    name = input("Enter your name: ").strip() or "Anonymous"
    age = input("Enter your age: ").strip() or "Unknown"
    city = input("Enter your city: ").strip() or "Unknown"
    
    bio = f"""
    ═══════════════════════════
    Personal Summary
    ═══════════════════════════
    Name:  {name} (type: {type(name).__name__})
    Age:   {age} (type: {type(age).__name__})
    City:  {city} (type: {type(city).__name__})
    ═══════════════════════════
    """
    
    print(bio)


# ============================================================================
# Exercise 2.1: Variable Assignment (Basic)
# ============================================================================

def exercise_2_1():
    """
    Challenge: Create 5 variables of different types and display with type().
    """
    var_int = 42
    var_float = 3.14159
    var_str = "Python"
    var_bool = True
    var_none = None
    
    variables = [var_int, var_float, var_str, var_bool, var_none]
    
    for var in variables:
        print(f"Value: {var:<10} | Type: {type(var)}")


# ============================================================================
# Exercise 2.2: Type Conversion (Intermediate) - Already implemented in notebook
# ============================================================================
# See Module 1: clean_sensor_data_v2()


# ============================================================================
# Exercise 2.3: Dynamic Type Handling (Advanced)
# ============================================================================

def exercise_2_3(expression: str):
    """
    Challenge: Build a flexible calculator without eval().
    
    Args:
        expression (str): Math expression like "10 + 5.5"
    
    Returns:
        tuple: (result, type_log)
    """
    type_log = []
    
    try:
        # Parse the expression safely
        parts = expression.split()
        if len(parts) != 3:
            raise ValueError("Invalid format. Use: 'num1 operator num2'")
        
        num1_str, operator, num2_str = parts
        
        # Convert to appropriate types
        num1 = float(num1_str) if '.' in num1_str else int(num1_str)
        num2 = float(num2_str) if '.' in num2_str else int(num2_str)
        
        type_log.append(f"num1: {num1_str} -> {type(num1).__name__}")
        type_log.append(f"num2: {num2_str} -> {type(num2).__name__}")
        
        # Perform operation
        operations = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else None,
        }
        
        if operator not in operations:
            raise ValueError(f"Unsupported operator: {operator}")
        
        result = operations[operator](num1, num2)
        
        if result is None:
            raise ZeroDivisionError("Division by zero")
        
        type_log.append(f"result: {result} ({type(result).__name__})")
        
        return result, type_log
        
    except (ValueError, ZeroDivisionError) as e:
        type_log.append(f"ERROR: {e}")
        return None, type_log


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    print("=== Testing Phase 1 Solutions ===\n")
    
    print("Exercise 1.1:")
    exercise_1_1()
    
    print("\nExercise 1.2:")
    exercise_1_2()
    
    print("\nExercise 2.1:")
    exercise_2_1()
    
    print("\nExercise 2.3:")
    result, log = exercise_2_3("10 + 5.5")
    print(f"Result: {result}")
    for entry in log:
        print(f"  {entry}")
