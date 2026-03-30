
import sys
import os

# Add the 'pkg' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'pkg')))

from calculator import Calculator

def run_tests():
    calculator = Calculator()
    test_cases = [
        ("1 + 2", 3.0),
        ("5 - 3", 2.0),
        ("2 * 4", 8.0),
        ("10 / 2", 5.0),
        ("1 + 2 * 3", 7.0),  # Test precedence
        ("10 / 0", "float division by zero"), # Should raise an error
        ("1 +", "not enough operands for operator +"),
        ("", None),
        ("   ", None),
        ("abc", "invalid token: abc"),
        ("1 + 2 + 3", 6.0),
        ("1 * 2 / 3", 0.6666666666666666), # Test multiple operators with different precedence
    ]

    for expression, expected in test_cases:
        try:
            result = calculator.evaluate(expression)
            print(f"Expression: '{expression}', Result: {result}, Expected: {expected}")
            assert result == expected or (isinstance(expected, str) and expected in str(result)), f"Test failed for '{expression}'. Expected {expected}, got {result}"
        except ValueError as e:
            print(f"Expression: '{expression}', Error: {e}, Expected error: {expected}")
            assert isinstance(expected, str) and expected in str(e), f"Test failed for '{expression}'. Expected error containing '{expected}', got '{e}'"
        except ZeroDivisionError as e:
            print(f"Expression: '{expression}', Error: {e}, Expected error: {expected}")
            assert isinstance(expected, str) and expected in str(e), f"Test failed for '{expression}'. Expected error containing '{expected}', got '{e}'"
        except Exception as e:
            print(f"Expression: '{expression}', Unexpected error: {e}")
            assert False, f"Test failed for '{expression}'. Unexpected error: {e}"

    print("\nAll tests completed.")

if __name__ == "__main__":
    run_tests()
