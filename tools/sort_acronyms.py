#!/usr/bin/python3

import re
import sys

if len(sys.argv) not in [2, 3]:
    print(f'Usage: {sys.argv[0]} <FILE> [<OUT-FILE>]', file=sys.stderr)
    exit(1)

in_file = sys.argv[1]
out_file = sys.argv[2] if len(sys.argv) == 3 else '/dev/stdout'

begin_acronym_area = re.compile(r'^\s*\\begin{acronym}')
match_begin_acronym_area = lambda s: re.match(begin_acronym_area, s)

acronym_definition = re.compile(r'^\s*\\acro')
match_acronym_definition = lambda s: re.match(acronym_definition, s)

acronym_name = re.compile(r'\[[^\]]*\]')
extract_acronym_name = lambda s: re.search(acronym_name, s).group(0)

with open(in_file, 'r') as file:
    lines = list(map(lambda s: s.rstrip(), file.readlines()))

acronym_definition_lines = list(filter(match_acronym_definition, lines[:]))
sorted_acronym_definition_lines = sorted(acronym_definition_lines, key=extract_acronym_name)

longest_acronym_name = max(map(extract_acronym_name, acronym_definition_lines), key=len)
begin_acronym_area_line = list(filter(match_begin_acronym_area, lines[:]))[0]
begin_acronym_area_new_line = re.sub(acronym_name, longest_acronym_name, begin_acronym_area_line)

lines = [
    '% ATTENTION: This file is manipulated by a script. Only add new acronyms and run tools/sort_acronyms.py',
    begin_acronym_area_new_line,
    *sorted_acronym_definition_lines,
    '\end{acronym}'
]

with open(out_file, 'w') as f:
    print('\n'.join(lines), file=f)
