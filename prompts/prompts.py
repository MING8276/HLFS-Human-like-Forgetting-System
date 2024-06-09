import utils.api as api
import openai
import os
import math
import utils.tools as tools
from core.retrieve.cos_sim import similarity
import json
from config.config import short_term_space
from core.retrieve.faiss import retrieve_in_PAISS
from utils.log import dialog_logger, topic_logger

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_ask_dict = {
    "cn": """
你是一位聊天专家,请针对用户{user_name}的问题，进行回答

有一些关于之前对话的参考信息(包括历史记录，与问题最相关的信息)，可以进行参考

以下是一些与回答问题```{query}```最相关的信息:

{dialog}

以下是历史对话记录:

{history}

请与{user_name}聊天:

输入:

{user_name}的问题

输出:

[你的回答]

输出要求:

根据你的通用知识，并适当参考历史对话记录，尤其重点参考最相关的信息，进行回答。

请注意要让问题```{query}```的最直接答案在输出的最前面展现。

让我们开始: 

{user_name}: {query}

输出:
""",
    "en": """
You are a chat expert. Please answer the question from user {user_name}

There are some reference information about previous conversations (including historical records,

and the most relevant information) that can be used as a reference

Here are some of the most relevant information related to answering the question```{query}```:
{dialog}

Here is a record of the previous dialogue:
{history}

Please chat with {user_name}:

Input:
Question from {user_name}

Output:
[Your answer]

Output requirements:

Based on your general knowledge and with appropriate reference to the historical dialogue records,

especially focusing on the most relevant information, please provide an answer.

Please note that the most direct answer to the question```{query}```should be presented at the beginning of the output.

Let's start:

{user_name}: {query}
Output:
"""
}

prompt_judge_dict = {
    "cn":
        """
给定对话内容和用户问题，请回答命令问题。

对话内容: ```{content}```

用户问题: ```{query}```

命令问题：基于对话内容，用户问题可以通过对话内容被回答吗？回答Yes表示yes，回答None表示no。

请严格按照以下格式回答: 

[你的回答]: Yes/None
"""
    , "en":
        """
Given the conversation content and the user

question, please answer the command question.

Conversation Content: ```{content}```

User Question: ```{query}```

Command Question: Based on the conversation

content, can the user question be answered by

conversation content? Respond with Yes for yes,

None for no. 

Please strictly follow the format below to answer

the questions:
[Answer]: Yes / None.
"""
}

prompt_get_topic_dict = {
    "cn":
        """
给定一段对话内容，请你基于这段对话内容总结出一个对话主题，主题只能用一个短语概括(小于等于5个字，不能存在标点符号)。

对话内容:

{history}  

请严格按照如下格式输出:

主题名称
""",
    "en":
        """
Given a conversation, please summarize a conversation topic based on this conversation content.

The topic can only be summarized in one phrase (less than or equal to 5 words, no punctuation).

Dialogue content:

{history}

Please output strictly in the following format:

Topic Name
"""
}

prompt_retrieve_dict = {
    "cn":
        """
给定许多原句子。

输出问题: ```{query}```最近似相关的一个原句, 这个原句应该能够直接回答```{query}```。

原句格式为: 数字序号#文字内容

输出格式:

原句(必须原封不动，不能改变一点)

例如:

6#我爷爷喜欢历史、文学、诗歌，他最喜欢写诗，他的文字很有力量
""",
    "en":
        """
Given lots of original sentence.

Output the original sentence that is most closely related the question: ```{query}```,

which can directly answer it.

The original sentence format being "Number#Text Content"

Output format:
The original sentence(The format must adhere to the original sentence format)

For example:

6#My grandfather likes history, literature, and poetry. He loves writing poetry the most, and his writing is very powerful
"""
}

prompt_forget_dict = {
    "cn":
        """
你是简化句子的专家。现在给定一个原句子：“{sentence}”。

你的任务是将其内容高度压缩，使得新句子的长度为原句长度的{score}%。

否则请隐式计算原句的长度，然后生成一个相应长度的新句子。

要求：

遵循长度是最重要的目标，请千万确保你输出的句子不超过原句长度的{score}%。

输出格式:

精简后的句子   
""",
    "en":
        """
You are an expert in simplifying sentences. Now give an original sentence: "{sentence}".

Your task is to highly compress its content so that the length of the new sentence is {score}% of the original sentence length.

Please implicitly calculate the length of the original sentence and generate a new sentence of the corresponding length.

Requirement:

Following length is the most important goal, please make sure that your output sentence does not exceed {score}% of the original sentence length.

Output format:

Simplified sentences
"""
}

prompt_ask_scm_dict = {
    "cn":
        """
以下是用户和人工智能助手的对话，请根据历史对话内容，回答用户当前问题：

相关历史对话：

{dialog}

历史对话记录：

{history}

###

User：{query}

AI：
""",
    "en":
        """
The following is a conversation between a user and an AI assistant.
 
Please answer the current question based on the history of the conversation:

Related conversation history:

{dialog}

Historical conversation records:

{history}

###

User: {query}

AI:    
"""
}

