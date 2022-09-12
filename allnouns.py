from nltk.corpus import wordnet as wn
from pprint import pprint
import random
import sys

object_root = None
all_nouns = []
all_verbs = []
all_adjectives = []
all_adverbs = []

to_ignore = [
    'curio.n.01',
    'keepsake.n.01',
    'shiner.n.02',
    'triviality.n.03',
    'floater.n.07',
    'growth.n.07',
    'location.n.01',
    'region.n.03',
    'addition.n.01',
    'space.n.02'
    ]

def load_words():
    global object_root
    global all_nouns
    global all_verbs
    global all_adjectives
    global all_adverbs
    object_root = wn.synset('object.n.01')
    all_nouns = list(wn.all_synsets(pos=wn.NOUN))
    all_verbs = list(wn.all_synsets(pos=wn.VERB))
    all_adjectives = list(wn.all_synsets(pos=wn.ADJ))
    all_adverbs = list(wn.all_synsets(pos=wn.ADV))

def word_from(synset):
    return synset.name().split('.')[0].replace('_', ' ')

def print_tree(root, depth=0):
    if root.name() not in to_ignore:
        print(('%02d' % depth) + ': ' + (' ' * depth) + root.name())
        for h in root.hyponyms():
            if h.hyponyms():
                print_tree(h, depth+1)
    
def main():
    load_words()
    print_tree(object_root)

if __name__ == '__main__':
    main()
    
