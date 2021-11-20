import sys

sys.path.insert(0, '/path/to/application/app/folder')

from scipy import stats

FLOOD_COMPARE_CONST = 10


def compare_messages_to_flood_detect(bot, chat_id, messages, ids):
    all_words_array = []
    all_words = dict()
    flood_ids = set()
    for message in messages:
        for word in message.split():
            if all_words.get(word) is None:
                all_words[word] = 0
    for i in range(len(messages)):
        current_words_dict = all_words.copy()
        for word in messages[i].split():
            current_words_dict[word] += 1
        all_words_array.append(list(current_words_dict.values()))
    sum_ = 0
    try:
        print(len(all_words_array))
        if len(all_words_array[0]) == 1:
            result_ids = []
            for i in range(len(all_words_array)):
                result_ids.append(i)
            return True, result_ids
        for i in range(len(all_words_array)):
            for j in range(i + 1, len(all_words_array)):
                try:
                    val = stats.pearsonr(all_words_array[i], all_words_array[j])[0]
                    if val == 'nan':
                        sum_ = 1000
                    else:
                        sum_ += val
                    if val > 0.8:
                        flood_ids.add(i)
                        flood_ids.add(j)
                except Exception as e:
                    sum_ = 1000
            if sum_ > FLOOD_COMPARE_CONST:
                return True, list(flood_ids)
        return False, []
    except Exception as e:
        return False, []


def compare_message_to_flood_detect(bot, messages, current_message, percent=0.5):
    all_words_array = []
    all_words = dict()
    flood_ids = set()
    for message in messages:
        for word in message.split():
            if all_words.get(word) is None:
                all_words[word] = 0
    for word in current_message.split():
        if all_words.get(word) is None:
            all_words[word] = 0
    for message in messages:
        current_words_dict = all_words.copy()
        for word in message.split():
            current_words_dict[word] += 1
        all_words_array.append(list(current_words_dict.values()))
    current_words_dict = all_words.copy()
    for word in current_message.split():
        current_words_dict[word] += 1
    curr_message = list(current_words_dict.values())
    sum_ = 0
    try:
        if len(all_words_array[0]) == 1:
            result_ids = []
            for i in range(len(all_words_array)):
                result_ids.append(i)
            return True, result_ids
        for i in range(len(messages)):
            val = stats.pearsonr(all_words_array[i], curr_message)[0]
            if val == 'nan':
                sum_ = 1000
            else:
                sum_ += val
            if val > 0.8:
                flood_ids.add(i)
        if sum_ > FLOOD_COMPARE_CONST * percent:
            return True, list(flood_ids)
        return False, []
    except:
        return False, []
