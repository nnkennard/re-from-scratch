import collections
import json
import stanza
import tqdm

STANZA_PIPELINE = stanza.Pipeline('en',
                                  processors='tokenize,lemma,pos,constituency',
                                  tokenize_pretokenized=True,
                                  tokenize_no_ssplit=True)

with open('nltk_stopwords.json', 'r') as f:
  STOPWORDS = json.load(f)

def get_forum_and_reviews(filename):
  with open(filename, 'r') as f:
    obj = json.load(f)
    return obj['forums'], obj['reviews']

def get_lemma(stanza_word):
  d = stanza_word.to_dict()
  if 'lemma' in d:
    return d['lemma']
  else:
    print(d)
    return "_"

def get_sentence_lists(text):
  annotated = STANZA_PIPELINE(text)
  sentences = []
  for sentence in annotated.sentences:
    sentences.append([get_lemma(word) for word in sentence.words])
  return sentences

def basov_original(review_text):
  sentences = get_sentence_lists(review_text)
  edges = []
  for sentence in sentences:
    selected_words = [w for w in sentence if w not in STOPWORDS]
    edges += list(tuple(i)
      for i in zip(selected_words[:-1], selected_words[1:]))
  return collections.Counter(edges)

def basov_sentence(review_text):
  sentences = get_sentence_lists(review_text)
  edges = []
  for sentence in sentences:
    selected_words = [w for w in sentence if w not in STOPWORDS]
    for i, w1 in enumerate(selected_words):
      for w2 in selected_words[i+1:]:
        edges.append((w1, w2))
  return collections.Counter(edges)

def get_mention_map(np_list, tree):
  if tree.label == "NP":
    np_list.append(" ".join(tree.leaf_labels()))

def np_sentence(review_text):
  annotated = STANZA_PIPELINE(review_text)
  edges = []
  for sentence in annotated.sentences:
    np_list = []
    sentence.constituency.visit_preorder(internal=lambda x:get_mention_map(np_list, x))
    for i, np1 in enumerate(np_list):
      for np2 in np_list[i+1:]:
        edges.append((np1, np2))
  return collections.Counter(edges)

def main():
  forum_map, reviews = get_forum_and_reviews('iclr2019_reviews.json')
  for review_id, review_text in tqdm.tqdm(reviews.items()):
    b_edges = basov_original(review_text)
    b_sentence = basov_sentence(review_text)
    print("ORIGINAL")
    for k, v in b_edges.most_common():
      if v == 1:
        break
      print(k, v)
    print()
    print("SENTENCE")
    for k, v in b_sentence.most_common():
      if v == 1:
        break
      print(k, v)
    print()



if __name__ == "__main__":
  main()

