#!/usr/bin/env python
import pytest
import sys

def main():
    """Run the test suite"""
    args = [
        "--strict-markers",
        "--tb=short",
        "-v",
        "tests"
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main()) 