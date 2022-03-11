import json
import requests
from bs4 import BeautifulSoup

site_url = "https://www.becker-posner-blog.com/page/"
last_page = 109
# Our JSON output file
out_file = 'becker-posner.json'
post_count = 0
post_list = []

# All the very short posts that we can ignore if they have no author
IGNORED_POSTS = ['notice', 'notice-1', 'correction', 'announcement', 'rearranging', 'tsunami', 'this-weeks-postings', 'acquisition-of-us-port-operations-tomorro']

# Possible title formats that can be found in the text and can help us identify the author
TITLES = [
    '-Becker ', '- Becker ', '-Becker. ', '- Becker. ', '-Becker\n', '- Becker\n', '-Becker.\n', '- Becker.\n',
    '--Posner\'s Comment', '--Posner\'s Response to Comments'
]

# The remaining posts that we know are from Posner
POSNER_POSTS = [
    '2009/08/it.html',
    '2005/06/refusing-to-retire-what-can-be-done-when-people-overstay-their-welcome.html'
    '2005/04/the-sexual-revolution.html',
    '2005/03/judicial-term-limits.html',
    '2005/02/the-summers-controversy-and-university-governance.html',
    '2005/01/the-tsunami-and-the-economics-of-catastrophic-risk.html',
    '2004/12/global-warming.html',
]


for i in range(1, last_page + 1):
    # We get the main blog pages with all the articles
    url = site_url + str(i)
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    for post in soup.findAll(class_='entry-type-post'):
        # We retrieve the page for one specific article
        post_url = post.find(class_='entry-header').find('a')['href']
        post_req = requests.get(post_url)
        post_soup = BeautifulSoup(post_req.content, 'html.parser')

        post_dict = {}

        date = post_soup.find(class_='date-header')
        post_dict['date'] = date.text

        text = post_soup.find(class_='entry-body')
        post_dict['text'] = text.text.strip()

        title = post_soup.find(class_='entry-header')
        post_dict['title'] = title.text

        post_dict['url'] = post_url

        # We look for the author name in the title
        post = post_soup.find(class_='entry-type-post')
        if 'posner' in title.text.lower():
            post_dict['author'] = 'Posner'
        elif 'becker' in title.text.lower():
            post_dict['author'] = 'Becker'

        # We look for the author name in the CSS class
        elif 'entry-author-richard_posner' in post['class']:
            post_dict['author'] = 'Posner'
        elif 'entry-author-gary_becker' in post['class']:
            post_dict['author'] = 'Becker'

        # We ignore short posts with no author
        elif any(post_url.endswith(x + '.html') for x in IGNORED_POSTS):
            post_dict['author'] = 'Unknown'

        # We check if the title isn't included in the text
        else:
            author_found = False
            lower_text = text.text.lower()
            # We check if the text contains something that looks like a title
            for x in TITLES:
                # For each possible title, first determine who'd be the author
                if 'Posner' in title:
                    author = 'Posner'
                    other = 'becker'
                else:
                    author = 'Becker'
                    other = 'posner'

                # Then try to see if the text contains this title
                if x.lower() in lower_text:
                    index = lower_text.index(x.lower())
                    # Then check that it's near the beginning (before any mention of the other author)
                    if other not in lower_text or lower_text.index(other) > index:
                        l = len(x)
                        # We override the author, title and text
                        post_dict['author'] = author
                        post_dict['title'] = text.text[:index + l - 1].strip()
                        post_dict['text'] = text.text[index + l:].strip()
                        author_found = True
                        break

            # We check the remaining manually annotated posts
            if not author_found and any(x in post_url for x in POSNER_POSTS):
                post_dict['author'] = 'Posner'
                author_found = True

            if not author_found:
                print('No Author at ' + post_url)
                post_dict['author'] = 'Unknown'

        time = post_soup.find(class_='post-footers')
        post_dict['time'] = time.text[10:-1]

        post_dict['comments'] = []

        comment_post_url = post_url[:-5] + '/comments/page/'
        comment_page = 1
        comment_soup = post_soup

        # The comments are spread on multiple pages
        while True:
            # We get all the comment on one page
            for comment in comment_soup.find(class_='comments-content').findChildren('div', recursive=False):
                comment_dict = {}

                comment_text = comment.find(class_='comment-content')
                comment_dict['text'] = comment_text.text.strip()

                comment_footer = comment.find(class_='comment-footer')
                comment_dict['author'] = '|'.join(comment_footer.text.split('|')[:-1])[16:-1]

                date = comment_footer.findAll('a')[-1]
                comment_dict['date'] = date.text

                post_dict['comments'].append(comment_dict)

            # If there is no next page button, we stop
            if not comment_soup.findAll(class_='pager-right'):
                break

            # Otherwise we go to the next page
            comment_page += 1
            comment_url = comment_post_url + str(comment_page)
            comment_req = requests.get(comment_url)
            comment_soup = BeautifulSoup(comment_req.content, 'html.parser')
            print('-> Comment page ' + str(comment_page))

        post_list.append(post_dict)

        post_count += 1
        print('Article ' + str(post_count))

with open(out_file, 'w') as f:
    json.dump(post_list, f)
