import functools
from nltk.corpus import wordnet as wn
from nltk.corpus.reader import wordnet as wnr
from pprint import pprint
import random
import sys

import irregulars

object_root = None
all_nouns = []
all_verbs = []
all_adjectives = []
all_adverbs = []

verb_lemmas_by_frame_id = {}

IGNORE_NOUNS = (
    'addition.n.01',
    'curio.n.01',
    'floater.n.07',
    'growth.n.07',
    'keepsake.n.01',
    'location.n.01',
    'natural_process.n.01',
    'procedure.n.01',
    'process.n.04',
    'psychoanalytic_process.n.01',
    'region.n.03',
    'shiner.n.02',
    'space.n.02'
    'triviality.n.03',
    )

def is_vowel(c):
    return c.lower() in 'aeiou'

def is_consonant(c):
    return not is_vowel(c)

def is_alterable_vowel_ending(word):
    if word[-1] in 'xw':
        return False
    if len(word) > 1 and is_consonant(word[-1]):
        if is_vowel(word[-2]):
            if len(word) > 2 and is_vowel(word[-3]):
                return False
            return True
    return False
    
@functools.lru_cache
def all_nouns_for(word, to_ignore=()):
    def walk_tree(tree):
            tree_result = [tree]
            for t in tree.hyponyms():
                if t.name() not in to_ignore:
                    tree_result += walk_tree(t)
            return tree_result
    return walk_tree(word)

def load_words():
    global object_root
    global all_nouns
    global all_verbs
    global all_adjectives
    global all_adverbs
    object_root = wn.synset('object.n.01')
    all_nouns = all_nouns_for(object_root, IGNORE_NOUNS)
    all_verbs = list(wn.all_synsets(pos=wn.VERB))
    all_adjectives = list(wn.all_synsets(pos=wn.ADJ))
    all_adverbs = list(wn.all_synsets(pos=wn.ADV))
    for verb in all_verbs:
        for lemma in verb.lemmas():
            for frame_id in lemma.frame_ids():
                if frame_id not in verb_lemmas_by_frame_id:
                    verb_lemmas_by_frame_id[frame_id] = {}
                verb_lemmas_by_frame_id[frame_id] = lemma

def word_from(synset):
    return synset.name().split('.')[0].replace('_', ' ')

def get_random_noun():
    return random.choice(all_nouns)
    
def get_random_verb():
    return random.choice(all_verbs)

def get_random_adjective():
    return random.choice(all_adjectives)

def get_random_adverb():
    return random.choice(all_adverbs)

def random_article(noun):
    if random.random() > 0.5:
        initial_vowel = noun[0] in 'aeiou'
        article = (initial_vowel and 'an') or 'a'
    else:
        article = 'the'
    return article, 1

def conjugate_past_present(verb, number=1, past=None):
    verb_string = word_from(verb)
    verb_parts = verb_string.split(' ')
    verb_root = verb_parts[0]
    if past or random.random() < .3:
        if verb_root in irregulars.VERBS:
            if past is not None:
                verb_root = irregulars.VERBS[verb_root][past]
            else:
                verb_root = irregulars.VERBS[verb_root][irregulars.PAST]
        else:
            if is_alterable_vowel_ending(verb_root):
                verb_parts[0] += verb_root[-1]
            ending = (verb_root[-1] == 'e' and 'd') or 'ed'
            verb_parts[0] += ending
    elif number == 1:
        if verb_parts[0][-1] in 'hs':
            verb_parts[0] += 'e'
        verb_parts[0] += 's'
    return ' '.join(verb_parts)

def conjugate_present_participle(verb):
    verb_string = word_from(verb)
    verb_parts = verb_string.split(' ')
    verb_root = verb_parts[0]
    if verb_root in irregulars.VERBS:
        verb_parts[0] = irregulars.VERBS[verb_root][irregulars.PRESENT_PART]
    else:
        verb_parts[0] += 'ing'
    return ' '.join(verb_parts)

def somebody():
    synset = random.choice(all_nouns_for(wn.synset('person.n.01'), IGNORE_NOUNS))
    noun = word_from(synset)
    article = random_article(noun)
    return (article[0] + ' ' + noun), article[1]

def something():
    noun_synset = random.choice(all_nouns_for(wn.synset('entity.n.01'), IGNORE_NOUNS))
    noun = word_from(noun_synset)
    result = ''
    if random.random() > 0.2:
        adj_synset = get_random_adjective()
        article, number = random_article(word_from(adj_synset))
        result += article + ' ' + word_from(adj_synset)
    else:
        article, number = random_article(noun)
        result += article
    result += ' ' + noun
    return result, number

def bodypart():
    synset = random.choice(all_nouns_for(wn.synset('body_part.n.01')))
    return word_from(synset)
    
def past_participle():
    verb = random.choice(all_verbs)
    return conjugate_past_present(verb, 1, irregulars.PAST_PART)

