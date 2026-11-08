# Build journal

Checkpoint 1 work days: October 27–30 and November 1, 2026.

Checkpoint 2 begins November 6 with the pivot to the Spatial Target Prioritization
Engine. [Session 1 work notes](checkpoint2_session1_notes.md) describe data preparation
and planning; they are not a substitute for the required conversation/session export.

November 6 Codex export: [readable session](readable/rollout-2026-11-06T20-38-14-01a1b3a8-0032-7dc0-b5f0-5def554d8455.md)
and [raw session](codex/rollout-2026-11-06T20-38-14-01a1b3a8-0032-7dc0-b5f0-5def554d8455.jsonl).
The current [course setup instructions](https://phcompeau.github.io/ProgrammingforScientists2026Undergrad/project/journal/setup.txt)
explicitly support both Codex and Claude Code session logs (checked November 7).

November 7: [session 2 work notes](checkpoint2_session2_notes.md),
[readable Codex export](readable/rollout-2026-11-07T22-34-35-01a1b938-e1d9-7c83-a2a2-0509e262916f.md),
and [raw export](codex/rollout-2026-11-07T22-34-35-01a1b938-e1d9-7c83-a2a2-0509e262916f.jsonl).
Student review is pending; work notes are not a verbatim conversation copy.

The readable exports below come from the native Codex session logs in [codex/](codex/). Each entry includes the recorded conversation and tool-use notes.

| Day | Date | Readable Codex session | Conversation copy |
| --- | --- | --- | --- |
| 1 | 2026-10-27 | [Session 1](readable/rollout-2026-10-27T21-05-07-01a1800a-15bb-7600-9c11-f2c6c19e0dfa.md) | [session1.txt](session1.txt) |
| 2 | 2026-10-28 | [Session 2](readable/rollout-2026-10-28T14-43-00-01a183d2-9b9a-7d72-ba08-6fb44a38026b.md) | [session2.txt](session2.txt) |
| 3 | 2026-10-29 | [Session 3](readable/rollout-2026-10-29T18-05-47-01a189b2-a0ae-79f3-9d58-62d0f8cf78fa.md) | [session3.txt](session3.txt) |
| 4 | 2026-10-30 | [Session 4](readable/rollout-2026-10-30T16-53-42-01a18e96-fcdf-7e40-9f5d-838fdb874f5d.md) | [session4.txt](session4.txt) |
| 5 | 2026-11-01 | [Session 5](readable/rollout-2026-11-01T14-50-38-01a198a9-f808-7f60-8b15-323f6c1cfa50.md) | [session5.txt](session5.txt) |
| 6 | 2026-11-06 | [Session 6](readable/rollout-2026-11-06T20-38-14-01a1b3a8-0032-7dc0-b5f0-5def554d8455.md) | [session6.txt](session6.txt) |
| 7 | 2026-11-07 | [Session 7](readable/rollout-2026-11-07T22-34-35-01a1b938-e1d9-7c83-a2a2-0509e262916f.md) | [session7.txt](session7.txt) |

The course exporter is installed at `.claude/hooks/save_journal.py`. The local pre-commit hook refreshes raw and readable exports before commits. The text conversation copies are maintained separately.

See [checkpoint 1](../CHECKPOINT_1.md) for the historical baseline and
[checkpoint 2](../CHECKPOINT_2.md) for the current five-session plan.

## Setup verification — November 7, 2026

The exporter at `.claude/hooks/save_journal.py` and executable local Git hook at
`.git/hooks/pre-commit` match the current published course files byte for byte.
Codex uses the same `.claude/` exporter path; Claude-specific session hooks are
skipped when setting up with Codex. The older `.codex/` configuration is not used
by this Git hook and is not required by the current course setup.

Manual export verified seven raw Codex sessions with seven readable Markdown
counterparts. A scan of raw and readable journal files found no standard token
patterns or suspicious password/key/token assignments. The exporter redacts common
token formats; manually review any unusual credentials before sharing logs.
Neither `journal/` nor `.claude/` is ignored. The local Git hook refreshes and stages
journal files at commit time; `.git/hooks/` itself is not versioned.

Submit the repository link on Canvas and commit/push regularly. If project work
also happens in ChatGPT or the Claude app, maintain `journal/chat_links.md` with
shared conversation links as described on the course journal page. No chat-app
links were provided in this session.
