---
name: code-review
description: Review code for quality, maintainability, and adherence to best practices
---

# Code Review

Perform a thorough code review focused on quality, maintainability, and best practices.

## Process

1. **Understand context**: Read the code and understand its purpose within the broader system.

2. **Check structure and design**:
   - Single Responsibility: Does each function/class do one thing?
   - Appropriate abstraction level — not too abstract, not too concrete
   - Clear interfaces and boundaries
   - No unnecessary coupling between components

3. **Check readability**:
   - Clear naming for variables, functions, and types
   - Logical code organization and flow
   - Complex logic is broken into understandable steps
   - No dead code or commented-out blocks

4. **Check robustness**:
   - Error handling is appropriate (not swallowed, not excessive)
   - Resource cleanup (connections, file handles, locks)
   - Thread safety where applicable
   - Graceful degradation for external dependencies

5. **Check performance** (only if relevant):
   - Obvious N+1 queries or unnecessary loops
   - Large allocations in hot paths
   - Missing indexes for common queries
   - Unbounded growth (caches, logs, queues)

## Output Format

- **Overall assessment**: Brief summary of code quality
- **Issues**: List with severity and specific file:line references
- **Positive patterns**: Things done well (reinforce good practices)
- **Suggestions**: Improvements that aren't bugs but would help maintainability
