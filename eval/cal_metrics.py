import json
import os
import argparse

language_choices = ['cn', 'en']
parser = argparse.ArgumentParser()
parser.add_argument("--language", type=str, default='en', choices=language_choices)
args = parser.parse_args()
language = args.language

history_dir = f'../data/{language}'
prefix = 'probing_questions_'
retention_list = ['retention_82', 'retention_56', 'retention_30']  # ['retention_82', 'retention_56', 'retention_30']
file_list_cn = ['品红茶', '增进爱情', '婚姻彩礼问题', '教育孩子', '旅行规划', '歌星与歌曲', '爷爷与诗歌', '电子游戏',
                '销售珠宝首饰', '锻炼身体']
file_list_en = ['tasting black tea', 'enhance love', 'The issue of dowry in marriage', 'educate a child',
                'travel planning', 'singers and songs', 'grandfather and poetry', 'video game',
                'selling jewelry and jewelry', 'exercise']

sum_len = 0

# benchmark metrics
sum_answer_acc_hlfs = 0
sum_answer_acc_mb = 0
sum_answer_acc_scm = 0

sum_retrieval_acc_hlfs = 0
sum_retrieval_acc_mb = 0
sum_retrieval_acc_scm = 0

sum_coherence_hlfs = 0
sum_coherence_mb = 0
sum_coherence_scm = 0

sum_recall_acc = 0

ask_answer_acc_hlfs = 0
ask_retrieval_acc_hlfs = 0
ask_coherence_hlfs = 0
ask_recall_acc = 0
ask_len = 0

rep_answer_acc_hlfs = 0
rep_retrieval_acc_hlfs = 0
rep_coherence_hlfs = 0
rep_recall_acc = 0
rep_len = 0

# retention metrics
ask_forgot_answer_acc = 0
ask_forgot_retrieval_acc = 0
ask_forgot_coherence = 0
ask_forgot_recall_acc = 0

rep_forgot_answer_acc = 0
rep_forgot_retrieval_acc = 0
rep_forgot_coherence = 0
rep_forgot_recall_acc = 0

if __name__ == '__main__':

    if language == 'cn':
        file_list = file_list_cn
    else:
        file_list = file_list_en
    # benchmark metrics
    for f in file_list:
        file_name = os.path.join(history_dir, prefix + f + '.json')
        if not os.path.exists(file_name):
            raise ValueError(f'File {file_name} does not exist!')
        with open(file_name, 'r', encoding='utf-8') as file:
            json_string = file.read()
        data = json.loads(json_string)
        results = data['result']  # results is a list: [{}, .., {}]
        sum_len += len(results)
        for result in results:
            if result['tag'] == 0:
                ask_answer_acc_hlfs += result['answer_acc'][0]
                ask_retrieval_acc_hlfs += result['retrieval_acc'][0]
                ask_coherence_hlfs += result['coherence'][0]
                ask_recall_acc += result['recall_acc']
                ask_len += 1
            else:
                rep_answer_acc_hlfs += result['answer_acc'][0]
                rep_retrieval_acc_hlfs += result['retrieval_acc'][0]
                rep_coherence_hlfs += result['coherence'][0]
                rep_recall_acc += result['recall_acc']
                rep_len += 1

            sum_answer_acc_hlfs += result['answer_acc'][0]
            sum_retrieval_acc_hlfs += result['retrieval_acc'][0]
            sum_coherence_hlfs += result['coherence'][0]
            sum_recall_acc += result['recall_acc']

            sum_answer_acc_mb += result['answer_acc'][1]
            sum_retrieval_acc_mb += result['retrieval_acc'][1]
            sum_coherence_mb += result['coherence'][1]

            sum_answer_acc_scm += result['answer_acc'][2]
            sum_retrieval_acc_scm += result['retrieval_acc'][2]
            sum_coherence_scm += result['coherence'][2]

    # retention metrics
    for rate in retention_list:
        file_dir = f'../eval/data/{rate}/{language}'
        for f in file_list:
            file_name = os.path.join(file_dir, f, prefix + f + '.json')
            if not os.path.exists(file_name):
                raise ValueError(f'File {file_name} does not exist!')
            with open(file_name, 'r', encoding='utf-8') as file:
                json_string = file.read()
            data = json.loads(json_string)
            results = data['result']
            for result in results:
                if result['tag'] == 0:
                    ask_forgot_answer_acc += result['answer_acc']
                    ask_forgot_retrieval_acc += result['retrieval_acc']
                    ask_forgot_recall_acc += result['recall_acc']
                    ask_forgot_coherence += result['coherence']
                else:
                    rep_forgot_answer_acc += result['answer_acc']
                    rep_forgot_retrieval_acc += result['retrieval_acc']
                    rep_forgot_recall_acc += result['recall_acc']
                    rep_forgot_coherence += result['coherence']
        print(f'{language}:\n{rate}:\n'
              f'ask_forgot_answer_acc = {ask_forgot_answer_acc / ask_len}, '
              f'ask_forgot_retrieval_acc = {ask_forgot_retrieval_acc / ask_len}, '
              f'ask_forgot_coherence = {ask_forgot_coherence / ask_len}, '
              f'ask_forgot_recall_acc = {ask_forgot_recall_acc / ask_len}')
        print('-----------------------------')
        print(f'rep_forgot_answer_acc = {rep_forgot_answer_acc / rep_len}, '
              f'rep_forgot_retrieval_acc = {rep_forgot_retrieval_acc / rep_len}, '
              f'rep_forgot_coherence = {rep_forgot_coherence / rep_len}, '
              f'rep_forgot_recall_acc = {rep_forgot_recall_acc / rep_len}')
        # reduction
        ask_forgot_answer_acc = 0
        ask_forgot_retrieval_acc = 0
        ask_forgot_recall_acc = 0
        ask_forgot_coherence = 0

        rep_forgot_answer_acc = 0
        rep_forgot_retrieval_acc = 0
        rep_forgot_recall_acc = 0
        rep_forgot_coherence = 0

    print('#############################')

    print(
        f'{language}:\n\nhlfs: answer_acc = {sum_answer_acc_hlfs / sum_len},'
        f' retrieval_acc = {sum_retrieval_acc_hlfs / sum_len}, '
        f'coherence = {sum_coherence_hlfs / sum_len}, recall_acc = {sum_recall_acc / sum_len}\n'
        f'MB: answer_acc = {sum_answer_acc_mb / sum_len}, retrieval_acc = {sum_retrieval_acc_mb / sum_len}, '
        f'coherence = {sum_coherence_mb / sum_len}\nSCM: answer_acc = {sum_answer_acc_scm / sum_len}, '
        f'retrieval_acc = {sum_retrieval_acc_scm / sum_len}, coherence = {sum_coherence_scm / sum_len}')
    print('******************************')
    print(f'ask_answer_acc_hlfs = {ask_answer_acc_hlfs / ask_len}, '
          f'ask_retrieval_acc_hlfs = {ask_retrieval_acc_hlfs / ask_len}, '
          f'ask_coherence_hlfs = {ask_coherence_hlfs / ask_len}, '
          f'ask_recall_acc = {ask_recall_acc / ask_len}')
    print('-----------------------------')
    print(f'rep_answer_acc_hlfs = {rep_answer_acc_hlfs / rep_len}, '
          f'rep_retrieval_acc_hlfs = {rep_retrieval_acc_hlfs / rep_len}, '
          f'rep_coherence_hlfs = {rep_coherence_hlfs / rep_len}, '
          f'rep_recall_acc = {rep_recall_acc / rep_len}')
