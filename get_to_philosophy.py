import requests as reqs
from bs4 import BeautifulSoup
import json
import itertools
import bisect
import re
from time import sleep


def get_parenthesized_ranges(start, end , text):
    indicies = []
    for match_element in [start, end]:
        offset = 0
        while offset < len(text):
            indx = text.find(match_element, offset)
            if(indx == -1):
                break
            offset = indx+1
            indicies.append(indx)
    start_indices, end_indicies = indicies[:len(indicies)//2],indicies[len(indicies)//2:]
    
    rnges = []
    for index in start_indices[::-1]:
        try:
            matchi = bisect.bisect_left(end_indicies, index)
            rnges.append((index, end_indicies[matchi]))
            del end_indicies[matchi]
        except:
            pass
        
    
    rnges.sort()
    rnges = [rng for i,rng in enumerate(rnges) if i==0 or rng[0] > rnges[i-1][1]]
    return rnges


visited = {}  
def crawl(curr_url):
    sleep(.5)  
    print(curr_url)
    if(visited.get(curr_url,False)):
        print("Loop DETECTED !!! BACKTRACKINGGG ")
        return False  
    page = reqs.get(curr_url)
    curr_url = page.url

    visited[curr_url] = True
    base_url = page.url.split('/wiki/')[0]
    page_title = page.url.split('/')[-1]

    
    if(page_title == "Philosophy"):
        return True
        
    html_body = BeautifulSoup(page.text, 'html.parser').find('body')
    wiki_body = html_body.find(id='mw-content-text')

    if(not wiki_body):
        print("No html element with id mw-content-text")

    body_paragraphs = wiki_body.contents[0].find_all('p')
    body_paragraphs = list(filter(lambda p : ''.join(p.text.split()) != '', body_paragraphs))
    body_paragraphs_text = ''.join(list(map(str,body_paragraphs)))
    
    parenthesized_ranges = get_parenthesized_ranges('(',')',body_paragraphs_text)
    
    def is_parenthesized_link(anchor):
        for rng in parenthesized_ranges:
            if(anchor in body_paragraphs_text[rng[0]: rng[1]+1]):
                return True
        return False    
    
    def is_self_loop(link):
        dest_page_title = link.split('/')[-1]
        return page_title == dest_page_title

    def is_wiki_link(link):
        return not (re.match("/wiki/.+",link) is None)
    
    links = list(itertools.chain(*(p.find_all('a',href= True) for p in body_paragraphs )))
    
    for link in links:
        if(is_wiki_link(link['href']) and not is_self_loop(link['href']) and not is_parenthesized_link(str(link))):
            if(crawl(base_url + link['href'])):
                return True
               
    return False
   

if __name__ == "__main__":
    inp_url = input('Please enter wkik page url: ')
    # simple url assertion
    if(not re.match("http(s)?://[a-zA-Z]{1,3}\.wikipedia\.org/(/)?wiki/.+", inp_url)):
        raise Exception("Not valid wiki page url")    

    crawl(inp_url)