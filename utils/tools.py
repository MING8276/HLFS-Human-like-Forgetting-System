import os
import datetime
import re
import matplotlib.pyplot as plt


def makeFile(fileName: str):
    if fileName is None:
        raise ValueError('fileName cannot be None')
    dir_path = os.path.dirname(os.path.abspath(fileName))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(fileName, 'w') as file:
        file.write('')


def acquireNewTime() -> str:
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


def timeGap(start) -> float:
    time_format = "%Y/%m/%d %H:%M:%S"
    some_time = datetime.datetime.strptime(start, time_format)
    now = datetime.datetime.now()
    delta = now - some_time
    hours = delta.total_seconds() / 3600  # hours
    return round(hours, 2)


def plot_data(values: list, label=None):
    x = range(0, len(values))
    plt.plot(x, values, marker='o', label=label, markersize=4)
    plt.title("Knowledge Retention Curves(Recall=1)")
    plt.xlabel("Time")
    plt.ylabel("R")
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def check_all_elements_exist(source, target) -> bool:
    return all(elem in source for elem in target)


def plot_multiple_data(*args, labels=None):
    if labels is None:
        labels = [f"列表 {i + 1}" for i in range(len(args))]
    for index, values in enumerate(args):
        x = range(0, len(values))
        plt.plot(x, values, marker='o', label=labels[index], markersize=4)
    plt.title("Comparative Analysis of Knowledge Retention Curves")
    plt.xlabel("timeGap")
    plt.ylabel("R")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.show()


def format_history(history, user_name: str) -> str:
    formatted_history = ""
    for entry in history:
        if 'User' in entry:
            formatted_history += f"[{user_name}]: " + entry['User'] + "\n"
        if 'AI' in entry:
            formatted_history += "[AI]: " + entry['AI'] + "\n"
    return formatted_history.strip()


def remove_number_prefix(input_string: str):
    pattern = r'(\d+)#'
    numbers = re.findall(pattern, input_string)
    modified_string = re.sub(pattern, '', input_string)
    if numbers:
        numbers = [int(num) for num in numbers]
    return_numbers = []
    [return_numbers.append(item) for item in numbers if item not in return_numbers]
    return modified_string, return_numbers


if __name__ == '__main__':
    pass
