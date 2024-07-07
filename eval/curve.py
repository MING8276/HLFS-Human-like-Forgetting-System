# Importing numpy for numerical operations and matplotlib for plotting
import numpy as np
import math
import matplotlib.pyplot as plt
from core.forget.curve import forgetting_curve, source_ab_curve
import utils.tools as tools

if __name__ == '__main__':
    # Figure_1
    x = np.linspace(1, 5, 200)
    y = 5 + 20 * np.tanh(0.5 * (x - 1))  # x -> recallTimes
    ye = (5 + 0.35 * np.exp(4)) - 0.35 * np.exp(-x + 5)
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='S = tanh-based', color='blue')
    plt.plot(x, 5 * x, label='S = 5 * recallTimes', color='green')
    plt.plot(x, 5 + 12 * np.log(x), label='S = Inx-based', color='red')
    plt.plot(x, ye, label='S = e^x-based', color='purple')
    plt.tight_layout()

    a = -13.5
    b = 37
    c = 1
    k = 1.5

    # Sigmoid
    ys = a + b / (1 + np.exp(-k * (x - c)))
    plt.plot(x, ys, label='S = sigmoid-based', color='pink')

    plt.title('The curve of S as a function of recallTimes')
    plt.xlabel('recallTimes')
    plt.ylabel('S', labelpad=1)
    plt.grid(True)
    plt.legend()
    plt.savefig('image/Figure 12.png', bbox_inches='tight')
    plt.show()
    # Figure_2
    score_1 = [forgetting_curve(i, 1, drawMode=1) for i in range(0, 24)]
    label = 'recallTimes=1'
    tools.plot_data(score_1, label=label)
    # Figure_8
    score_1 = [forgetting_curve(i, 1, drawMode=1) * 10000 for i in range(0, 24)]
    score_2 = [forgetting_curve(i, 2, drawMode=1) * 10000 for i in range(0, 24)]
    score_3 = [forgetting_curve(i, 3, drawMode=1) * 10000 for i in range(0, 24)]
    score_4 = [forgetting_curve(i, 4, drawMode=1) * 10000 for i in range(0, 24)]
    score_5 = [forgetting_curve(i, 5, drawMode=1) * 10000 for i in range(0, 24)]
    labels = ['recallTimes=1', 'recallTimes=2', 'recallTimes=3', 'recallTimes=4', 'recallTimes=5']
    tools.plot_multiple_data(score_1, score_2, score_3, score_4, score_5, labels=labels)
    # Figure_9
    score_1 = [source_ab_curve(i, 1, drawMode=1) * 10000 for i in range(0, 24)]
    score_2 = [source_ab_curve(i, 2, drawMode=1) * 10000 for i in range(0, 24)]
    score_3 = [source_ab_curve(i, 3, drawMode=1) * 10000 for i in range(0, 24)]
    score_4 = [source_ab_curve(i, 4, drawMode=1) * 10000 for i in range(0, 24)]
    score_5 = [source_ab_curve(i, 5, drawMode=1) * 10000 for i in range(0, 24)]
    labels = ['recallTimes=1', 'recallTimes=2', 'recallTimes=3', 'recallTimes=4', 'recallTimes=5']
    tools.plot_multiple_data(score_1, score_2, score_3, score_4, score_5, labels=labels)
