import data_reader
# TODO: What bout 666.666?
# TODO: Reordering: How to handle first and last phrases?
# TODO: Should we care about performance and/or memory usage?
# TODO: How to deal with translations that are not in the translation of reodering model?
# TODO: Report: Talk about divide-by-zero error
# TODO: Report: Discuss backoff and why it should be zero if history not in LM
# TODO: Convert to log probs
# TODO: How to deal with translations that are not in the phrase table

def calculate_language_probability(english_phrase, language_model):
  english_words = english_phrase.split(" ")

  # Base case
  if len(english_words) == 0:
    return 0

  # Return (log) probability if in language model
  if english_phrase in language_model:
    return language_model[english_phrase][0]

  # Else, recursively backoff to lower n-gram models
  # If the history is not in the language model, we use a backoff weight of 0
  else:
    history = " ".join(english_words[:-1])
    backoff_weight = language_model.get(history, default=[0,0])[1]

    lower_order_ngram = " ".join(english_words[1:])
    lower_order_ngram_prob = calculate_language_probability(lower_order_ngram, language_model)

    return backoff_weight + lower_order_ngram_prob

def calculate_translation_probability(german_phrase, english_phrase, translation_model):
  log_sum = 0

  if (german_phrase, english_phrase) in translation_model:
    for log_probabillity in translation_model[(german_phrase, english_phrase)]:
      log_sum += log_probabillity

  return log_sum

def calculate_reordering_probability(german_phrase, english_phrase, german_indexes, reordering_model):
  # german_indexes = [german_s_index, german_e_index, german_previous_s_index, german_previous_e_index, german_next_s_index, german_next_e_index]
  german_s_index, german_e_index = german_indexes[0], german_indexes[1]
  german_previous_s_index, german_previous_e_index = german_indexes[2], german_indexes[3]
  german_next_s_index, german_next_e_index = german_indexes[4], german_indexes[5]

  if not (german_phrase, english_phrase) in reordering_model:
    return 0

  log_sum = 0
  # Right-to-left
  if german_s_index - 1 == german_previous_e_index:
    log_sum += reordering_model[(german_phrase, english_phrase)][0] # Monotone

  elif german_e_index + 1 == german_previous_s_index:
    log_sum += reordering_model[(german_phrase, english_phrase)][1] # Swap

  else:
    log_sum += reordering_model[(german_phrase, english_phrase)][2] # Discont

  # Left-to-right
  if german_e_index + 1 == german_next_s_index:
    log_sum += reordering_model[(german_phrase, english_phrase)][4] # Monotone

  elif german_s_index - 1 == german_next_e_index:
    log_sum += reordering_model[(german_phrase, english_phrase)][5] # Swap

  else:
    log_sum += reordering_model[(german_phrase, english_phrase)][6] # Disct

  return log_sum

def main():
  trace_file = open('Data/testresults.trans.txt.trace', 'r')
  english_file = open('Data/file.test.en', 'r')
  german_file = open('Data/file.test.de', 'r')

  print("Reading models")
  language_model = data_reader.read_language_model()
  translation_model = data_reader.read_translation_model()
  reordering_model = data_reader.read_reordering_model()

  for i in range(1):
    trace_line = trace_file.readline()
    english_line = english_file.readline()
    german_line = german_file.readline()

    trace_phrases = trace_line.split(" ||| ")
    english_words = english_line.split(" ")
    german_words = german_line.split(" ")

    translation_cost = 0

    for trace_i, trace_phrase in enumerate(trace_phrases):
      # Get necessary values
      (german_indices, english_phrase) = trace_phrase.split(":")
      (german_previous_indices, previous_english_phrase) = trace_phrases[max(trace_i - 1, 0)].split(":")
      (german_next_indices, next_english_phrase) = trace_phrases[min(trace_i + 1, len(trace_phrases) - 1)].split(":")

      (german_s_index, german_e_index) = map(int, german_indices.split("-"))
      (german_previous_s_index, german_previous_e_index) = map(int, german_previous_indices.split("-"))
      (german_next_s_index, german_next_e_index) = map(int, german_next_indices.split("-"))

      german_indexes = [german_s_index, german_e_index, german_previous_s_index, german_previous_e_index, german_next_s_index, german_next_e_index]
      german_phrase = " ".join(german_words[german_s_index : german_e_index + 1])

      # Calculate probabilities
      phrase_probability = 0
      phrase_probability += calculate_language_probability(english_phrase, language_model)
      phrase_probability += calculate_translation_probability(german_phrase, english_phrase, translation_model)
      phrase_probability += calculate_reordering_probability(german_phrase, english_phrase, german_indexes, reordering_model)

      translation_cost += phrase_probability

    print("Translation cost: {}".format(translation_cost))


if __name__ == '__main__':
  main()
