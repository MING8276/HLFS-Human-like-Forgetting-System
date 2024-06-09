# 🚀HLFS: Enabling Long-term Memory to Forget like human

This is the official repository for the paper "HLFS: Enabling Long-term Memory to Forget like human". 
In this paper, we introduce the **Human-Like Forgetting System (HLFS)**, a comprehensive forgetting system based on a variant of the Ebbinghaus forgetting curve. Building upon this, we have developed the **General Chat Box (GCB)**. The overall architecture of the model is illustrated in the following diagram:

<img src="misc/workflow.png" align="middle" width="95%">

#  ✨ Updates
- [**2024-06-08**] We have established an open-source repository for **HLFS** for the first time

# 🌐 Overview
HLFS is a comprehensive forgetting system with a range of functions including memory storage, data backup and recovery, and a recall mechanism. Powered by HLFS, GCB integrates gpt-3.5-turbo and boasts excellent dialogue processing capabilities.

The detailed project structure tree is as follows:

```markdown
HLFS/
├── box/ -- GCB
│   ├── box_demo.py
│   └── box_functions.py 
│
├── config/
│   └── config.py
│
├── core/
│   ├── forget/ -- Forgetting curve
│   ├── retrieve/ -- Memory retrieve methods
│   │   ├── con_sim.py
│   │   └── faiss.py
│   └── mem_struct.py -- Data structure for HLFS and GCB
│
├── data/ -- Datasets
│
├── eval/
│   ├── data/ -- Datasets of the critical dialogue retention=30%, 56%, 82%
│   │   ├── retention_30
│   │   ├── retention_56
│   │   └── retention_82
│   ├── image/ -- Results
│   ├── cal_metrics.py -- Benchmark
│   ├── cal_sim.py -- Similarity calculation
│   ├── curve.py -- Curve plotting
│   └── data_loader.py -- Loading the construction dataset
│
├── history/ -- Memory storage
│   └── bake/ -- Dataset of Retention=100%
│  
├── logs/
│
├── misc/ 
│
├── prompts/ 
│   └── prompts.py -- The prompts and correlation functions
│
├── utils/ 
│   ├── api.py
│   ├── log.py
│   └── tools.py
│
├── requirements.txt
│
└── README.md
│
└── second_derivative_integral.py -- Calculation of second derivative integration in the appendix
```
# 👨‍💻 Usage

## config

In `config/config.py`, Contains parameters related to HLFS and GCB. In addition, you need to put all your apiKeys into `openai_key` (especially if your apiKeys are restricted)

## Requirements

The key requirements are as below:

- python 3.9+
- openai 0.27.0+
- llama-index==0.5.17.post1
- transformers==4.28.0

## Installation

Step 1: Create a new conda environment:
```shell
conda create -n hlfs python=3.9 -y
conda activate hlfs
```

Step 2: Install relevant packages
```shell
pip install -r requirements.txt
```

## Run

We strive to make the process of experiencing the code as simple as possible.

### Construction Dataset
We provide a method for loading and constructing datasets, which is in `eval/data_loader.py`, You can change variable `data_dir` and `data_file` to select one.

But we have already helped complete this step, The constructed datasets under different retention rates are as follows:

- _R_=100%: `history/bake/`
- _R_=82%: `eval/data/retention_82`
- _R_=56%: `eval/data/retention_56`
- _R_=30%: `eval/data/retention_30`

you can directly transfer the constructed dataset to `history/` so that GCB can read directly from it:
```shell
mv history/bake/en/exercise/* history/
```
or:
```shell
mv eval/data/retention_82/en/exercise/* history/
```

### Dialogue with GCB
You can run this command to directly communicate with GCB:
```shell
cd box/
python box_demo.py \
    --language en \
    --history_path ../history \
    --test_model False \
    --ltm_box hlfs
```

We provide a quick overview of the arguments:

- `--language`: Choose language`['cn', 'en']`
- `--history_path`: Set the location for saving conversation history, user information, etc. **We strongly recommend that you keep the default** `../history`
- `--test_model`: Test mode, if you want to use the dataset provided in our paper for result validation, please set it to `True`. In this case, the Global Memory Table (GMT) will not be updated and your conversation process will not be saved. If you want to experience the complete GCB conversation service, please set it to `False`. You will experience the full functionality. 
- `--ltm_box`: We inherited two benchmarks`['hlfs', 'scm']`. For MemoryBank, please visit [MemoryBank-SiliconFriend](https://github.com/zhongwanjun/MemoryBank-SiliconFriend)

⚠️ Please note that dialogue with GCB does not require `/history` to be non-empty.

### Periodic trigger forgetting
```shell
cd core/
python timer.py \
    --test_model False \
    --time_gap 1 \
    --recall_times 1 \
    --forgetting_cycle 1 
```
Here:
- `--test_model`: If `True`, you need to set `--time_gap` and `--recall_times` by yourself; if `False`, you need to set `--forgetting_cycle`
- `--time_gap`: The time gap between the last recall and the present (test_model = True)
- `--recall_times`: recall times (test_model = True)
- `--forgetting_cycle`

⚠️ Please note that Periodic trigger forgetting does require /history to be non-empty.

### Evaluation stage
-`eval/cal_metrics.py`: Benchmark comparative experiment

-`eval/cal_sim.py`: Contextual Coherence, Topic Similarity.

-`second_derivative_integral.py`: Calculate the second derivative integral, as detailed in the appendix of the paper

📈 We have already run the program in advance and all the results have been accurately labeled in the dataset, Please refer to the code for specific usage details

# License

This project is released under the MIT license. Please see the [LICENSE](LICENSE) file for more information.