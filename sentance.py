import functools
from nltk.corpus import wordnet as wn
from nltk.corpus.reader import wordnet as wnr
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

def isvowel(c):
    return c.lower() in 'aeiou'

def isconsonant(c):
    return not isvowel(c)

@functools.lru_cache
def all_nouns_for(word):
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
    all_nouns = all_nouns_for(object_root)
    all_verbs = list(wn.all_synsets(pos=wn.VERB))
    all_adjectives = list(wn.all_synsets(pos=wn.ADJ))
    all_adverbs = list(wn.all_synsets(pos=wn.ADV))

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

def conjugate_verb(verb, number):
    verb_string = word_from(verb)
    verb_parts = verb_string.split(' ')
    if random.random() < .3:
        ending = (verb_parts[0][-1] == 'e' and 'd') or 'ed'
        verb_parts[0] += ending
    elif number == 1:
        if verb_parts[0][-1] in 'hs':
            verb_parts[0] += 'e'
        verb_parts[0] += 's'
    return ' '.join(verb_parts)
    
def somebody():
    synset = random.choice(all_nouns_for(wn.synset('person.n.01')))
    noun = word_from(synset)
    article = random_article(noun)
    return (article[0] + ' ' + noun), article[1]

def something():
    noun_synset = random.choice(all_nouns_for(wn.synset('entity.n.01')))
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
    return word_from(verb) + 'ed'

def infinitive():
    verb = random.choice(all_verbs)
    return word_from(verb)

def adjnoun():
    if random.random() > 0.5:
        return word_from(random_adjective())
    else:
        return word_from(random_noun())
    
# Sentance forms

def nothing_clause(verb):
    pass

def something_verb(verb):
    subject, number = something()
    return subject + ' ' + conjugate_verb(verb, number)

def somebody_verb(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number)

def it_is_verbing(verb):
    return 'It is ' + conjugate_verb(verb, number) + 'ing'

def something_is_verbing_PP(verb):
    subject, number = something()
    return subject + ' is ' + conjugate_verb(verb, number) + 'ing ' + past_participle()

def something_verb_something_adjnoun(verb):
    subject, number = something()
    return subject + ' ' + verb().name + ' ' + something()[0] + ' ' + adjnoun()

def something_verb_adjnoun(verb):
    subject, number = something()
    return subject + ' ' + verb().name + ' ' + adjnoun()

def somebody_verb_adjective(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + random_adjective()

def somebody_verb_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + something()[0]

def somebody_verb_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0]

def something_verb_something(verb):
    subject, number = something()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + something()[0]

def something_verb_to_somebody(verb):
    subject, number = something()
    return subject + ' ' + conjugate_verb(verb, number) + ' to ' + something()[0]

def somebody_verb_on_somebody(verb):
    return subject + ' ' + conjugate_verb(verb, number) + ' on ' + something()[0]

def somebody_verb_somebody_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0] + ' ' + something()[0]

def somebody_verb_something_to_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + something()[0] + ' to ' + somebody()[0]  # locative

def somebody_verb_something_from_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + something()[0] + ' from ' + somebody()[0] # dative

def somebody_verb_somebody_with_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0] + ' with ' + something()[0] # instrumentive

def somebody_verb_somebody_of_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0] + ' of ' + something()[0]

def somebody_verb_something_on_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + something()[0] + ' on ' + somebody()[0]  # locative

def somebody_verb_somebody_PP(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0] + ' ' + past_participle()

def somebody_verb_something_PP(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + something()[0] + ' ' + past_participle()

def somebody_verb_PP(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + past_participle()

def somebodys_bodypart_verb(verb):
    subject, number = somebody()
    return subject + '\'s ' + bodypart() + ' ' + conjugate_verb(verb, number)

def somebody_verb_somebody_to_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0] + ' to ' + infinitive()

def somebody_verb_somebody_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0] + ' ' + infinitive()

def somebody_verb_that_clause(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' that ' + clause()

def somebody_verb_to_somebody(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' to ' + somebody()[0]

def somebody_verb_to_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' to ' + infinitive()

def somebody_verb_whether_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' whether ' + infinitive()

def somebody_verb_somebody_into_ving_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + somebody()[0] + \
        ' into ' + get_random_verb() + 'ing ' + something()[0]

def somebody_verb_something_with_something(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + something()[0] + ' with ' + something()[0]

def somebody_verb_infinitive(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + infinitive()

def somebody_verb_ving(verb):
    subject, number = somebody()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + get_random_verb() + 'ing'

def it_verb_that_clause(verb):
    return 'It ' + conjugate_verb(verb, 1) + ' that ' + clause()

def something_verb_infinitive(verb):
    subject, number = something()
    return subject + ' ' + conjugate_verb(verb, number) + ' ' + infinitive()

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
    
