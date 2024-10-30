from tests.TestFramework import *
from game_engine.effects import *
import os
import importlib
import inspect

def collect_test_cases():
    """Automatically collect all test cases from test_cases directory"""
    test_cases_dir = "tests/test_cases"
    test_classes = []
    
    # Get all python files in test_cases directory
    for file in os.listdir(test_cases_dir):
        if (file.startswith("test_") or file.endswith("_test.py")) and file.endswith(".py"):
            # Convert filename to module name
            module_name = f"tests.test_cases.{file[:-3]}"
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find all classes in module that end with 'Test' or 'Tests'
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    (name.endswith('Test') or name.endswith('Tests')) and
                    name != 'GameTestCase'):
                    test_classes.append(obj)
    
    return test_classes

def run_all_tests():
    """Run all test cases with nice output"""
    test_classes = collect_test_cases()

    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\nRunning tests in {class_name}:")
        
        # Get all test methods in the class
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            test = test_class()
            try:
                # Run the test
                getattr(test, method_name)()
                passed_tests += 1
                print(f"  ✓ {method_name} passed")
            except AssertionError as e:
                print(f"  ✗ {method_name} failed")
                print(f"    {str(e)}")
            except Exception as e:
                print(f"  ✗ {method_name} failed")
                print(f"    Error: {str(e)}")
                raise  # Re-raise the exception for debugging
    
    print(f"\nTest Results: {passed_tests}/{total_tests} tests passed")

if __name__ == '__main__':
    # For debugging a specific test:
    # run_specific_test()
    
    # For running all tests:
    run_all_tests()
