import json
import os
import utils.tools as tools
import box.box_functions as functions
from core.mem_struct import User, Topic, Dialog

data_dir = "../data/en"
data_file = "exercise.json"
history_dir = "../history"


def save_to_memory_bank(dialogues, username):
    memory_bank_dir = os.path.join(data_dir, 'memory_bank')
    filepath = os.path.join(memory_bank_dir, 'update_memory.json')
    memory_bank_dict = {}
    history_dict = {}
    history_dict["2024-05-02"] = []
    for dialog in dialogues:
        history_dict["2024-05-02"].append({"query": dialog.now_dialog["User"], "response": dialog.now_dialog["AI"]})
    memory_bank_dict[username] = {"name": username, "history": history_dict}
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(json.dumps(memory_bank_dict))
    print(f"Save memory bank to {filepath}")


if __name__ == '__main__':

    file_name = os.path.join(data_dir, data_file)
    if not os.path.exists(file_name):
        raise FileNotFoundError(f'{file_name} not found')
    with open(file_name, 'r', encoding='utf-8') as f:
        json_string = f.read()
    data = json.loads(json_string)
    # load user
    user = User(data['username'])
    filepath = os.path.join(history_dir, data['username'] + '.json')
    if not os.path.exists(filepath):
        tools.makeFile(filepath)
        catalogue_path = os.path.join(history_dir, 'UserCatalogue.txt')
        with open(catalogue_path, 'a') as file:
            file.write(data['username'] + '\n')
    else:
        with open(filepath, 'r') as file:
            json_string = file.read()
        tmp_user = json.loads(json_string)
        if data['username'] != tmp_user['name']:
            raise ValueError(f'username does not match')
        user.topic_name_list = tmp_user['topic_name_list']

    topic = Topic(user, data['topic_name'])
    dialogues = []
    for dialog_dict in data['content']:
        dialogue = Dialog(topic=topic, question=dialog_dict['human'], response=dialog_dict['chatgpt'])
        dialogues.append(dialogue)
    functions.save_message_with_user(user, topic, dialogues, history_dir)
    save_to_memory_bank(dialogues, user.name)
