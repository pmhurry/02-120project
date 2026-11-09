# Project journal requirements

- Create a new `journal/sessionN.txt` conversation copy for every new project work
  session, using the next unused sequential number. The user explicitly requires
  these in addition to raw/readable Codex exports and work notes.
- Refresh the current session's conversation copy as the discussion continues,
  including explanation quizzes, corrections, and closeout. A continuation of the
  same work session updates its existing file rather than creating a new number
  for each message or date change.
- Run `python3 .claude/hooks/save_journal.py` to refresh saved logs, then use
  `python3 scripts/export_conversation.py journal/codex/<source-log>.jsonl journal/sessionN.txt`.
  Choose the source log for the current session; strip IDE context and preserve
  recorded user/assistant wording. Do not invent messages or include internal reasoning.
- Link new conversation copies in `journal/README.md` and include them in the
  session's Git closeout. State any unavailable transcript content honestly.
