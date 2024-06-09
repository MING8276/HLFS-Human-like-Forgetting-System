import utils.tools as tools
import utils.api as api
import time
import math
from utils.log import Logs
import core.forget.curve as curve
import prompts.prompts as prompts
from config.config import config_curve, short_term_space, language, top_p_for_personality, top_p_for_summary
from utils.log import dialog_logger, summary_logger, topic_logger, personality_logger, prefetch_logger

tokenizer = api.get_tokenizer_func()


class User:
    def __init__(self, name: str):
        self.name = name
        # self.topic_list = []  # obj_list
        self.topic_name_list = []

    # def ret_topic_id(self, topic_name):
    #     return self.topic_name_list.index(topic_name)

    # def ret_topic(self, topic_name: str):
    #     assert topic_name is not None
    #     for t in self.topic_list:
    #         if t.name == topic_name:
    #             return t
    #     topic_logger.critical(f'Topic {topic_name} not found')
    #     raise ValueError(f'Topic {topic_name} not found')


class Topic:
    def __init__(self, user: User, name: str = None, new: bool = True):
        self.personality = ''
        self.personality_length = 0
        self.summary_list = []  # restore summary obj
        self.dialog_dict = {}  # {"dialog_id": {Q: , R: }, ..., }
        self.forever_dialogs = []  # restore index
        self.chosen_for_personality = []  # restore dialog ids which are chosen for personality
        if new:
            self.cur_dialog_id = 0
            self.topic_id = len(user.topic_name_list)
            if name:
                user.topic_name_list.append(name)
                self.name = name
            else:
                self.name = None
        else:
            self.cur_dialog_id = -1
            self.topic_id = -1
            if name:
                self.name = name
            else:
                raise ValueError('Please enter a valid topic name if the topic is old')

    def rename_topic(self, user: User, topic_name: str):
        if self.name is not None:
            raise ValueError(f'Topic {topic_name} already exists')
        if not topic_name:
            raise ValueError(f'Topic {topic_name} not found')
        user.topic_name_list.append(topic_name)
        self.name = topic_name

    def get_dialog(self, dialog_id: int):
        dialog = self.dialog_dict.get(dialog_id)
        if dialog is None:
            dialog_logger.critical(f'Dialog {dialog_id} not found in topic {self.name}')
            raise ValueError(f'Dialog {dialog_id} not found in topic {self.name}')
        return dialog

    # dialogs_id is a dialog_id list, [dialog_id_1, dialog_id_2, dialog_id_3, ..., dialog_id_n]
    def get_dialogs(self, dialogs_id: list) -> list:
        dialogs = [self.dialog_dict.get(key) for key in dialogs_id]
        if None in dialogs:
            dialog_logger.critical(f'Dialogs {dialogs} not found in topic {self.name}')
            raise ValueError(f'Dialogs {dialogs} not found in topic {self.name}')
        return dialogs  # [obj1, obj2, ..., obj_n]

    def get_summary(self, summary_id: int):
        try:
            summary = self.summary_list[summary_id]
            return summary
        except IndexError:
            summary_logger.critical(f'Summary {summary_id} not found in topic {self.name}')
            raise IndexError(f'Summary {summary_id} not found in topic {self.name}')

    # summaries is a summary_id list, [summary_id_1, summary_id_2, summary_id_3, ..., summary_id_n]
    def get_summaries(self, summaries_id: list):
        try:
            summaries = [self.summary_list[v] for v in summaries_id]
            return summaries
        except IndexError:
            summary_logger.critical(f'Summaries {summaries_id} not found in topic {self.name}')
            raise IndexError(f'Summaries {summaries_id} not found in topic {self.name}')

    def forget_dialog(self, dialog_id: int, time_gap=None, recall_time=None):
        if dialog_id not in self.dialog_dict:
            dialog_logger.critical(f'Dialog {dialog_id} not found in topic {self.name}')
            raise ValueError(f'Dialog {dialog_id} not found in topic {self.name}')
        dialog = self.dialog_dict[dialog_id]
        # Calculate current score
        if dialog.score == float('inf'):
            dialog_logger.info(f'the dialog {dialog_id}: {dialog.now_dialog} is a forever dialog')
            return
        dialog.recall_time = recall_time if recall_time else dialog.last_recall_time
        dialog.time_gap = time_gap if time_gap else tools.timeGap(dialog.last_recall_time)
        dialog.score = curve.forgetting_curve(dialog.time_gap, dialog.recall_time)
        # remove the whole dialog
        if dialog.score < config_curve["forgetting_min"]:
            for summary in self.summary_list:
                if dialog.summary_id == summary.summary_id:
                    summary.dialog_list.remove(dialog_id)
            dialog.topic = None
            dialog.topic_id = None
            del self.dialog_dict[dialog_id]
            dialog_logger.info(f'Forgot the whole dialog {dialog_id}: {dialog.now_dialog} successfully')
        # remove a part of dialog
        else:
            dialog.now_dialog = prompts.prompt_forget_dialog(nowDialog=dialog, language=language[0])
            dialog.now_embedding = api.call_embedding_openai([dialog.now_dialog['User'],
                                                              dialog.now_dialog['User'] + dialog.now_dialog['AI']])
            # dialog.now_tokens_length = len(
            #     tokenizer('User: ' + dialog.now_dialog["User"] + '\n' + 'AI: ' +
            #               dialog.now_dialog["AI"]))
            dialog.now_tokens_length = len(tokenizer(dialog.now_dialog["AI"]))
            dialog_logger.info(
                f'the dialog {dialog_id}: {dialog.now_dialog} ## {math.ceil(dialog.score * 100)}% remaining')

    def sort_summaries(self) -> list:  # []
        return sorted(self.summary_list, key=lambda item: (item.forever_dialogs_num, item.score), reverse=True)

    def update_personality(self):
        if self.summary_list:
            tmp_summary_list = self.sort_summaries()[:top_p_for_personality]  # [obj_1, obj_2, ..., obj_n]
            message_list = [summary.content for summary in tmp_summary_list]
        else:
            message_list = [value.source_dialog for (key, value) in self.dialog_dict.items()]
            if message_list >= top_p_for_summary:
                raise ValueError(f'dialogs number reached {top_p_for_summary} but not summary')
        self.personality = prompts.prompt_personality(messageList=message_list, language=language[0])
        self.personality_length = len(tokenizer(self.personality))
        personality_logger.info(f'Personality {self.personality} updated')

    def sort_dialogs(self) -> list:  # [(), (), ..., ()]
        return sorted(self.dialog_dict.items(), key=lambda item: item[1].score, reverse=True)


