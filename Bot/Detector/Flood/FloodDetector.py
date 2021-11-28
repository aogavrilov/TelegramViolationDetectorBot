import array
import collections

import numpy as np
from scipy.stats import stats


class FloodDetector:
    def __init__(self, FLOOD_COMPARE_CONST: int = 10):
        """
        Class for flood detection in messages

        :param FLOOD_COMPARE_CONST:
            Limit sum of correlation(similarity) between messages after which methods indicates that messages have flood.

        Methods:
        --------
        compare_messages_to_flood_detect(self, messages: array, similarity_coefficient: float = 1) -> (bool, list):
            Check messages in array for flood and returns flag == flood detected , indexes where messages is flood

        compare_message_to_flood_detect(self, messages: array, current_message: str, similarity_coefficient: float =
        0.5) -> (bool, list):
            Check message to similarity with other messages in array, return flag == flood \
            detected, indexes where messages is flood
        """

        self.FLOOD_COMPARE_CONST = FLOOD_COMPARE_CONST

    @staticmethod
    def _messages2words_counts(messages: array) -> (bool, array):
        """Build vocabulary, calculate word counts in messages and return indicator that vocabulary has only one word
        and words count """
        messages_concatenated = ' '.join(messages)
        word2id = {word: i for i, word in enumerate(set(messages_concatenated.split()))}
        words_count_in_messages = []
        is_one_word_in_vocabulary = len(word2id) == 1
        for message in messages:
            words_count_in_message = np.zeros(len(word2id))
            for word in message.split():
                words_count_in_message[word2id[word]] += 1
            words_count_in_messages.append(words_count_in_message)
        return is_one_word_in_vocabulary, words_count_in_messages

    def compare_messages_to_flood_detect(self, messages: array, similarity_coefficient: float = 1) -> (bool, list):
        """
        Check last messages to similarity and detect flood

        :param messages: array of str
            Last messages in chat with which pinged message is compared.

        :param similarity_coefficient: float, optional
            Coefficient by which is multiplied with FLOOD_COMPARE_CONST. Can be useful to correct limit sum of messages
            similarity based on count of messages and chat activity.
        :return: (bool, list)
            Return indicator is messages have flood messages and list of flood messages
        """

        flood_message_ids = set()
        messages_similarity = 0
        is_one_word_in_dictionary, words_count_in_messages = self._messages2words_counts(messages)
        if is_one_word_in_dictionary:
            result_ids = []
            for i in range(len(words_count_in_messages)):
                result_ids.append(i)
            return True, result_ids
        for i in range(len(messages)):
            for j in range(i + 1, len(messages)):
                correlation_between_messages = stats.pearsonr(words_count_in_messages[i], words_count_in_messages[0])[0]
                if correlation_between_messages == np.nan:
                    messages_similarity += 1
                else:
                    messages_similarity += correlation_between_messages
                if messages_similarity > 0.8:
                    flood_message_ids.add(i)
                    flood_message_ids.add(j)
            if messages_similarity > self.FLOOD_COMPARE_CONST * similarity_coefficient:
                return True, list(flood_message_ids)
        return False, []

    def compare_message_to_flood_detect(self,
                                        messages: array,
                                        current_message: str,
                                        similarity_coefficient: float = 0.5) -> (bool, list):
        """
        Check added by user message with other messages to similarity and detect flood

        :param messages: array of str
            Last messages in chat with which pinged message is compared.
        :param current_message: str
            Pinged by user message
        :param similarity_coefficient: float, optional
            Coefficient by which is multiplied with FLOOD_COMPARE_CONST. Can be useful to correct limit sum of messages
            similarity based on count of messages and chat activity.
        :return: (bool, list)
            Return indicator is messages have flood messages and list of flood messages
        """

        flood_message_ids = set()
        messages.insert(0, current_message)
        is_one_word_in_dictionary, words_count_in_messages = self._messages2words_counts(messages)

        messages_similarity = 0
        if is_one_word_in_dictionary:
            result_ids = []
            for i in range(len(words_count_in_messages)):
                result_ids.append(i)
            return True, result_ids

        for i in range(1, len(messages)):
            correlation_between_messages = stats.pearsonr(words_count_in_messages[i], words_count_in_messages[0])[0]
            if correlation_between_messages == np.nan:
                messages_similarity += 1
            else:
                messages_similarity += correlation_between_messages
            if correlation_between_messages > 0.8:
                flood_message_ids.add(i)
        if messages_similarity > self.FLOOD_COMPARE_CONST * similarity_coefficient:
            return True, list(flood_message_ids)
        return False, []
