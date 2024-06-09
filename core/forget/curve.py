import numpy as np
import math
import utils.tools as tools
from config.config import config_curve
from utils.log import Logs

forgetting_curve_logger = Logs('forgetting_curve')


def forgetting_curve(timeGap, recallTimes, config=config_curve, drawMode=0):
    score = None
    if timeGap < 0 or recallTimes <= 0:
        forgetting_curve_logger.error('timeGap or recallTimes must be greater than 0.')
    if 1 <= recallTimes <= config['forever_remember']:
        r = 0.5 * (recallTimes + 1)
        s = config['expand_overall'] + config['expand_y'] * np.tanh(
            r - config['offset_x'])
        # s = -13.5 + 37 / (1 + np.exp(-1.5 * (recallTimes - 1)))
        # s = (5 + 0.35 * np.exp(4)) - 0.35 * np.exp(-recallTimes + 5)
        score = math.exp(-timeGap / s)
    else:
        score = float('inf')
    if drawMode:
        return score
    else:
        return __final_score(score, config_curve)


def source_ab_curve(timeGap, recallTimes, config=config_curve, drawMode=0):
    score = None
    if 1 <= recallTimes <= config['forever_remember']:
        score = math.exp(-timeGap / (5 * recallTimes))
    else:
        score = float('inf')
    if drawMode:
        return score
    else:
        return __final_score(score, config_curve)


def __final_score(score: float, config=config_curve):
    if score < config['forgetting_min']:
        return 0
    elif score == float('inf'):
        return score
    else:
        return round(score, 2)


if __name__ == '__main__':
    for j in range(1, 6):
        print([source_ab_curve(i, j, config_curve, drawMode=1) for i in range(24)])
    print('############')
    for j in range(1, 6):
        print([forgetting_curve(i, j, config_curve, drawMode=1) for i in range(24)])
    # print(forgetting_curve(6, 1))
