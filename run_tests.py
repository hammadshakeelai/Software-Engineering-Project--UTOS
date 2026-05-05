#!/usr/bin/env python
"""UTOS Test Runner

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v        # Verbose
    python run_tests.py rbac        # Run RBAC tests only
    python run_tests.py data        # Run data entry tests only
    python run_tests.py solver       # Run solver tests only
    python run_tests.py integration # Run integration tests only
"""

import sys
import unittest

CATEGORIES = {
    "rbac": "tests.test_all_features.RBACTests",
    "data": "tests.test_all_features.MasterDataAPITests",
    "solver": "tests.test_all_features.TimetableGenerationTests",
    "http": "tests.test_all_features.HTTPAPITests",
    "requests": "tests.test_all_features.ChangeRequestTests",
    "lock": "tests.test_all_features.LockUnlockTests",
    "integration": "tests.test_integration",
    "solver_unit": "tests.test_solver",
}

def main():
    category = sys.argv[1] if len(sys.argv) > 1 else None
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if category and category in CATEGORIES:
        test_path = CATEGORIES[category]
        if "." in test_path:
            suite.addTests(loader.loadTestsFromName(test_path))
        else:
            suite.addTests(loader.loadTestsFromName(f"tests.test_{category}"))
            suite.addTests(loader.loadTestsFromName(f"tests.test_integration"))
    else:
        # Run all tests
        suite.addTests(loader.loadTestsFromName("tests.test_all_features"))
        suite.addTests(loader.loadTestsFromName("tests.test_integration"))
        suite.addTests(loader.loadTestsFromName("tests.test_solver"))
    
    verbosity = 2 if "-v" in sys.argv else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())