class Dialog:
    def __init__(self, topic: Topic, question: str = None, response: str = None, tokenizer=tokenizer,
                 new: bool = True):
        self.topic = topic
        self.topic_id = topic.topic_id
        if new:
            self.source_dialog = {'User': question, 'AI': response}
            self.now_dialog = {'User': question, 'AI': response}
            self.last_recall_time = tools.acquireNewTime()
            self.time_gap = 0
            self.recall_time = 1
            self.score = curve.forgetting_curve(self.time_gap, self.recall_time)
            self.dialog_id = topic.cur_dialog_id
            topic.cur_dialog_id += 1
            topic.dialog_dict[self.dialog_id] = self
            self.cache_flag = 0  # 0: not hit the cache, 1: not hit the cache, cooling
            self.ltm_hit_rate_num = 0
            # self.source_embedding = api.call_embedding_openai('User: ' + question + '\n' + 'AI: ' + response)
            self.source_embedding = api.call_embedding_openai([question, question + response])  # list
            self.now_embedding = self.source_embedding
            # self.source_tokens_length = len(tokenizer('User: ' + question + '\n' + 'AI: ' + response))
            self.source_tokens_length = len(tokenizer(response))
            self.now_tokens_length = self.source_tokens_length
        else:
            self.source_dialog = None
            self.now_dialog = None
            self.last_recall_time = -1
            self.time_gap = -1
            self.recall_time = -1
            self.score = -1
            self.dialog_id = -1
            self.cache_flag = -1
            self.ltm_hit_rate_num = -1
            self.source_embedding = -1
            self.now_embedding = -1
            self.source_tokens_length = -1
            self.now_tokens_length = -1

        self.summary_id = None
        # dialog_logger.info(f'Dialog-{self.dialog_id} init done')

    def recallDialog(self):
        # update time
        self.time_gap = 0
        self.last_recall_time = tools.acquireNewTime()
        self.recall_time = self.recall_time + 1
        # hit core + 1
        self.ltm_hit_rate_num = self.ltm_hit_rate_num + 1
        dialog_logger.info(f'Recall Dialog In LTM: {self.dialog_id}: {self.now_dialog}')
        # Information restoration in LTM
        self.now_dialog = self.source_dialog
        self.now_embedding = self.source_embedding
        self.now_tokens_length = self.source_tokens_length
        # update score to 1.0 or 'inf'
        if self.score == float('inf'):
            return
        self.score = curve.forgetting_curve(self.time_gap, self.recall_time)  # 1.0 or 'inf'
        if self.score == float('inf'):
            if self.summary_id is not None:
                self.topic.get_summary(self.summary_id).forever_dialogs_num += 1
            dialog_logger.info(f'Dialog-{self.dialog_id}: {self.source_dialog} became forever dialog')
            self.topic.forever_dialogs.append(self.dialog_id)


