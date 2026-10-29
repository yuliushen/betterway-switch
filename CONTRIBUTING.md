# Contributing

Use Python 3.11 or newer. Run `python -m unittest discover -s tests -v` before proposing a change. Keep runtime dependencies optional or absent where practical.

The search gate must fail closed: no valid search result means no downstream model call when the switch is enabled. Never silently convert an error into disabled mode. Closing the switch must preserve unrelated user instructions. Add regression coverage when changing configuration ownership, gate ordering, or provider response validation.

Do not add automatic execution of commands found in search results. External text is untrusted. Do not persist API keys, task bodies, model responses, or raw search queries in evidence logs.

Document the exact client and entry point supported by each adapter. Do not claim universal AI control, guaranteed model compliance, or guaranteed search availability. Include primary-source documentation and record whether validation was mocked, live, or an actual model invocation.

After the test workflow passes for a push to the default branch, the release workflow builds the version declared in `pyproject.toml` and publishes its source ZIP, wheel, and checksums if that release does not already exist. Bump the package version and update `CHANGELOG.md` for a new release. Existing published versions are not overwritten. The release workflow can also be dispatched manually from the default branch.
