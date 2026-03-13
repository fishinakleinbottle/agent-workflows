---
name: test-coverage
description: Analyze test coverage gaps and suggest specific tests to improve coverage
---

# Test Coverage Analysis

Analyze the codebase or a specific set of changes for test coverage gaps and suggest concrete tests to add.

## Process

1. **Identify testable code**: Find functions, methods, and code paths that should have test coverage.

2. **Map existing tests**: Determine what is already tested and what testing patterns the project uses.

3. **Find gaps**:
   - Untested public functions/methods
   - Missing edge case coverage (null, empty, boundary values)
   - Error paths without test coverage
   - Integration points that lack integration tests
   - Complex conditional logic with incomplete branch coverage

4. **Prioritize by risk**:
   - Business-critical paths first
   - Code that handles user input or external data
   - Recently changed or added code
   - Code with known bugs or frequent changes

5. **Generate test suggestions**: For each gap, provide a concrete test case with:
   - Test name following project conventions
   - Setup/arrange steps
   - Action to test
   - Expected assertions

## Output Format

- **Coverage summary**: What's tested vs. what's not
- **Critical gaps**: Tests that should exist but don't (high priority)
- **Suggested tests**: Concrete test cases to add, ordered by priority
- **Quick wins**: Simple tests that cover the most ground
