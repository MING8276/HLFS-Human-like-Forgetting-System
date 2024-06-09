import sched
import time
import argparse
from box.box_functions import trigger_forgetting

scheduler = sched.scheduler(time.time, time.sleep)


def scheduled_function(interval, history_dir):
    trigger_forgetting(history_dir)
    scheduler.enter(interval, 1, scheduled_function, (interval, history_dir))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--history_path", type=str, default='../history')
    parser.add_argument("--time_gap", type=int, default=1)
    parser.add_argument("--recall_times", type=int, default=1)
    parser.add_argument("--forgetting_cycle", type=int, default=1)
    parser.add_argument("--test_model", type=bool, default=False)
    args = parser.parse_args()
    if args.test_model:
        trigger_forgetting(args.history_path, time_gap=args.timeGap, recall_time=args.recallTimes)
    else:
        scheduler.enter(0, 1, scheduled_function, (args.forgetting_cycle, args.history_path))
        scheduler.run()
