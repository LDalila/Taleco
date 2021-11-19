import difflib
import enchant
import os
import string

english_dict = enchant.Dict("en_US")

in_path = 'data/sunstein_edited'

# Tries to identify if a line is a normal text line or a potential header/footer line
def is_normal(line):
    if not line:
        return False
    l = len(line)
    dig_l = len([x for x in line if x.isdigit()])
    let_l = len([x for x in line if x.isalpha()])
    low_l = len([x for x in line if x.islower()])
    upp_l = len([x for x in line if x.isupper()])

    return low_l/l > 0.5 and upp_l/l < 0.2 and let_l/l > 0.7 and dig_l/l < 0.2


# For each file
for f in os.listdir(in_path):
    print(f)
    # Select only raw OCR output text files
    if f.endswith('.txt') and not f.endswith('_mclean.txt') and not f.endswith('_aclean.txt'):
        with open(in_path + '/' + f, 'r', encoding='utf-8') as in_file:
            data = in_file.read()
            # Remove double spaces and spaces at the beginning/end of lines
            lines = [line.strip() for line in data.replace('  ', ' ').split('\n')]
            
            # Tries to remove mid-sentence newlines that should not appear and solve hyphenation.
            # For each line ending with word1- and the next line starting with word2,
            # we have two possible merges:
            # - One long word (word1word2)
            # - One hyphenated long word (word1-word2)
            # We check the presence of both words in an English dictionary and applies the following rules:
            # long exists  compound exists  choose     example      accuracy
            # Y            Y                long       e-mail       OK
            # Y            N                long       decomp-ose   OK
            # N            Y                compound   high-rise    OK
            # N            N                long       ?            ?
            
            edited_lines = [] # The list of lines in the document after pre-processing
            cur_line = ''
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or all(x in string.punctuation for x in line):
                    if cur_line:
                        edited_lines.append(cur_line.strip())
                    cur_line = ''
                    continue
                if line.endswith('-'):
                    if i == len(lines) - 1: # Just remove the hyphen
                        cur_line += line[:-1]
                    else:
                        first_part = line.split(' ')[-1]
                        last_part = lines[i+1].split(' ')[0]
                        
                        long = first_part + last_part
                        compound = first_part + '-' + last_part
                        
                        long_e = english_dict.check(long)
                        compound_e = english_dict.check(compound)
                        
                        if english_dict.check(long): # Choose the long word
                            cur_line += line[:-1]
                        elif not english_dict.check(compound): # Also choose the long word
                            cur_line += line[:-1]
                        else: # Choose the compound word
                            cur_line += line
                else:
                    cur_line += line + ' '
            edited_lines.append(cur_line.strip())
            
            # Remove first page in UCLS documents
            if edited_lines[0] == 'University of Chicago Law School University of Chicago Law School Chicago Unbound Chicago Unbound':
                edited_lines = edited_lines[10:]
            
            # When encountering a header, remove until the beginning of the text on the next page
            lines_to_del = set()
            for i, line in enumerate(edited_lines):
                if line.startswith('HeinOnline'):
                    lines_to_del.add(i)
                    i += 1
                    while True:
                        line = edited_lines[i]
                        if is_normal(line):
                            i += 1
                            break
                        lines_to_del.add(i)
                        i += 1
                        if i >= len(edited_lines):
                            break
            
            # Delete lines that were marked for removal
            edited_lines = [i for j, i in enumerate(edited_lines) if j not in lines_to_del]
            
            # Merge lines that have bad justification parsing
            edited_lines2 = []
            cur_line = ''
            for i, line in enumerate(edited_lines):
                cur_line += line + ' '
                if i + 1 < len(edited_lines):
                    # Ignore sentence ends
                    # Only merge normal lines
                    # Don't merge footnotes
                    # Only merge short lines
                    if not any(x in line[-5:] for x in '.;?!*') \
                            and is_normal(line) and is_normal(edited_lines[i + 1]) \
                            and not edited_lines[i + 1][0] in '0123456789*' \
                            and line.count(' ') < 3 and edited_lines[i + 1].count(' ') < 3:
                        continue
                if cur_line:
                    edited_lines2.append(cur_line.strip())
                cur_line = ''
            if cur_line:
                edited_lines2.append(cur_line.strip())
            edited_lines = edited_lines2
            
            print(edited_lines)
            input()
        # Compare to gold standard
        try:
            with open(in_path + '/' + f.replace('.txt', '_mclean.txt'), 'r', encoding='utf-8') as gold_file:
                gold_lines = gold_file.read().splitlines()
        
            diff = difflib.context_diff(edited_lines, gold_lines)
            for line in diff:
                print(line)
        except FileNotFoundError:
            pass
        
        # Write to output file
        with open(in_path + '/' + f.replace('.txt', '_aclean.txt'), 'w', encoding='utf-8') as out_file:
            out_file.writelines('\n'.join(edited_lines))
