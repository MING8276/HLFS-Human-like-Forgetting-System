import json
import os
from core.retrieve.cos_sim import similarity
import utils.api as api
import argparse

language_choices = ['cn', 'en']
parser = argparse.ArgumentParser()
parser.add_argument("--language", type=str, default='en', choices=language_choices)
args = parser.parse_args()
language = args.language

topic_name = "video game"
retention = 'retention_56'

topic_file_name = f'../data/{language}/{topic_name}.json'
benchmark_file_name = f'../data/{language}/probing_questions_{topic_name}.json'
forgot_file_name = f'../eval/data/{retention}/{language}/{topic_name}/probing_questions_{topic_name}.json'


def topic_sim():
    if not os.path.exists(topic_file_name):
        raise FileNotFoundError(f'{topic_file_name} does not exist!')
    with open(topic_file_name, 'r', encoding='utf-8') as f:
        json_string = f.read()
    data = json.loads(json_string)
    topic_embedding = api.call_embedding_openai(data['topic_name'])
    question_embedding = api.call_embedding_openai([item['human'] for item in data['content']])
    score = sum([similarity(topic_embedding[0], question_embedding[i]) for i in range(len(question_embedding))]) / len(
        question_embedding)
    print(f'{topic_file_name}\nscore: {score}')


def benchmark_coherence():
    if not os.path.exists(benchmark_file_name):
        raise FileNotFoundError(f'{benchmark_file_name} does not exist!')
    with open(benchmark_file_name, 'r', encoding='utf-8') as f:
        json_string = f.read()
    data = json.loads(json_string)
    query_label_embedding = api.call_embedding_openai([item['traction'] + item['label'] for item in data['result']])
    hlfs_answer_embedding = api.call_embedding_openai([item['hlfs_answer'] for item in data['result']])
    mb_answer_embedding = api.call_embedding_openai([item['mb_answer'] for item in data['result']])
    scm_answer_embedding = api.call_embedding_openai([item['scm_answer'] for item in data['result']])

    for i in range(0, len(data['result'])):
        print(i + 1, [similarity(query_label_embedding[i], hlfs_answer_embedding[i]),
                      similarity(query_label_embedding[i], mb_answer_embedding[i]),
                      similarity(query_label_embedding[i], scm_answer_embedding[i])])


def forget_coherence():
    if not os.path.exists(forgot_file_name):
        raise FileNotFoundError(f'{forgot_file_name} does not exist!')
    with open(forgot_file_name, 'r', encoding='utf-8') as f:
        json_string = f.read()
    data = json.loads(json_string)
    query_label_embedding = api.call_embedding_openai([item['traction'] + item['label'] for item in data['result']])
    forgot_answer_embedding = api.call_embedding_openai([item['forgot_answer'] for item in data['result']])

    for i in range(0, len(data['result'])):
        print(i + 1, [similarity(query_label_embedding[i], forgot_answer_embedding[i])])


def __preprocessing():
    if not os.path.exists(forgot_file_name):
        raise FileNotFoundError(f'{forgot_file_name} does not exist!')
    with open(forgot_file_name, 'r', encoding='utf-8') as f:
        json_string = f.read()
    data = json.loads(json_string)
    results = data['result']
    for result in results:
        del result['mb_answer']
        del result['scm_answer']
        result['forgot_answer'] = ""
        result['answer_acc'] = -1
        result['recall_acc'] = -1
        result['retrieval_acc'] = -1
        result['coherence'] = -2
    data['result'] = results
    formatted_data = json.dumps(data, ensure_ascii=False, indent=4)
    with open(forgot_file_name, 'w', encoding='utf-8') as f:
        f.write(formatted_data)
    print(f'{forgot_file_name} preprocessing completed!')


if __name__ == '__main__':
    # topic_sim()
    # benchmark_coherence()
    # __preprocessing()
    # forget_coherence()
    pass
