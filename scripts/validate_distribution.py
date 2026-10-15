#!/usr/bin/env python3
"""Offline structure, empty-template, local-link and prompt-sync checks."""
from pathlib import Path
import csv
import io
import json
import re
import sys
sys.dont_write_bytecode = True
from build_chatgpt_prompt import render

root = Path(__file__).resolve().parents[1]
skill = (root/'SKILL.md').read_text(encoding='utf-8')
assert skill.startswith('---\n'), 'Missing frontmatter'
header = skill.split('---', 2)[1]
assert re.search(r'^name: manage-family-n600k$', header, re.M)
assert re.search(r'^description: .+', header, re.M)
assert len(skill.splitlines()) < 500
for path in root.rglob('*.md'):
    for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if not re.match(r'[a-z]+://|#', link):
            assert (path.parent/link.split('#')[0]).exists(), f'Broken local link: {path}: {link}'
case = json.loads((root/'assets/case-template.json').read_text(encoding='utf-8'))
assert case['template_only'] is True
assert case['household_alias'] is None
assert all(c['child_alias'] is None for c in case['children'])
assert len(list(csv.reader(io.StringIO((root/'assets/document-register.csv').read_text(encoding='utf-8'))))) == 1
prompt = (root/'CHATGPT-PROMPT.md').read_text(encoding='utf-8')
assert prompt == render(), 'Generated prompt is stale'
assert not re.search(r'\]\((?:references|assets)/', prompt), 'Prompt depends on local file'
for snippet in ['שינוי לשכה לאחר מכן עלול להיות מורכב', 'להגיש במהלך הביקור בארה״ב', 'כתובת אמריקאית אמינה', 'אין להוסיף נוטריון או אפוסטיל', 'תור, אישור מקדים או חלוף זמן אינם אזרחות']:
    assert snippet in prompt, f'Missing workflow guardrail: {snippet}'
for path in root.rglob('*'):
    if path.is_file() and '__pycache__' not in str(path):
        text = path.read_text(encoding='utf-8')
        assert not re.search(r'skill-[0-9a-f]{32}', text), f'Private skill ID: {path}'
        assert ('chatgpt.com/' + 'skills?') not in text, f'Private skill URL: {path}'
        assert not re.search(r'https://(?:docs\.google\.com|drive\.google\.com|notion\.so)/', text), f'Private document link: {path}'
print('PASS: frontmatter, required files, local links, empty templates, standalone prompt sync, workflow guardrails, private-link checks.')
print('These are static checks, not legal verification or a remote installation test. Review all files before publication.')
