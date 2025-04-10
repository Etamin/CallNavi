# CallNavi

**CallNavi** is a benchmark suite and toolkit designed to evaluate and enhance the capabilities of Large Language Models (LLMs) in handling function calling, routing, and invocation tasks. This project focuses on assessing models' abilities to select appropriate APIs, generate accurate parameters, and manage nested API calls, particularly in complex, multi-step scenarios.

## Overview

Interacting with software systems via chatbots often requires the generation of API calls with correct sequencing and parameterization. CallNavi addresses this challenge by:

- Introducing a novel dataset tailored for evaluating API function selection, parameter generation, and nested API calls.
- Benchmarking state-of-the-art LLMs across varying levels of complexity to assess their performance in API function generation and parameter accuracy.
- Proposing an enhanced API routing method that combines general-purpose LLMs for API selection supplemented by prompt engineering techniques.

These approaches aim to improve the handling of complex API tasks, offering practical advancements for real-world API-driven chatbot systems.

For a comprehensive understanding, please refer to our [arXiv paper](https://arxiv.org/abs/2501.05255).

## Features

- **Task Routing Evaluation**: A set of 729 questions designed to test LLMs' capabilities in API function selection and parameter generation.
- **Benchmarking Tools**: Scripts and utilities to facilitate the evaluation of LLMs on the provided dataset.

## Repository Structure

- `Agent_Routers_Test/`: Contains test cases for agent routing scenarios.
- `Dataset/`: Includes the dataset used for benchmarking.
- `YAML/`:  Files for different input/output formats.
- `APIOnly.py`: The script focuses on API selection-only interactions.
- `Asyn.py`: Implements asynchronous generation prompt optimization.
- `Backward.py`: Implements backward thinking prompt optimization.
- `Data_statistics.py`: Provides statistical analysis of the dataset.
- `Judge_call.py`: Evaluates the correctness of API call selections.
- `Judge_para.py`: Evaluates the correctness of API generated with parameters.
- `predict.py`: Main script for running predictions.
- `requirements.txt`: Lists the dependencies required for the project.
- `wash.py`: Utility script for data preprocessing.


## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Etamin/CallNavi.git
   cd CallNavi
   ```

2. **Install Dependencies**:
   Ensure you have Python 3 installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To evaluate an LLM using the CallNavi benchmark:

1. **Prepare the Model**: Ensure your model is accessible and compatible with the scripts provided.

2. **Run Predictions**:
   ```bash
   python predict.py --model_path path_to_your_model
   ```

3. **Evaluate Results**:
   ```bash
   python Judge_call.py --predictions path_to_predictions
   python Judge_para.py --predictions path_to_predictions
   ```

Replace `path_to_your_model` and `path_to_predictions` with the appropriate paths.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request if you have suggestions or improvements. For significant changes, consider opening an issue first to discuss your ideas.

## License

This project is licensed under the MIT License. 

---

*For detailed methodologies and experimental results, please refer to our [arXiv paper](https://arxiv.org/abs/2501.05255).*
```

Feel free to integrate this `README.md` into your repository. Let me know if you need further assistance or modifications! 
