
import sys, math
from collections import Counter
import cPickle

uniform_prob = "uniform"
empirical_prob = "empirical"

interp_weight = 0.2
edit_prob = 0.1
equal_prob = 0.9

queries_loc = 'data/queries.txt'
gold_loc = 'data/gold.txt'
google_loc = 'data/google.txt'

unigram_file = 'unigram'
bigram_file = 'bigram'
del_file = 'del'
ins_file = 'ins'
sub_file = 'sub'
trans_file = 'trans'
count_file = 'count'

unigram_counts = Counter()
bigram_counts = Counter()
del_dic = {}
ins_dic = {}
sub_dic = {}
trans_dic ={}
count_dic = {}
term_count = 0

alphabet = "abcdefghijklmnopqrstuvwxyz0123546789&$+_' "

def read_query_data():
  """
  all three files match with corresponding queries on each line
  """
  queries = []
  gold = []
  google = []
  with open(queries_loc) as f:
    for line in f:
      queries.append(line.rstrip())
  with open(gold_loc) as f:
    for line in f:
      gold.append(line.rstrip())
  with open(google_loc) as f:
    for line in f:
      google.append(line.rstrip())
  assert( len(queries) == len(gold) and len(gold) == len(google) )
  return (queries, gold, google)

def uni_cost_prob(r, q, dist):
  if q == r:
    return equal_prob
  else:
    return math.pow(uni_prob, dist)

def unigram_prob(string):
  return unigram_counts[string]/term_count

def bigram_prob(w1, w2):
  return bigram_counts[(w1, w2)]/unigram_counts[w1]

def interp_prob(w1, w2):
  if w1 is None:
    return unigram_prob(w2)
  else:
    return interp_weight*unigram_prob(w1) + (1 - interp_weight)*bigram_prob(w1, w2)

def query_prob(query):
  strings = query.split()
  prob = 0
  w1 = None
  for w2 in strings:
    prob += math.log(interp_prob(w1, w2))
    w1 = w2
  return prob

def read_models():
  """
  reads in unigram and bigram counts stored from buildmodels.sh
  reads in empircal edit cost dictionaries stored from buildmodels.sh
  """
  unigram = open(unigram_file, 'rb')
  bigram = open(bigram_file, 'rb')
  delete = open(del_file, 'rb')
  insert = open(ins_file, 'rb')
  subs = open(sub_file, 'rb')
  trans = open(trans_file, 'rb')
  count = open(count_file, 'rb')
  unigram_counts = cPickle.load(unigram)
  bigram_counts = cPickle.load(bigram)
  term_count = len(unigram_counts)
  del_dic = cPickle.load(delete)
  ins_dic = cPickle.load(insert)
  sub_dic = cPickle.load(subs)
  trans_dic = cPickle.load(trans)
  count_dic = cPickle.load(count)


alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(string):
   splits     = [(string[:i], string[i:]) for i in range(len(string) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)
   
def edits2(string):
    return set(e2 for e1 in edits1(string) for e2 in edits1(e1) )

def is_valid_query(query):
	words = query.split()
	for word in words
		if word not in unigram_counts
			return False
	return True

def uniform_query_prob(query,candidate_query):
	#TODO: differentiate between 1 and 2 edits
	query_prob = query_prob(candidate_query)
	if query == candidate_query
		return query_prob * equal_prob
	else
		return query_prob * edit_prob
	
def find_uniform_correction(query):
	candidate_queries = edits1(query) or edits2(query)
	#delete all queries containing invalid words
	candidate_queries = set(q for q in candidate_queries if is_valid_query(q))
	max_query = ""
	max_query_prob = 0
	for curr_query in candidate_queries
		curr_query_prob = uniform_query_prob(query, curr_query)
		if curr_query_prob > max_query_prob
			max_query = curr_query
			max_query_prob = curr_query_prob
	return max_query
	
def empirical_query_prob(query, candidate_query):
	query_prob = query_prob(candidate_query)
	(edit_type, edit_arg) = compute_edit_type(query, candidate_query)
	
	if edit_type = 'ins'
		return query_prob * (ins_dict(edit_arg)/count_dict(edit_arg))
	elif edit_type = 'sub'
		return query_prob * (sub_dict(edit_arg)/count_dict(edit_arg))
	elif edit_type = 'del'
		return query_prob * (del_dict(edit_arg)/count_dict(edit_arg))
	elif edit_type = 'trans'
		return query_prob * (trans_dict(edit_arg)/count_dict(edit_arg))
	else
		return 0
	
def find_empirical_correction(query):
	candidate_edit1_queries = edits1(query)
	candidate_edit2_queries = edits2(query)
	#TODO: Generate all queries 1 to 2 edits away, storing edits
	#TODO: Write function to return query probability given edits
	#TODO: Incorporate additional simple heuristics to trim candidate sizes
	

def main(argv):
  prob_type = argv[1]
  read_models() # retrieve the language models
  (queries, gold, google) = read_query_data()
  
  for query in queries
  	result = ''
  	if prob_type == uniform_prob
  		result = find_uniform_correction(query)
  	elif prob_type == empirical_prob
		result = find_empirical_correction(query)
	print >> sys.stdout, result
  
if __name__ == '__main__':
  print(sys.argv)
  main(sys.argv)
  
def compute_edit_type(incor, cor):
    edit_type = None
    edit_arg = None
    if len(incor) < len(cor):
      edit_type = 'del'
      edit_arg = find_del_arg(incor, cor)
    elif len(incor) > len(cor):
      edit_type = 'ins'
      edit_arg = find_ins_arg(incor, cor)
    else:
      (edit_type, edit_arg) = compute_sub_trans(incor, cor)
    return edit_type, edit_arg

def compute_sub_trans(incor, cor):
    edit_type = None
    edit_arg = None
    ind = find_discrep(incor, cor)
    if ind == len(incor) - 1:
      edit_type = 'sub'
      edit_arg = incor[ind]+cor[ind]
    elif incor[ind+1] == cor[ind+1]:
      edit_type = 'sub'
      edit_arg = incor[ind]+cor[ind]
    else:
      edit_type = 'trans'
      edit_arg = cor[ind:ind+2]
    return edit_type, edit_arg

def find_discrep(incor, cor):
    for i in range(0,min(len(incor), len(cor))):
      if incor[i] != cor[i]:
        return i
    return max(len(incor), len(cor)) - 1

def find_del_arg(incor, cor):
    ind = find_discrep(incor, cor) - 1
    if ind == -1:
      return '$' + cor[0]
    else:
      return cor[ind:ind+2]
   
def find_ins_arg(incor, cor):
    ind = find_discrep(incor, cor) - 1
    if ind == -1:
      return '$' + incor[0]
    else:
      return incor[ind:ind+2]	
