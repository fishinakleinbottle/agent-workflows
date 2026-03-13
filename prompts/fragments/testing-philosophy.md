## Testing Philosophy

- Tests should verify behavior, not implementation details.
- Prefer integration tests for critical paths; unit tests for complex logic.
- A failing test should clearly indicate what broke and where.
- Don't mock what you don't own — use fakes or test doubles for external services.
- Test names should describe the scenario and expected outcome.
- Avoid testing framework internals or language features.
