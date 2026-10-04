#!/usr/bin/env python
import re

for fname in ['tests/test_cards.py', 'tests/test_entities.py']:
    with open(fname, 'r') as f:
        content = f.read()
    # Finde alle Vorkommen von name " ohne =
    # Pattern: name "something" wo kein = nach name steht
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Suche nach pattern: name " ... " ohne =
        if re.search(r'name\s+"', line) and 'name="' not in line and 'name =' not in line:
            # Finde den Namen-Teil und ersetze
            new_line = re.sub(r'name\s+"', 'name="', line)
            if new_line != line:
                print(f'{fname}:{i}: FIXED: {line.rstrip()[:80]} -> {new_line.rstrip()[:80]}')
                # Wende die Änderung an
                content = content.replace(line, new_line)
    
    # Schreibe die Datei zurück (außer wenn nur Prüfungen waren)
    # Wir haben oben schon ersetzt, aber wir müssen die Datei tatsächlich speichern
    # Actually, let's just track and then do a proper fix

print("Done scanning")