#!/usr/bin/env python
"""Fix imports in test files from merithra.core.* to core.*"""

import re

test_files = [
    'tests/test_cards.py',
    'tests/test_effects.py',
    'tests/test_entities.py',
    'tests/test_state_machine.py',
]

for fname in test_files:
    with open(fname, 'r') as f:
        content = f.read()
    
    old_count = content.count('merithra.core')
    if old_count > 0:
        new_content = re.sub(r'from merithra\.core\.', 'from core.', content)
        new_content = re.sub(r'import merithra\.core\.', 'import core.', new_content)
        with open(fname, 'w') as f:
            f.write(new_content)
        print(f'{fname}: replaced {old_count} merithra.core imports')
    else:
        print(f'{fname}: no merithra.core imports found')