import os
import re
import shutil
import wordninja

from Levenshtein import distance
from string import punctuation
from tqdm import tqdm

# TODO Also split on caps?
# TODO Check numbers BEFORE references
# TODO Check weird ' and " (after ".( )")
# TODO Check numbers after ".( )"
# TODO Check unended paragraphs (no ".")
# TODO Check weird "?" that could be " or -, especially near punctuation or with a character right after, or with no case after
# TODO Check weird ” or “ without match

# Possibilities: 'words_usa.txt', 'words_tito_bouzout.txt', 'words_corncob_lowercase.txt', words_alpha.txt
words_file = 'words_usa.txt'

EN_WORDS = set(open(words_file).read().splitlines())
SUNSTEIN_WORDS = set(open('words_sunstein.txt').read().splitlines())
SUNSTEIN_SUB = open('words_sunstein_subst.txt').read().splitlines()
SUNSTEIN_SUB = {k: v for k, v in zip(SUNSTEIN_SUB[0::2], SUNSTEIN_SUB[1::2])}
SUNSTEIN_CASE_WORDS = set(open('words_sunstein_case.txt').read().splitlines())
SUNSTEIN_CASE_SUB = open('words_sunstein_case_subst.txt').read().splitlines()
SUNSTEIN_CASE_SUB = {k: v for k, v in zip(SUNSTEIN_CASE_SUB[0::2], SUNSTEIN_CASE_SUB[1::2])}

cutoff = 2000
context_size = 80
inner_ctx = 25
len_auto = len(SUNSTEIN_WORDS) + len(SUNSTEIN_SUB)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


RE_BRACKET = re.compile(r'\[(.)\]')
RE_DOUBLE_DASH = re.compile(r'--')
RE_LONG_ELLIPSIS = re.compile(r' *\. *\. *\. *(\. *)+')
RE_WORD_SEP = re.compile(r'[\s/\'—]')
RE_DIGITS_REF = re.compile(r'^[\d()\-,.]+$')

filenames = []
texts = []

for file in os.listdir('sunstein/processed/'):
    if not file.endswith('txt'):
        continue
    year = int(file[:4])
    # if 'final' in file and file.startswith('1988_sex'): # TODO
    if 'mclean' in file and year <= cutoff or 'cermine' in file and year > cutoff:
        file = 'sunstein/processed/' + file
        filenames.append(file)
        with open(file) as f:
            texts.append(f.read())
            
auto_operations = 0
manual_operations = 0

num_answers = [str(i) for i in range(1, 11)]


def rewind(idx, res):
    if res is not None:
        idx -= res.end()
    return idx
    

def rewind_more(idx, res, text):
    while not RE_WORD_SEP.match(text[idx]):
        idx -= 1
    idx = rewind(idx, res)
    return idx


def add_to_dict(raw_word):
    if raw_word.lower() not in SUNSTEIN_WORDS and not RE_DIGITS_REF.search(raw_word):
        SUNSTEIN_WORDS.add(raw_word.lower())
        shutil.copy('words_sunstein.txt', 'words_sunstein.bak')
        open('words_sunstein.txt', 'w').write('\n'.join(sorted(SUNSTEIN_WORDS)))


def replace_no_add(raw_word, replace, text, idx, res):
    if raw_word == replace:
        print('Loop detected - aborting.')
        idx = rewind(idx, res)
        return idx, text
    if res:
        text = text[:max(idx-50, 0)] + text[max(idx-50, 0):idx+50+res.start()].replace(raw_word, replace) + text[idx+50+res.start():]
    else:
        text = text[:idx-50] + text[max(idx-50, 0):].replace(raw_word, replace)
    idx = rewind_more(idx, res, text)
    return idx, text


def replace_and_add(raw_word, replace, text, idx, res):
    if raw_word == replace:
        print('Loop detected - aborting.')
        idx = rewind(idx, res)
        return idx, text
    if not RE_WORD_SEP.search(replace):
        add_to_dict(replace)
    else:
        for word in RE_WORD_SEP.split(replace):
            add_to_dict(word.rstrip('.,:;?!"').lstrip('"'))
    SUNSTEIN_SUB[raw_word.lower()] = replace.lower()
    shutil.copy('words_sunstein_subst.txt', 'words_sunstein_subst.bak')
    open('words_sunstein_subst.txt', 'w').write('\n'.join(k + '\n' + v for k, v in sorted(SUNSTEIN_SUB.items())))
    idx, text = replace_no_add(raw_word, replace, text, idx, res)
    return idx, text