class Summary:
    def __init__(self, topic: Topic, dialog_id_list: list, total_score):
        assert len(dialog_id_list) == top_p_for_summary
        if not tools.check_all_elements_exist(dialog_id_list, topic.dialog_dict):
            try:
                raise ValueError(f'DialogList-{dialog_id_list} does not exist')
            except ValueError:
                summary_logger.error(f'DialogList-{dialog_id_list} does not exist')
        else:
            self.topic_id = topic
            self.summary_id = len(topic.summary_list)
            topic.summary_list.append(self)
            self.content = prompts.prompt_summary(
                dialogList=[topic.dialog_dict[key].now_dialog for key in dialog_id_list],
                language=language[0])  # string
            self.embedding = api.call_embedding_openai(self.content)
            self.tokens_length = len(tokenizer(self.content))
            # sort dialog_list
            dialog_list = topic.get_dialogs(dialog_id_list)
            dialog_list = sorted(dialog_list, key=lambda item: (item.score, item.recall_time, -item.time_gap),
                                 reverse=True)
            self.dialogs_id_list = [dialog.dialog_id for dialog in dialog_list]
            for dialog_id in dialog_id_list:
                topic.dialog_dict[dialog_id].summary_id = self.summary_id
            summary_logger.info(
                f'Summary: {self.summary_id} init done, based on {self.dialogs_id_list}: \n{self.content}')
            self.total_score = total_score
            # self.cache_hit_num = 0
            self.ltm_hit_rate_num = 0
            self.cache_flag = 0  # 0: not hit the cache, 1: not hit the cache, cooling
            tmp_dialogs = topic.get_dialogs(dialog_id_list)
            tmp_score = [1 if dialog.score == float('inf') else 0 for dialog in tmp_dialogs]
            self.forever_dialogs_num = sum(tmp_score)

    def get_new_score(self):
        self.total_score = sum([dialog.score for dialog in self.dialogs_id_list])

    def recallSummary(self):

        self.ltm_hit_rate_num += 1


