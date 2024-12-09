
# CallNavi

CallNavi is a dataset and tools designed to benchmark and enhance task routing and call optimization for large language models (LLMs). By utilizing advanced techniques and benchmark datasets, CallNavi enables efficient zero-shot task routing, facilitating better performance in multi-task environments.

## Features

- **Task Routing Test For LLMs**: 729 questions.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [TaskNavi Dataset](#tasknavi-dataset)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Etamin/CallNavi.git
cd CallNavi
pip install -r requirements.txt
```

Ensure you have Python 3.8+ and the necessary runtime environments for the LLMs.

---

## Usage

CallNavi can be easily integrated into your workflow:

### Quick Start

```bash
python3 predict.py
```

### Custom Configuration

```python
modelst=['modelNameInOllama1','modelNameInOllama2...']
# When using OpenAI
os.environ['OPENAI_API_KEY']=''
# When using OLLAMA
client = Client(host='http://:11434')
```

### Judge
```bash
python3 wash.py
python3 Judge_para.py
```
## TaskNavi Dataset

CallNavi includes the **TaskNavi** dataset, a benchmark designed for testing task-routing efficiency. The dataset covers:


### Accessing the Dataset

The dataset is available in the `Dataset/` directory. Load it using:

```python

```

---

## Examples



---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or feedback, feel free to create an issue on the repository or reach out to us at .

---

Let me know if you'd like to customize this further!
