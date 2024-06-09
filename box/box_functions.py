import os
import sys
import json
import time

import utils.tools as tools
from core.mem_struct import User, Topic, Summary, Dialog, PrefetchSpace


def load_username(username: str, file_dir: str, language: str = 'cn') -> User:
    if not username or not file_dir:
        raise ValueError('Username or fileDir cannot be empty')
    user = User(username)
    filepath = os.path.join(file_dir, username + '.json')

    if not os.path.exists(filepath):
        tools.makeFile(filepath)
        catalogue_path = os.path.join(file_dir, 'UserCatalogue.txt')
        with open(catalogue_path, 'a') as file:
            file.write(username + '\n')
        if language == 'cn':
            print(f"初次见面, 欢迎您, {username}! 让我们开始吧!")
        else:
            print(f"First time meeting, welcome {username}! Now let's begin!")
    else:
        with open(filepath, 'r') as file:
            json_string = file.read()
        tmp_user = json.loads(json_string)
        if username != tmp_user['name']:
            raise ValueError(f'Username {username} does not match')
        user.topic_name_list = tmp_user['topic_name_list']
        # user.topic_list = tmp_user['topic_list']
        if language == 'cn':
            print(f"欢迎回来，欢迎您，{username}! 让我们继续吧!")
        else:
            print(f"Welcome back, welcome {username}! Let's keep going!")
    return user


def load_resource(username, topic_name: str, file_dir: str, user=None) -> dict:
    filepath = os.path.join(file_dir, username + '_' + topic_name + '.json')
    if not os.path.exists(filepath):
        raise ValueError(f'filepath: {filepath} is not exist! Please check it')
    with open(filepath, 'r') as file:
        json_string = file.read()
    tmp_topic = json.loads(json_string)
    topic = Topic(user, name=topic_name, new=False)
    topic.topic_id = tmp_topic['topic_id']
    topic.forever_dialogs = tmp_topic['forever_dialogs']
    topic.cur_dialog_id = tmp_topic['cur_dialog_id']
    dialog_list = []
    dialogues = {int(key): value for key, value in tmp_topic['dialog_dict'].items()}
    for dialog_id, dialog_dict in dialogues.items():
        dialog = Dialog(topic, new=False)
        dialog.dialog_id = dialog_id
        dialog.now_dialog = dialog_dict['now_dialog']
        dialog.source_dialog = dialog_dict['source_dialog']
        dialog.last_recall_time = dialog_dict['last_recall_time']
        dialog.time_gap = dialog_dict['time_gap']
        dialog.recall_time = dialog_dict['recall_time']
        dialog.score = dialog_dict['score']
        dialog.cache_flag = dialog_dict['cache_flag']
        dialog.ltm_hit_rate_num = dialog_dict['ltm_hit_rate_num']
        dialog.source_embedding = dialog_dict['source_embedding']
        dialog.now_embedding = dialog_dict['now_embedding']
        dialog.source_tokens_length = dialog_dict['source_tokens_length']
        dialog.now_tokens_length = dialog_dict['now_tokens_length']
        topic.dialog_dict[dialog_id] = dialog
        dialog_list.append(dialog)
    return {'topic': topic, 'dialogues': dialog_list}


def save_message_with_user(user, topic, dialogues, save_dir):
    dialogues_dict = {}
    for dialog in dialogues:
        tmp = {'now_dialog': dialog.now_dialog, 'source_dialog': dialog.source_dialog,
               'last_recall_time': dialog.last_recall_time,
               'time_gap': dialog.time_gap, 'recall_time': dialog.recall_time, 'score': dialog.score, 'cache_flag': 0,
               'ltm_hit_rate_num': dialog.ltm_hit_rate_num, 'source_embedding': dialog.source_embedding,
               'now_embedding': dialog.now_embedding,
               'source_tokens_length': dialog.source_tokens_length, 'now_tokens_length': dialog.now_tokens_length}
        dialogues_dict[str(dialog.dialog_id)] = tmp
    topic_dict = {'topic_id': topic.topic_id, 'topic_name': topic.name, 'cur_dialog_id': topic.cur_dialog_id,
                  'forever_dialogs': topic.forever_dialogs, 'dialog_dict': dialogues_dict}
    user_dict = {'name': user.name, 'topic_name_list': user.topic_name_list}
    user_string = json.dumps(user_dict)
    topic_string = json.dumps(topic_dict)
    user_path = os.path.join(save_dir, user.name + '.json')
    topic_path = os.path.join(save_dir, user.name + '_' + topic.name + '.json')
    with open(user_path, 'w') as file:
        file.write(user_string)
    print(f'File saved successfully at {user_path}')
    with open(topic_path, 'w') as file:
        file.write(topic_string)
    print(f'File saved successfully at {topic_path}')


def __save_message_with_username(username: str, topic, dialogues, save_dir):
    dialogues_dict = {}
    for dialog in dialogues:
        tmp = {'now_dialog': dialog.now_dialog, 'source_dialog': dialog.source_dialog,
               'last_recall_time': dialog.last_recall_time,
               'time_gap': dialog.time_gap, 'recall_time': dialog.recall_time, 'score': dialog.score, 'cache_flag': 0,
               'ltm_hit_rate_num': dialog.ltm_hit_rate_num, 'source_embedding': dialog.source_embedding,
               'now_embedding': dialog.now_embedding,
               'source_tokens_length': dialog.source_tokens_length, 'now_tokens_length': dialog.now_tokens_length}
        dialogues_dict[str(dialog.dialog_id)] = tmp
    topic_dict = {'topic_id': topic.topic_id, 'topic_name': topic.name, 'cur_dialog_id': topic.cur_dialog_id,
                  'forever_dialogs': topic.forever_dialogs, 'dialog_dict': dialogues_dict}
    topic_string = json.dumps(topic_dict)
    topic_path = os.path.join(save_dir, username + '_' + topic.name + '.json')
    with open(topic_path, 'w') as file:
        file.write(topic_string)
    print(f'File saved successfully at {topic_path}')


def trigger_forgetting(history_dir: str, time_gap=None, recall_time=None):
    if not os.path.exists(history_dir):
        raise ValueError(f'History dir {history_dir} does not exist')
    catalogue_path = os.path.join(history_dir, 'UserCatalogue.txt')
    if not os.path.exists(catalogue_path):
        raise ValueError(f'UserCatalogue file {catalogue_path} does not exist')
    usernames = []
    with open(catalogue_path, 'r') as file:
        for line in file:
            usernames.append(line.strip())
    for username in usernames:
        filepath = os.path.join(history_dir, username + '.json')
        if not os.path.exists(filepath):
            raise ValueError(f'User: {username} profile not established')
        with open(filepath, 'r') as file:
            json_string = file.read()
        user_dict = json.loads(json_string)
        topic_names = user_dict['topic_name_list']
        for topic_name in topic_names:
            # dialogues is a dialogues object list
            resource_dict = load_resource(username, topic_name, history_dir)
            for dialog in resource_dict['dialogues']:
                resource_dict['topic'].forget_dialog(dialog.dialog_id, time_gap, recall_time)
            filtered_dialogues = [dialog_obj for dialog_obj in resource_dict['dialogues'] if dialog_obj.topic]
            __save_message_with_username(username, resource_dict['topic'], filtered_dialogues, history_dir)
            print(f'{username}-{topic_name} forgetting success')
    print('The forgetting process is all completed!')