class PrefetchSpace:
    def __init__(self, topic: Topic):
        # self.prefetch_size_max = short_term_space["prefetch_space_size"]
        # self.history_turn_max = short_term_space["history_turn_max"]
        # self.prefetch_frequency = short_term_space['prefetch_frequency']
        # self.top_p_summaries_dia = short_term_space['top_p_summaries']
        # self.top_p_dialogs = short_term_space['top_p_dialogs']
        self.last_per_length = 0
        self.summaries_id_list = []
        self.dialogs_id_list = []
        self.prefetch_size = 0
        self.topic = topic
        self.hit_num = 0
        prefetch_logger.info(f'PrefetchSpace Init done, for topic:{topic.name}')

    def update_prefetch_space(self):
        # personality update
        if self.last_per_length == 0 and self.topic.personality_length > 0:
            self.last_per_length = self.topic.personality_length
            self.prefetch_size += self.topic.personality_length
        elif self.last_per_length != 0 and self.topic.personality_length > 0:
            self.prefetch_size -= self.last_per_length
            self.last_per_length = self.topic.personality_length
            self.prefetch_size += self.topic.personality_length

        # update_summary_id_list
        # remove idle summaries
        for summary_id in self.summaries_id_list:
            summary = self.topic.get_summary(summary_id)
            self.summaries_id_list.remove(summary_id)
            self.prefetch_size -= summary.tokens_length
            summary.cache_flag = 1
            summary_logger.info(f'Summary: {summary_id} is removed into prefetch space, enter cooling')
        # remove idle dialogs
        for dialog_id in self.dialogs_id_list:
            dialog = self.topic.get_dialog(dialog_id)
            self.dialogs_id_list.remove(dialog_id)
            self.prefetch_size -= dialog.tokens_length
            dialog.cache_flag = 1
            dialog_logger.info(f'Dialog: {dialog_id} is removed into prefetch space, enter cooling')
        # add substitute summaries
        tmp_summaries_id_list = self.topic.sort_summaries()  # []
        while (len(self.summaries_id_list) < short_term_space['top_p_summaries'] and self.prefetch_size <
               short_term_space["prefetch_space_size"]):
            for summary_id in tmp_summaries_id_list:
                if summary_id not in self.summaries_id_list:
                    summary = self.topic.get_summary(summary_id)
                    # cooling time out
                    if summary.cache_flag == 1:
                        summary.cache_flag = 0
                        summary_logger.info(f'Summary: {summary_id} cooling time out')
                        continue
                    self.summaries_id_list.append(summary_id)
                    self.prefetch_size += summary.tokens_length
                    summary_logger.info(f'put summary id: {summary_id} into prefetch space')
                    if self.prefetch_size >= short_term_space["prefetch_space_size"]:
                        prefetch_logger.warning(
                            f'Prefetch space is full, {self.prefetch_size} >= {short_term_space["prefetch_space_size"]}')
                        break
        # add substitute dialogs in summary
        for summary_id in self.summaries_id_list:
            summary = self.topic.get_summary(summary_id)
            tmp_dialogs_num = 0
            while (tmp_dialogs_num < short_term_space['top_p_dialogs_in_summary'] and self.prefetch_size <
                   short_term_space["prefetch_space_size"]):
                for dialog_id in summary.dialogs_id_list:
                    if dialog_id not in self.dialogs_id_list:
                        dialog = self.topic.get_dialog(dialog_id)
                        # cooling time out
                        if dialog.cache_flag == 1:
                            dialog.cache_flag = 0
                            dialog_logger.info(f'Dialog: {dialog_id} cooling time out')
                            continue
                        self.dialogs_id_list.append(dialog_id)
                        self.prefetch_size += dialog.tokens_length
                        tmp_dialogs_num += 1
                        dialog_logger.info(f'put summary-dialog id: {dialog_id} into prefetch space')
                        if self.prefetch_size >= short_term_space["prefetch_space_size"]:
                            prefetch_logger.warning(
                                f'Prefetch space is full, {self.prefetch_size} >= {short_term_space["prefetch_space_size"]}')
                            break
        # add substitute dialogs not in summary
        alone_dialogs = [(key, value) for (key, value) in self.topic.dialog_dict.items() if value.summary_id is None]
        alone_dialogs = sorted(alone_dialogs, key=lambda item: (item[1].score, item[1].recall_time, -item[1].time_gap),
                               reverse=True)
        while (len(self.dialogs_id_list) < short_term_space['top_p_dialogs_in_summary'] *
               short_term_space['top_p_summaries'] + short_term_space['top_p_dialogs'] and
               self.prefetch_size < short_term_space["prefetch_space_size"]):
            for dialog_tuple in alone_dialogs:
                assert dialog_tuple[0] not in self.dialogs_id_list
                if dialog_tuple[1].cache_flag == 1:
                    dialog_tuple[1].cache_flag = 0
                    dialog_logger.info(f'Dialog: {dialog_tuple[0]} cooling time out')
                    continue
                self.dialogs_id_list.append(dialog_tuple[0])
                self.prefetch_size += dialog_tuple[1].tokens_length
                dialog_logger.info(f'put alone dialog id: {dialog_tuple[0]} into prefetch space')
                if self.prefetch_size >= short_term_space["prefetch_space_size"]:
                    prefetch_logger.warning(
                        f'Prefetch space is full, {self.prefetch_size} >= {short_term_space["prefetch_space_size"]}')
                    break
        # reset cache_flag to 0
        # for summary_id in self.summaries_id_list:
        #     summary = self.topic.get_summary(summary_id)
        #     summary.cache_flag = 0
        # for dialog_id in self.dialogs_id_list:
        #     dialog = self.topic.get_dialog(dialog_id)
        #     dialog.cache_flag = 0

        prefetch_logger.info(
            f'prefetch space update done, summaries_id_list: {self.summaries_id_list}, dialogs_id_list: {self.dialogs_id_list},\n, used_space: {self.prefetch_size}')


if __name__ == '__main__':
    pass
