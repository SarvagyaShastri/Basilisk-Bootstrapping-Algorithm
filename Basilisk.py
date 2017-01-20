import sys
import re
from operator import itemgetter
import math


def read_seeds(fname):
    seeds = set()
    try:
        with open(fname) as doc:
            for line in doc:
                line = line.upper().strip()
                seeds.add(line)
    except Exception, e:
        raise e
    return seeds


def read_context(fname):
    context = []
    try:
        with open(fname) as doc:
            for line in doc:
                group_1 = re.match(r'(.*)\*(.*?)\:(.*)',
                                   line).group(1).upper().strip().split()
                group_2 = re.match(r'(.*)\*(.*)', line).group(2).strip()
                context.append([group_1[-1], group_2])
    except Exception, e:
        raise e
    return context


def find_key_value(seeds, context):
    key_value = {}
    for item in context:
        if item[1] in key_value:
            if item[0] in key_value[item[1]]:
                continue
            else:
                key_value[item[1]].append(item[0])
        else:
            key_value[item[1]] = [item[0]]
    return key_value


def calculate_scores(key_value, seeds):
    scores = []
    for key in key_value:
        count = 0
        for value in key_value[key]:
            if value in seeds:
                count += 1
        semfreq = count
        head_nouns = len(key_value[key])
        if head_nouns > 1:
            try:
                RLogF = (float(semfreq) / head_nouns) * math.log(head_nouns, 2)
            except Exception, e:
                raise e
        else:
            RLogF = 0
        scores.append([RLogF, key])
    return scores


def find_top_ten(scores):
    count = 0
    temp = 0
    temp2 = scores[9][0]
    top_scores = []
    for i in scores[10:]:
        temp = i[0]
        if temp == temp2:
            count += 1
        else:
            return [i for i in scores[:10 + count] if i[0] > 0]


def collect_head_noun(pattern_pool, key_value, seeds):
    all_heads = []
    for item in pattern_pool:
        if key_value[item[1]] in all_heads:
            continue
        else:
            all_heads.extend(key_value[item[1]])
    return list(set(all_heads) - seeds)


def find_word_freq(word, key_value, seeds):
    result = []
    for item in key_value:
        count = 0
        heads = key_value[item]
        if word in heads:
            for vals in heads:
                if vals in seeds:
                    count += 1
            result.append(count + 1)
    return result


def find_top_five(top_new_words):
    count = 0
    temp = 0
    temp2 = top_new_words[4][0]
    top_scores = []
    for i in top_new_words[5:]:
        temp = i[0]
        if temp == temp2:
            count += 1
        else:
            return [i for i in top_new_words[:5 + count]]


def main():
    try:
        fname_seed = sys.argv[1]
        seeds = read_seeds(fname_seed)
    except Exception:
    	try:
        	seeds = read_seeds("human-seeds.txt")
        except Exception:
        	print "human-seeds.txt not present is folder"
        	sys.exit()
    try:
        fname_context = sys.argv[2]
        context = read_context(fname_context)
    except Exception:
    	try:
        	context = read_context("contexts.txt")
        except Exception:
        	print "contexts.txt not present in folder"
        	sys.exit()
    key_value = find_key_value(seeds, context)
    seed_list = list(seeds)
    seed_list.sort()
    print "\nSEED WORDS: ",
    for i in seed_list:
        print i,
    print "\n"
    print "UNIQUE WORDS: %d" % len(key_value)
    for z in xrange(5):
        print "\nITERATION %d" % (z + 1)
        scores = calculate_scores(key_value, seeds)
        scores.sort(reverse=True)
        temp_pattern_pool = find_top_ten(scores)
        temp = sorted(temp_pattern_pool, key=itemgetter(1))
        pattern_pool = sorted(temp, key=itemgetter(0), reverse=True)
        print "\nPATTERN POOL"
        for i, item in enumerate(pattern_pool):
            print "%d. %s (%.3f)" % ((i + 1), item[1], item[0])
        new_head_nouns = collect_head_noun(pattern_pool, key_value, seeds)
        top_new_words = []
        for word in new_head_nouns:
            freq = find_word_freq(word, key_value, seeds)
            avgLog = 0
            for item in freq:
                avgLog = avgLog + math.log(item, 2)
            avgLog = float(avgLog) / len(freq)
            top_new_words.append([avgLog, word])
        temp = sorted(top_new_words, key=itemgetter(1))
        top_new_words = sorted(temp, key=itemgetter(0), reverse=True)
        new_words = find_top_five(top_new_words)
        print "\nNEW WORDS"
        for i in range(5):
            print "%s (%0.3f)" % (new_words[i][1], new_words[i][0])
        for i in xrange(5):
            seeds.add(top_new_words[i][1])

main()
