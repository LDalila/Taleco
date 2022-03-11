from bs4 import BeautifulSoup

from collections import Counter
import os

folder = 'sunstein/processed/'

for filename in os.listdir(folder):
    print(filename)
    if filename.endswith('_cermine.xml'):
        with open(folder + filename) as f:
            soup = BeautifulSoup(f.read(), 'xml')

        out_text = ''

        for p in soup.find_all('p'):
            for line in p.text.split('\n'):
                begin = line.split(' ')[0]
                if not begin:
                    continue
                if begin[-1] == '.' and begin[:-1].isnumeric():
                    continue
                out_text += line + ' '
            out_text += '\n'
        
        with open(folder + filename[:-4] + '.txt', 'w') as f:
            f.write(out_text)
    
    if filename.endswith('_lapdf.xml'):
        with open(folder + filename) as f:
            soup = BeautifulSoup(f.read(), 'xml')
            
        font_size = Counter(int(page['mostPopWordHeight']) for page in soup.find_all('page')).most_common()[0][0]
        
        out_text = ''
        
        for page in soup.find_all('page'):
            line_start = 1000
            for chunk in page.find_all('chunk'):
                if int(chunk['fontSize']) - font_size in [-1, 0, 1]:
                    words = [word for word in chunk.find('words').find_all('wd') if int(word['h']) - font_size in [-1, 0, 1]]
                    if len(words) < 3:
                        continue
                    chunk_text = words[0]['t'] + ' ' + words[1]['t']
                    for prev_word, word, next_word in zip(words, words[1:], words[2:]):
                        line_start = min(line_start, int(next_word['x']))
                        x1 = int(prev_word['x'])
                        x2 = int(word['x'])
                        x3 = int(next_word['x'])
                        y1 = int(prev_word['y'])
                        y2 = int(word['y'])
                        y3 = int(next_word['y'])
                        if abs(y3 - y2) > 5*max(1, abs(y2 - y1)) or abs(y2 - y1) >= font_size - 1 and abs(y3 - y2) >= font_size - 1: # Newline: third word is significantly relatively lower compared to the previous two, OR both the second and third are significantly relatively lower than the previous ones
                            if word['t'].endswith('-'): # Hyphenation
                                # print('Hyphenation?', word['t'], next_word['t'])
                                chunk_text = chunk_text[:-1] + next_word['t'] # TODO: Perform additional checks
                            elif x3 - line_start > 10:
                                # print('Paragraph?', next_word['t'], line_start, x3)
                                chunk_text += '\n' + next_word['t']
                            else:
                                chunk_text += ' ' + next_word['t']
                        else:
                            chunk_text += ' ' + next_word['t']
                    out_text += chunk_text + '\n'
        
        with open(folder + filename[:-4] + '.txt', 'w') as f:
            f.write(out_text)

    