def infinitive():
    verb = random.choice(all_verbs)
    return word_from(verb)

def adjnoun():
    if random.random() > 0.5:
        return word_from(get_random_adjective())
    else:
        return word_from(random_noun())
    
# Sentance forms

def nothing_clause(verb):
    pass

def something_verb(verb):
    subject, number = something()
    return subject + ' ' + conjugate_past_present(verb, number)

def somebody_verb(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number)

def it_is_verbing(verb):
    return 'It is ' + conjugate_present_participle(verb)

def something_is_verbing_PP(verb):
    subject, number = something()
    return subject + ' is ' + conjugate_present_participle(verb) + ' ' + past_participle()

def something_verb_something_adjnoun(verb):
    subject, number = something()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0] + ' ' + adjnoun()

def something_verb_adjnoun(verb):
    subject, number = something()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + adjnoun()

def somebody_verb_adjective(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + \
        word_from(get_random_adjective())

def somebody_verb_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0]

def somebody_verb_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0]

def something_verb_something(verb):
    subject, number = something()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0]

def something_verb_to_somebody(verb):
    subject, number = something()
    return subject + ' ' + conjugate_past_present(verb, number) + ' to ' + something()[0]

def somebody_verb_on_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' on ' + something()[0]

def somebody_verb_somebody_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0] + ' ' + something()[0]

def somebody_verb_something_to_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0] + ' to ' + somebody()[0]  # locative

def somebody_verb_something_from_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0] + ' from ' + somebody()[0] # dative

def somebody_verb_somebody_with_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0] + ' with ' + something()[0] # instrumentive

def somebody_verb_somebody_of_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0] + ' of ' + \
        something()[0]

def somebody_verb_something_on_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0] + ' on ' + \
        somebody()[0]  # locative

def somebody_verb_somebody_PP(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0] + ' ' + \
        past_participle()

def somebody_verb_something_PP(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0] + ' ' + \
        past_participle()

def somebody_verb_PP(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + past_participle()

def somebodys_bodypart_verb(verb):
    subject, number = somebody()
    return subject + '\'s ' + bodypart() + ' ' + conjugate_past_present(verb, number)

def somebody_verb_somebody_to_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0] + ' to ' + \
        infinitive()

def somebody_verb_somebody_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0] + ' ' + \
        infinitive()

def somebody_verb_that_clause(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' that ' + clause()

def somebody_verb_to_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' to ' + somebody()[0]

def somebody_verb_to_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' to ' + infinitive()

def somebody_verb_whether_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' whether ' + infinitive()

def somebody_verb_somebody_into_ving_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + somebody()[0] + \
        ' into ' + conjugate_present_participle(get_random_verb()) + something()[0]

def somebody_verb_something_with_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + something()[0] + ' with ' + \
        something()[0]

def somebody_verb_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + infinitive()

def somebody_verb_ving(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + \
        conjugate_present_participle(get_random_verb())

def it_verb_that_clause(verb):
    return 'It ' + conjugate_past_present(verb, 1) + ' that ' + clause()

def something_verb_infinitive(verb):
    subject, number = something()
    return subject + ' ' + conjugate_past_present(verb, number) + ' ' + infinitive()

CLAUSE_HANDLERS = [
    nothing_clause,
    something_verb, somebody_verb,
    it_is_verbing, something_is_verbing_PP,
    something_verb_something_adjnoun, something_verb_adjnoun,
    somebody_verb_adjective, somebody_verb_something,
    somebody_verb_somebody, something_verb_something,
    something_verb_something, something_verb_to_somebody,
    somebody_verb_on_somebody, somebody_verb_somebody_something,
    somebody_verb_something_to_somebody, somebody_verb_something_from_somebody,
    somebody_verb_somebody_with_something, somebody_verb_somebody_of_something,
    somebody_verb_something_on_somebody, somebody_verb_somebody_PP,
    somebody_verb_something_PP, somebody_verb_PP,
    somebodys_bodypart_verb, somebody_verb_somebody_to_infinitive,
    somebody_verb_somebody_infinitive, somebody_verb_that_clause,
    somebody_verb_to_somebody, somebody_verb_to_infinitive,
    somebody_verb_whether_infinitive,
    somebody_verb_somebody_into_ving_something, somebody_verb_something_with_something,
    somebody_verb_infinitive, somebody_verb_ving,
    it_verb_that_clause, something_verb_infinitive
    ]

def clause():
    verb = get_random_verb()
    verb_lemma = random.choice(verb.lemmas())
    frame_id = random.choice(verb_lemma.frame_ids())
    frame_string = wnr.VERB_FRAME_STRINGS[frame_id]
    #print('     ' + frame_string)
    return CLAUSE_HANDLERS[frame_id](verb)

def sentance():
    return clause().capitalize() + '.'

def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 10
    load_words()
    for i in range(n):
        print(sentance())

if __name__ == '__main__':
    main()
    
