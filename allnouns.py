from nltk.corpus import wordnet as wn
from pprint import pprint
import random
import sys

object_root = None
all_nouns = []
all_verbs = []
all_adjectives = []
all_adverbs = []

"""to_ignore = (
    'abstraction.n.06',
    'addition.n.01',
    'audio.n.04',
    'bilocation.n.01',
    'curio.n.01',
    'growth.n.07',
    'ingredient.n.01',
    'making.n.03',
    'natural_process.n.01',
    'procedure.n.01',
    'there.n.01',
    'triviality.n.03',
    'whereabouts.n.01'
    )"""
to_ignore = ()

def load_words():
    global object_root
    global all_nouns
    global all_verbs
    global all_adjectives
    global all_adverbs
    object_root = wn.synset('physical_entity.n.01')
    all_nouns = list(wn.all_synsets(pos=wn.NOUN))
    all_verbs = list(wn.all_synsets(pos=wn.VERB))
    all_adjectives = list(wn.all_synsets(pos=wn.ADJ))
    all_adverbs = list(wn.all_synsets(pos=wn.ADV))

def word_from(synset):
    return synset.name().split('.')[0].replace('_', ' ')

def print_tree(root, depth=0):
    count = 0
    if root.name() not in to_ignore:
        for h in root.hyponyms():
            if h.hyponyms():
                count += print_tree(h, depth+1)
        print(('%02d' % depth) + ': ' + (' ' * depth) + (' %4d   ' % count) + root.name())
        count += 1
    return count

def main():
    load_words()
    print_tree(object_root)
    #for a in all_adjectives:
    #    print(word_from(a))

        
if __name__ == '__main__':
    main()
    
