## Error Handling

- Handle errors at the appropriate level — don't catch what you can't handle.
- Use typed/structured errors over generic error strings.
- Include enough context in error messages to diagnose without a debugger.
- Don't swallow errors silently. Log or propagate them.
- Distinguish between operational errors (retry-able) and programmer errors (bugs).
- Clean up resources in error paths (connections, file handles, locks).
