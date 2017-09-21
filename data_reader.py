import requests

english_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.en"
german_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.de"
word_alignment_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.aligned"

def _read_sentences(dataset):
  return dataset.splitlines()

def read_english_sentences():
  english_dataset = requests.get(english_dataset_url).text
  return _read_sentences(english_dataset)

def read_english_sentences_local():
  with open('data/file.en.txt', 'r') as f:
    english_dataset = f.read().splitlines()
    return english_dataset

def read_german_sentences():
  german_dataset = requests.get(german_dataset_url).text
  return _read_sentences(german_dataset)

def read_german_sentences_local():
  with open('data/file.de.txt', 'r') as f:
    german_dataset = f.read().splitlines()
    return german_dataset

def read_word_alignments():
  word_alignment_dataset = requests.get(word_alignment_dataset_url).text
  word_alignments = _read_sentences(word_alignment_dataset)
  return [[string_to_tupple(x) for x in alignment.split()] for alignment in word_alignments]

def read_word_alignments_local():
  with open('data/file.aligned.txt', 'r') as f:
    word_alignments = f.read().splitlines()
    return [[string_to_tupple(x) for x in alignment.split()] for alignment in word_alignments]

def string_to_tupple(s):
  numbers = s.split('-')
  return (int(numbers[1]), int(numbers[0]))