def add_to_case_dict(raw_word):
    SUNSTEIN_CASE_WORDS.add(raw_word)
    shutil.copy('words_sunstein_case.txt', 'words_sunstein_case.bak')
    open('words_sunstein_case.txt', 'w').write('\n'.join(sorted(SUNSTEIN_CASE_WORDS)))


def replace_and_add_case(raw_word, replace, text, idx, res):
    if raw_word == replace:
        print('Loop detected - aborting.')
        idx = rewind(idx, res)
        return idx, text
    if not RE_WORD_SEP.search(replace):
        add_to_case_dict(replace)
    else:
        for word in RE_WORD_SEP.split(replace):
            add_to_case_dict(word.rstrip('.'))
    SUNSTEIN_CASE_SUB[raw_word] = replace
    shutil.copy('words_sunstein_case_subst.txt', 'words_sunstein_case_subst.bak')
    open('words_sunstein_case_subst.txt', 'w').write('\n'.join(k + '\n' + v for k, v in sorted(SUNSTEIN_CASE_SUB.items())))
    idx, text = replace_no_add(raw_word, replace, text, idx, res)
    return idx, text


for i, text in enumerate(texts):
    final_filename = filenames[i].replace('mclean', 'final').replace('cermine', 'final')
    if os.path.exists(final_filename):
        continue
        # pass # TODO

    # Fancy punctuation
    auto_operations += text.count('“')
    auto_operations += text.count('”')
    auto_operations += text.count('`')
    auto_operations += text.count('–')
    auto_operations += text.count('[ed]')
    auto_operations += text.count('[ing]')
    text = text.replace('“', '"').replace('”', '"').replace('’', '\'').replace('‘', '\'').replace('`', '\'').replace('–', ' - ').replace('  ', ' ').replace('[ed]', 'ed').replace('[ing]', 'ing')
    
    # [A]ll -> All
    auto_operations += len(re.findall(RE_BRACKET, text))
    text = re.sub(RE_BRACKET, '\\1', text)
    
    # ......., . . . . . -> ...
    auto_operations += len(re.findall(RE_LONG_ELLIPSIS, text))
    text = re.sub(RE_LONG_ELLIPSIS, '...', text)
    
    # -- -> -
    auto_operations += len(re.findall(RE_DOUBLE_DASH, text))
    text = re.sub(RE_DOUBLE_DASH, '-', text)
    
    prev_idx = 0
    idx = 0
    print('='*100)
    print(f'File {i+1}/{len(filenames)}: {filenames[i]}')
    print('='*100)
    print()
    running = True
    pbar = tqdm(total=len(text))
    while idx < len(text) and running:
        res = RE_WORD_SEP.search(text[idx:])
        if res is None:
            curr_word = text[idx:]
            running = False
        else:
            curr_word = text[idx:idx+res.start()]
        if not curr_word:
            idx += res.end()
            continue
        
        # Processing
        raw_word = curr_word.strip(punctuation)
        case_check = True
        if raw_word \
                and (raw_word.lower() not in EN_WORDS | SUNSTEIN_WORDS | SUNSTEIN_SUB.keys()) \
                and not RE_DIGITS_REF.search(raw_word):
            ctx_before = text[max(idx-context_size, 0):idx].replace('\\n', '\\\\n')
            ctx_after = text[idx+len(curr_word):idx+len(curr_word)+context_size].replace('\\n', '\\\\n')
            ctx_word = f'[{curr_word}]'
            print('-'*212)
            print(f'{bcolors.WARNING}[{idx:>5}/{len(text)}]{bcolors.ENDC} ...{ctx_before:>85}{bcolors.FAIL}{ctx_word:^{inner_ctx}}{bcolors.ENDC}{ctx_after}...')
            print('-'*212)
            orig_split = wordninja.split(raw_word)
            split = ' '.join(orig_split)
            hyphen_split = ' - '.join(orig_split)
            spaced_out = raw_word.replace(',', ', ')
            spaced_out_l = spaced_out.replace('"', ' "')
            spaced_out_r = spaced_out.replace('"', '" ')
            spaced_out_l = spaced_out_l.replace(':', ': ').replace(';', '; ').replace(')', ') ').replace('(', ' (').replace('-', ' - ').replace('  ', ' ').replace(' ,', ',').replace(' ;', ';').strip(' ')
            spaced_out_r = spaced_out_r.replace(':', ': ').replace(';', '; ').replace(')', ') ').replace('(', ' (').replace('-', ' - ').replace('  ', ' ').replace(' ,', ',').replace(' ;', ';').strip(' ')
            if '...' in spaced_out_l:
                spaced_out_l = spaced_out_l.replace('...', '... ').replace('... ,', '...,')
                spaced_out_r = spaced_out_r.replace('...', '... ').replace('... ,', '...,')
            else:
                spaced_out_l = spaced_out_l.replace('.', '. ').replace('. ,', '.,')
                spaced_out_r = spaced_out_r.replace('.', '. ').replace('. ,', '.,')
            spaced_out_l = spaced_out_l.replace('  ', ' ')
            spaced_out_r = spaced_out_r.replace('  ', ' ')
            print(f'Unknown word: {bcolors.FAIL}[{raw_word}]{bcolors.ENDC}, possible split: {bcolors.OKGREEN}[{split}]{bcolors.ENDC}, spaced out: {bcolors.OKBLUE}[{spaced_out_l}]{bcolors.ENDC} / {bcolors.OKBLUE}[{spaced_out_r}]{bcolors.ENDC}')
            distances = sorted([(distance(word, raw_word.lower()), word) for word in EN_WORDS | SUNSTEIN_WORDS])
            
            str_replace = ''
            for replace_idx in range(10):
                str_replace += f'{bcolors.OKCYAN}[{replace_idx+1}]{bcolors.ENDC} {distances[replace_idx][1]}     '
            print(str_replace.strip())
            print(f'{bcolors.OKCYAN}[A]{bcolors.ENDC}dd     {bcolors.OKCYAN}[R]{bcolors.ENDC}eplace     {bcolors.OKGREEN}[S]{bcolors.ENDC}plit     {bcolors.OKCYAN}[H]{bcolors.ENDC}yphenize     {bcolors.OKCYAN}[C]{bcolors.ENDC}ontext     Merge {bcolors.OKCYAN}[L]{bcolors.ENDC}eft     {bcolors.OKCYAN}[M]{bcolors.ENDC}erge right     {bcolors.OKCYAN}[O]{bcolors.ENDC}ne-time     {bcolors.OKCYAN}[F]{bcolors.ENDC}ast replace     {bcolors.OKCYAN}[N]{bcolors.ENDC}umber removal     {bcolors.OKBLUE}[D]{bcolors.ENDC}etach words     D{bcolors.OKBLUE}[e]{bcolors.ENDC}tach right     Ne{bcolors.OKCYAN}[w]{bcolors.ENDC} rule     {bcolors.OKCYAN}[I]{bcolors.ENDC}gnore     Add h{bcolors.OKCYAN}[y]{bcolors.ENDC}phens')
            
            choice = ''
            while choice.lower() not in num_answers + ['a', 'c', 'd', 'e', 'f', 'h', 'i', 'l', 'm', 'n', 'o', 'r', 's', 'w', 'y']:
                choice = input('Choose action: ')
            
            choice = choice.lower()
            if choice == 'a':
                add_to_dict(raw_word.lower())
            elif choice == 'r':
                replace = input('Replacement value: ')
                idx, text = replace_and_add(raw_word, replace, text, idx, res)
                raw_word = replace
            elif choice == 's':
                idx, text = replace_and_add(raw_word, split, text, idx, res)
                raw_word = split
            elif choice == 'h':
                idx, text = replace_no_add(raw_word, ' - '.join(orig_split), text, idx, res)
                case_check = False
                idx = rewind_more(idx, res, text)
            elif choice == 'c':
                idx = rewind(idx, res)
                context_size += 80
                inner_ctx = 0
                manual_operations -= 1
                case_check = False
            elif choice in num_answers:
                choice = int(choice) - 1
                idx, text = replace_and_add(raw_word, distances[choice][1], text, idx, res)
                raw_word = distances[choice][1]
                case_check = False
            elif choice == 'l':
                if res is not None:
                    text = text[:idx-1] + text[idx:]
                    idx = rewind_more(idx, res, text)
                else:
                    print('EOF reached, skipping')
                case_check = False
            elif choice == 'm':
                if res is not None:
                    text = text[:idx+res.start()] + text[idx+res.end():]
                    idx = rewind(idx, res)
                else:
                    print('EOF reached, skipping')
                case_check = False
            elif choice == 'o':
                search = input('Search value: ')
                replace = input('Replacement value: ')
                idx, text = replace_no_add(search, replace, text, idx, res)
                raw_word = raw_word.replace(search, replace)
            elif choice == 'f':
                replace = input('Replacement value: ')
                if res:
                    text = text[:idx] + replace + res.group(0) + text[idx+res.start():]
                else:
                    text = text[:idx] + replace
                case_check = False
                idx = rewind_more(idx, res, text)
            elif choice == 'n':
                idx, text = replace_no_add(raw_word, ''.join(char for char in raw_word if not char.isnumeric()), text, idx, res)
                raw_word = ''.join(char for char in raw_word if not char.isnumeric())
            elif choice == 'd':
                idx, text = replace_and_add(raw_word, spaced_out_l, text, idx, res)
                raw_word = spaced_out_l
            elif choice == 'e':
                idx, text = replace_and_add(raw_word, spaced_out_r, text, idx, res)
                raw_word = spaced_out_r
            elif choice == 'w':
                search = input('Search value: ')
                replace = input('Replacement value: ')
                idx, text = replace_and_add(search, replace, text, idx, res)
                raw_word = raw_word.replace(search, replace)
            elif choice == 'i':
                case_check = False
            elif choice == 'y':
                idx, text = replace_and_add(raw_word, hyphen_split, text, idx, res)
                raw_word = hyphen_split
            if choice != 'c':
                context_size = 80
                inner_ctx = 25
            manual_operations += 1
        elif raw_word.lower() in SUNSTEIN_SUB.keys():
            idx, text = replace_no_add(raw_word, SUNSTEIN_SUB[raw_word.lower()], text, idx, res)
            raw_word = SUNSTEIN_SUB[raw_word.lower()]
        elif raw_word.lower() in SUNSTEIN_WORDS:
            pass
        
        if case_check:
            upper = sum(1 for c in raw_word if c.isupper())
            lower = sum(1 for c in raw_word if c.islower())
            if not RE_WORD_SEP.search(raw_word) and lower and (upper > 1 or upper == 1 and raw_word[0].islower()):
                if raw_word not in SUNSTEIN_CASE_WORDS | SUNSTEIN_CASE_SUB.keys():
                    ctx_before = text[max(idx-context_size, 0):idx].replace('\\n', '\\\\n')
                    ctx_after = text[idx+len(curr_word):idx+len(curr_word)+context_size].replace('\\n', '\\\\n')
                    ctx_word = f'[{curr_word}]'
                    print('-'*212)
                    print(f'{bcolors.WARNING}[{idx:>5}/{len(text)}]{bcolors.ENDC} ...{ctx_before:>85}{bcolors.FAIL}{ctx_word:^{inner_ctx}}{bcolors.ENDC}{ctx_after}...')
                    print('-'*212)
                    print(f'Inconsistent case: {bcolors.FAIL}[{raw_word}]{bcolors.ENDC}')
                    print(f'{bcolors.OKCYAN}[U]{bcolors.ENDC}pper          {bcolors.OKCYAN}[L]{bcolors.ENDC}ower          {bcolors.OKCYAN}[I]{bcolors.ENDC}gnore          {bcolors.OKCYAN}[S]{bcolors.ENDC}entence          {bcolors.OKCYAN}[C]{bcolors.ENDC}ustom          {bcolors.OKCYAN}[O]{bcolors.ENDC}ne-time')
                    
                    choice = ''
                    while choice.lower() not in num_answers + ['c', 'i', 'l', 'o', 's', 'u']:
                        choice = input('Choose action: ').lower()

                    if choice == 'l':
                        idx, text = replace_and_add_case(raw_word, raw_word.lower(), text, idx, res)
                    elif choice == 'u':
                        idx, text = replace_and_add_case(raw_word, raw_word.upper(), text, idx, res)
                    elif choice == 'i':
                        add_to_case_dict(raw_word)
                    elif choice == 'c':
                        replace = input('Replacement value: ')
                        idx, text = replace_and_add_case(raw_word, replace, text, idx, res)
                    elif choice == 's':
                        idx, text = replace_and_add_case(raw_word, raw_word.capitalize(), text, idx, res)
                    elif choice == 'o':
                        search = input('Search value: ')
                        replace = input('Replacement value: ')
                        idx, text = replace_no_add(search, replace, text, idx, res)
                    manual_operations += 1
                elif raw_word in SUNSTEIN_CASE_SUB:
                    auto_operations += 1
                    idx, text = replace_no_add(raw_word, SUNSTEIN_CASE_SUB[raw_word], text, idx, res)
                elif raw_word in SUNSTEIN_CASE_WORDS:
                    pass
        
        if res is not None:
            idx += res.end()
        
        pbar.update(idx - prev_idx)
        prev_idx = idx
    pbar.close()

    print('Automatic operations:', auto_operations + len_auto) # Not perfect, would need to remove and substract by len_auto but only for applied substitutions
    print('Manual operations:', len(SUNSTEIN_WORDS) + len(SUNSTEIN_SUB) + len(SUNSTEIN_CASE_SUB) + len(SUNSTEIN_CASE_WORDS))
    
    open(final_filename, 'w').write(text) # TODO