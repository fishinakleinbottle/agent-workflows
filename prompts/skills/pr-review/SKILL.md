---
name: pr-review
description: Review pull requests for correctness, missing tests, and security issues
---

# PR Review

Review the current pull request thoroughly, focusing on correctness, security, and completeness.

## Process

1. **Understand the change**: Read the PR description and all modified files. Identify the intent behind the change.

2. **Check correctness**:
   - Does the code do what the PR description claims?
   - Are there edge cases that aren't handled?
   - Are error paths handled properly?
   - Could any changes break existing functionality?

3. **Check for security issues**:
   - Input validation and sanitization
   - Authentication/authorization gaps
   - Injection vulnerabilities (SQL, XSS, command injection)
   - Secrets or credentials in code
   - Unsafe deserialization

4. **Check test coverage**:
   - Are new code paths tested?
   - Are edge cases covered?
   - Do existing tests still pass with these changes?
   - Are there integration tests where needed?

5. **Check code quality**:
   - Is the code readable and well-structured?
   - Are there unnecessary complexity or over-engineering?
   - Does it follow the project's existing patterns?
   - Are there any performance concerns?

## Output Format

Provide a structured review with:
- **Summary**: One-line summary of the change
- **Risk level**: Low / Medium / High
- **Issues found**: List with severity (Critical / Warning / Suggestion)
- **Missing tests**: Specific scenarios that need test coverage
- **Approval recommendation**: Approve / Request Changes / Needs Discussion
