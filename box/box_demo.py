import argparse
import os
import platform
import box_functions as functions
from core.mem_struct import Topic, Dialog
import config.config as config
import prompts.prompts as prompts

os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    language_choices = ['cn', 'en']
    ltm_box_choices = ['hlfs', 'scm']
    parser.add_argument("--language", type=str, default='en', choices=language_choices)
    parser.add_argument("--history_path", type=str, default='../history')
    parser.add_argument("--test_model", type=bool, default=False)
    parser.add_argument("--ltm_box", type=str, default='hlfs', choices=ltm_box_choices)
    args = parser.parse_args()
    language = args.language
    test_model = args.test_model
    history_dir = args.history_path
    ltm_box = args.ltm_box
    # os.path.join(directory, filename)
    history = []  # [{'User':, 'AI': }, {'User':, 'AI': }, ..., {'User':, 'AI': }]
    if language == 'cn':
        print('\n请输入用户名:')
    else:
        print('\nPlease Enter Your Name:')
    user_name = input("")
    user = functions.load_username(user_name, history_dir, language)
    resource = {}
    dialogues = []
    # prefetch_trigger = 0
    # continue
    if user.topic_name_list:
        if language == 'cn':
            print(
                f'您上次进行了关于{user.topic_name_list}的对话, 您是否希望继续其中的某一个话题?\n(如果想，请输入您希望继续的话题，否则无需输入):')
        else:
            print(
                f'Last time you had a conversation about {user.topic_name_list}, would you like to continue on one of '
                f'the topics?\n(If desired, please enter the topic you wish to continue with, otherwise there is no '
                f'need to enter):')
        topic_name = input("")
        while topic_name not in user.topic_name_list and topic_name:
            if language == 'cn':
                print(f'请输入正确的主题:')
            else:
                print(f'Please enter the correct topic:')
            topic_name = input("")
        if topic_name:
            print("loading...")
            resource = functions.load_resource(user.name, topic_name, history_dir, user=user)
            print("##########################")
            if language == 'cn':
                print(
                    f"加载完毕，让我们继续话题(输入[stop]停止对话，输入[clear]清空历史记录): {topic_name}")
            else:
                print(f"Loading completed, let's continue with the topic(Enter [stop] to stop the conversation, "
                      f"enter [clear] to clear history): {topic_name}")
        else:
            if language == 'cn':
                print(
                    "让我们开启一个崭新的话题吧(输入[stop]停止对话，输入[clear]清空历史记录): ")
            else:
                print("Let's start a brand-new topic(Enter [stop] to stop the conversation, "
                      f"enter [clear] to clear history):")
            resource['dialogues'] = dialogues
    else:
        resource['dialogues'] = dialogues
        if language == 'cn':
            print(
                "让我们开启一个崭新的话题吧(输入[stop]停止对话，输入[clear]清空历史记录): ")
        else:
            print("Let's start a brand-new topic(Enter [stop] to stop the conversation, "
                  f"enter [clear] to clear history):")
    while True:
        query = input(f"\n{user_name}: ").strip()
        if query == "stop":
            break
        if query == "clear":
            history = []
            os.system(clear_command)
            continue
        if not query:
            continue
        if not resource.get("topic"):
            resource['topic'] = Topic(user)
        if ltm_box == 'hlfs':
            response = prompts.prompt_ask(user=user, query=query, resource=resource, history_dir=history_dir,
                                          history=history[-config.without_topic_history_turn_max:],
                                          language=language, test_model=test_model)
        else:
            response = prompts.prompt_ask_scm(user=user, query=query, resource=resource, history_dir=history_dir,
                                              history=history[-config.without_topic_history_turn_max:],
                                              language=language)
        history.append({'User': query, 'AI': response})
        print('AI: ', response)
        if len(history) > config.without_topic_history_turn_max and not test_model:
            if not resource.get("topic").name:
                resource['topic'].rename_topic(user, prompts.prompt_get_topic(user, history, language))
            dialog = Dialog(topic=resource['topic'], question=history[0]['User'], response=history[0]['AI'])
            resource['dialogues'].append(dialog)
            del history[0]
    if test_model:
        print("test over")
        exit(0)
    print("Saving user history...")
    if not resource.get("topic").name:
        resource['topic'].rename_topic(user, prompts.prompt_get_topic(user, history, language))
    while history:
        dialog = Dialog(topic=resource['topic'], question=history[0]['User'], response=history[0]['AI'])
        resource['dialogues'].append(dialog)
        del history[0]
    topic = resource['topic']
    functions.save_message_with_user(user=user, topic=topic, dialogues=resource['dialogues'], save_dir=history_dir)
    print("Save completed!")
