"""Export a numbered conversation copy from a project's saved Codex JSONL log."""
import argparse
import json
from pathlib import Path


def export(source, output):
    messages = []
    for line in source.read_text().splitlines():
        row = json.loads(line)
        payload = row.get('payload', {})
        if row.get('type') != 'event_msg':
            continue
        kind = payload.get('type')
        if kind not in ('user_message', 'agent_message'):
            continue
        text = payload.get('message', '')
        if kind == 'user_message':
            if '## My request:' in text:
                text = text.split('## My request:', 1)[1]
            elif text.lstrip().startswith(('<environment_context>', '<external_codex_apps_open_page>')):
                continue
        text = text.strip()
        if text:
            messages.append(('USER' if kind == 'user_message' else 'ASSISTANT', text))
    if not messages:
        raise ValueError('No conversation messages found')
    header = (f'Chat transcript — {output.stem}\n\n'
              f'Source: {source.as_posix()}\n'
              'Extracted from the native Codex session log. Includes recorded user and '
              'assistant messages available at export time; excludes IDE context, tools, '
              'internal reasoning, and system/developer instructions. This is not a native '
              'Claude Code export. See the source log for message timestamps.\n\n')
    text = header + '\n\n---\n\n'.join(f'{role}:\n{text}' for role, text in messages) + '\n'
    # Match the course exporter's common credential redaction.
    import importlib.util
    spec = importlib.util.spec_from_file_location('course_journal', Path(__file__).resolve().parents[1] / '.claude/hooks/save_journal.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output.write_text(module.scrub(text))
    print(f'{output}: {len(messages)} messages exported')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    export(args.source, args.output)
