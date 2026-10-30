# Integration validation — 30 October 2026

- 55 offline tests passed, including 23 new research integration/transport tests
  and the existing real FFmpeg rendering test.
- Tested two-source niche selection, next-topic selection within an existing
  niche, insufficient evidence, required citations and immutable decided runs.
- Tested missing/stale sources, exact raw metric pointers, unknown values,
  scope grouping, duplicate-source identification and changed-input rejection.
- Agent-Reach transport tests use mocks: bounded read-only argument lists,
  no shell execution, caching, explicit retry, rate limits, timeouts, missing CLI
  and unsupported response versions.
- The vidIQ MCP configuration and Agent-Reach command/envelope contracts were
  checked against official documentation and the upstream source referenced in
  docs/research-integration.md.

Live vidIQ authorization in the user's Claude environment, actual Agent-Reach
network searches, and a complete Claude research/decision session were not run
here. No research credits or paid media were used for this integration's tests.
These tests are not market findings, revenue evidence or Japanese editorial QA.
Configure/authenticate the providers in the environment where Claude runs.


A subprocess CLI smoke check also completed initialization, two-source fixture
imports, analysis, decision recording and state verification. All research
values in that check were synthetic and the temporary workspace was removed.