def prompt_forget_dialog(nowDialog, language: str = 'cn') -> dict:  # nowDialog: {Q: , R: }
    sentence = nowDialog.source_dialog['AI']
    if nowDialog.score > 0.95:
        return nowDialog
    response = sentence[:math.ceil(nowDialog.score * len(sentence))]
    # message = [{'role': 'system',
    #             'content': prompt_forget_dict[language].format(sentence=sentence,
    #                                                            score=score_percentage)}]
    # max_tokens = math.ceil(nowDialog.source_tokens_length * nowDialog.score)
    # response = api.call_gpt3_5_turbo(message, max_tokens=max_tokens)
    return {'User': nowDialog.source_dialog['User'], 'AI': response}

def prompt_ask_scm(user, query: str, history: list, resource, history_dir: str, language: str = 'cn') -> str:
    topic = resource.get('topic')
    query_embedding = api.call_embedding_openai(query)
    dialog = []
    if resource.get('dialogues'):
        assert topic.name
        dialogues_list = resource.get('dialogues')
        candidates = [[dialog, dialog.now_embedding[1]]
                      for dialog in dialogues_list]
        for candidate in candidates:
            candidate[1] = similarity(query_embedding[0], candidate[1])
        sorted_list = sorted(candidates, key=lambda item: item[1], reverse=True)
        most_relevant_dialogs = [sorted_list[0][0], sorted_list[1][0]]
        for d in most_relevant_dialogs:
            dialog.append(d.now_dialog)
        dialog = tools.format_history(dialog, user.name)
        print("------[" + dialog + "]------")

    message = [{'role': 'system', 'content': prompt_ask_scm_dict[language].format(
                                                                              history=tools.format_history(history,
                                                                                                           user.name),
                                                                              dialog=dialog if dialog else None,
                                                                              query=query)}]
    response = api.call_gpt3_5_turbo(message)
    return response


def prompt_ask(user, query: str, history: list, resource, history_dir: str, language: str = 'cn',
               test_model: bool = False) -> str:
    topic = resource.get('topic')
    dialogues = []
    dialog = []
    # retrieve relevant message
    if resource.get('dialogues'):
        assert topic.name
        index_path = os.path.join(history_dir, user.name + '_' + topic.name + '_index' + '.json')
        dialogues_list = resource.get('dialogues')
        for dialog in dialogues_list:
            tmp_dict = {'User': str(dialog.dialog_id) + '#' + dialog.now_dialog['User'],
                        'AI': str(dialog.dialog_id) + '#' + dialog.now_dialog['AI']}
            dialogues.append(tmp_dict)
        result = retrieve_in_PAISS(tools.format_history(dialogues, user.name),
                                   prompt_retrieve_dict[language].format(query=query),
                                   index_path=index_path)
        print('-----------------------[' + result + ']-----------------------')
        dialog, hit_dialog_id_list = tools.remove_number_prefix(result)
        if not hit_dialog_id_list:
            dialog_logger.warning('FAISS not hit anything, reject recall dialogues')
        else:
            # Similarity determination
            dialog = ''
            candidates = [[dialog.dialog_id, dialog.now_embedding[1]] for dialog in dialogues_list]
            dialog_embedding = api.call_embedding_openai(query)
            for candidate in candidates:
                candidate[1] = similarity(dialog_embedding[0], candidate[1])
            sorted_list = sorted(candidates, key=lambda item: item[1], reverse=True)
            tmp_hit_dialogues_ids = [value[0] for value in sorted_list[:2]]
            if hit_dialog_id_list[0] not in tmp_hit_dialogues_ids:
                hit_dialog_id_list = tmp_hit_dialogues_ids
            else:
                if hit_dialog_id_list[0] == tmp_hit_dialogues_ids[1]:
                    hit_dialog_id_list.append(tmp_hit_dialogues_ids[0])
            # recall dialog
            for hit_dialog_id in hit_dialog_id_list:
                flag = 0
                for tmp_dialog in dialogues_list:
                    if hit_dialog_id == tmp_dialog.dialog_id:
                        dialog = dialog + tools.format_history([tmp_dialog.now_dialog], user.name) + '\n'
                        if not test_model:
                            tmp_dialog.recallDialog()
                        else:
                            dialog_logger.info(f'##TEST_MODEL## Recall Dialog In LTM: {tmp_dialog.dialog_id}: {tmp_dialog.now_dialog}')
                        flag = 1
                    if flag == 1:
                        break
                if flag == 0:
                    raise ValueError(f'The dialog id: {hit_dialog_id} is incorrect')


    message = [{'role': 'system', 'content': prompt_ask_dict[language].format(user_name=user.name,
                                                                              history=tools.format_history(history,
                                                                                                           user.name),
                                                                              dialog=dialog if dialog else None,
                                                                              query=query)}]

    response = api.call_gpt3_5_turbo(message)
    return response


def prompt_get_topic(user, history: list, language: str = 'cn') -> str:
    message = [{'role': 'system',
                'content': prompt_get_topic_dict[language].format(history=tools.format_history(history, user.name))}]
    response = api.call_gpt3_5_turbo(message)
    return response


if __name__ == '__main__':
    s = '爷爷80多岁了，平日里除了喜欢写诗还喜欢散步、听国际时事，也喜欢在广场上跟朋友们晒太阳、聊天，我的奶奶也有80多岁了，她跟爷爷结婚了大半辈子，抚养了三个孩子。她每天在厨房里忙碌着，洗菜做饭，她有时候心情会不好，喜欢跟爷爷拌嘴，但他们依然十分相爱，互相依赖'
    message = [{'role': 'system',
                'content': prompt_forget_dict["cn"].format(sentence=s, score=90)}]
    response = api.call_gpt3_5_turbo(message, max_tokens=50)
    print(response)
