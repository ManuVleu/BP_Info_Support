import markdown
from bs4 import BeautifulSoup
import random
import re

class Chapter:
    def __init__(self, name, dir, parent=None):
        self.name = name
        self.dir = dir
        self.files = []
        self.children = []
        self.parent = parent

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self

    def get_file_by_name(self, file_name):
        for file in self.files:
            if file.name == file_name:
                return file
        return None
    
    def get_random_chapter(self):
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_chapters())
        return random.choice(nodes)

    def get_all_chapters(self):
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_chapters())
        return nodes
        
    def get_random_file(self):
        if self.files:
            return random.choice(self.files)
        else:
            return None

    def print_tree(self, level=0):
        print("  " * level + "- " + str(self.name))
        for child in self.children:
            child.print_tree(level + 1)


class File:
    def __init__(self,name,dir):
        self.name = name
        self.dir = dir
        self.text = self.get_structured_text()# Dictionary of chapters in file where each chapter has a list of sentences so they aren't longer than max_input_length(model can only take so much tokens).

    def get_structured_text(self):
        with open(self.dir, 'r') as f:
            tempMd = f.read()

        html_text = markdown.markdown(tempMd)

        return get_text_per_h_elems(html_text)
    

def clean_markdown_text(text):
    cleaned_text = text.replace('*','').replace('\n',' ')
    return cleaned_text

def get_text_per_h_elems(html_text,min_length=10):
    soup = BeautifulSoup(html_text, 'html.parser')
    blacklist = ["script","ul","ol","li"]
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    text_list = {}
    for header in headers:
        text = ''
        sibling = header.find_next_sibling()
        while sibling and sibling.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if not sibling.name in blacklist:
                text += sibling.get_text(strip=True)
            sibling = sibling.find_next_sibling()
        if text:
            text = clean_markdown_text(text)
            if not len(text) < min_length:
                text_list[header.text.strip()] = split_string_into_items(text)

    return text_list

def split_into_sentences(text):
    sentences = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    return sentences

def split_string_into_items(text, max_length=512):
    sentences = split_into_sentences(text)
    items = []
    current_item = ""
    for sentence in sentences:
        if len(current_item) + len(sentence) + 1 <= max_length:
            current_item += " " + sentence
        else:
            items.append(current_item.strip())
            current_item = sentence
    if current_item:
        items.append(current_item.strip())
    return items