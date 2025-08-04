#!/usr/bin/env python3
"""
Sample Python file for testing the AI Code Analyzer.
This file demonstrates various coding patterns and potential issues.
"""

import os
import sys
from typing import List, Dict, Optional

# Global variables (potential code smell)
GLOBAL_COUNTER = 0
user_data = {}

class DataProcessor:
    """A class that processes data with some issues."""
    
    def __init__(self, data=None):
        # Missing type hints
        self.data = data if data else []
        self.results = []
    
    def process_data(self, items):
        """Process a list of items."""
        # No input validation
        for item in items:
            if item > 10:  # Magic number
                self.results.append(item * 2)
            else:
                self.results.append(item)
        return self.results
    
    def get_summary(self):
        # Inefficient list operations
        total = 0
        for result in self.results:
            total = total + result
        return {
            'total': total,
            'count': len(self.results),
            'average': total / len(self.results) if self.results else 0
        }

def fetch_user_data(user_id):
    """Fetch user data from somewhere."""
    # Potential security issue - no input sanitization
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    # No error handling
    if user_id in user_data:
        return user_data[user_id]
    else:
        return None

def main():
    """Main function with various issues."""
    global GLOBAL_COUNTER
    
    # Hard-coded values
    data = [1, 5, 15, 8, 12, 3, 20]
    
    processor = DataProcessor()
    results = processor.process_data(data)
    
    print("Processing results:")
    # Using print instead of logging
    for i in range(len(results)):  # Should use enumerate
        print(f"Item {i}: {results[i]}")
    
    summary = processor.get_summary()
    print(f"Summary: {summary}")
    
    # Unused variable
    unused_var = "This variable is never used"
    
    GLOBAL_COUNTER += 1

if __name__ == "__main__":
    main()