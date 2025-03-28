import json
import copy
import string
from tqdm import tqdm
from typing import Any, Tuple

# --- Helper Functions for JSON Normalization and Comparison ---

def normalize_str(s: str) -> str:
    """
    Normalize a string by removing punctuation and whitespace,
    and converting it to uppercase.
    """
    translator = str.maketrans('', '', string.punctuation + string.whitespace)
    return s.translate(translator).upper()

def normalize_json(obj: Any) -> Any:
    """
    Recursively normalize a JSON-like object:
      - For dict: normalize keys (if string) and values (order of keys is ignored)
      - For list: normalize each element (order preserved)
      - For str: normalize using normalize_str()
      - For other types: leave unchanged
    """
    if isinstance(obj, dict):
        normalized = {}
        for key, value in obj.items():
            new_key = normalize_str(key) if isinstance(key, str) else key
            normalized[new_key] = normalize_json(value)
        return normalized
    elif isinstance(obj, list):
        return [normalize_json(item) for item in obj]
    elif isinstance(obj, str):
        return normalize_str(obj)
    else:
        return obj

def wildcard_compare(val1: Any, val2: Any) -> bool:
    """
    Recursively compare two normalized JSON values.
    If either value is the wildcard string "$$$", consider it a match.
    """
    if isinstance(val1, str) and val1 == "$$$":
        return True
    if isinstance(val2, str) and val2 == "$$$":
        return True

    if isinstance(val1, dict) and isinstance(val2, dict):
        if set(val1.keys()) != set(val2.keys()):
            return False
        for k in val1.keys():
            if not wildcard_compare(val1[k], val2[k]):
                return False
        return True

    if isinstance(val1, list) and isinstance(val2, list):
        if len(val1) != len(val2):
            return False
        unmatched = list(val2)
        for item1 in val1:
            found = False
            for i, item2 in enumerate(unmatched):
                if wildcard_compare(item1, item2):
                    found = True
                    del unmatched[i]
                    break
            if not found:
                return False
        return True

    return val1 == val2

def compare_json_with_wildcard(json_obj1: Any, json_obj2: Any) -> bool:
    """
    Compare two JSON objects by normalizing them and treating any value equal to "$$$" as a wildcard.
    """
    norm1 = normalize_json(json_obj1)
    norm2 = normalize_json(json_obj2)
    return wildcard_compare(norm1, norm2)

def replace_values_with_blank(obj: Any) -> Any:
    """
    Recursively replace all non-container values with "<BLANK>".
    (This is used to create a template version of the ground truth.)
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_dict[key] = replace_values_with_blank(value)
        return new_dict
    elif isinstance(obj, list):
        return [replace_values_with_blank(item) for item in obj]
    else:
        return "<BLANK>"

def convert_int_to_string(obj: Any) -> Any:
    """
    Recursively convert all int values in the object to strings.
    """
    if isinstance(obj, dict):
        return {key: convert_int_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_int_to_string(item) for item in obj]
    elif isinstance(obj, int):
        return str(obj)
    else:
        return obj

def transform_json(input_data: dict) -> Tuple[str, str]:
    """
    Given an input JSON (as a dict), returns a tuple of two JSON strings:
      1. A version with all non-container values replaced with "<BLANK>"
      2. A version with integer values converted to strings.
    """
    blank_version = replace_values_with_blank(input_data)
    int_string_version = convert_int_to_string(input_data)
    return json.dumps(blank_version), json.dumps(int_string_version)

def writefile(l, dct):
    with open(l + ".json", 'w') as file:
        file.write(json.dumps(dct, indent=2))

# --- A Simple Function to Generate a JSON Schema from a Template ---
def generate_json_schema(obj: Any) -> dict:
    """
    Recursively generate a JSON Schema for a given JSON-like object.
    This basic implementation infers types from the sample object.
    """
    if isinstance(obj, dict):
        properties = {}
        required = []
        for key, value in obj.items():
            properties[key] = generate_json_schema(value)
            required.append(key)
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    elif isinstance(obj, list):
        if obj:
            # Assume homogeneous items; use the schema of the first item.
            return {"type": "array", "items": generate_json_schema(obj[0])}
        else:
            return {"type": "array"}
    elif isinstance(obj, int):
        return {"type": "integer"}
    elif isinstance(obj, float):
        return {"type": "number"}
    elif isinstance(obj, bool):
        return {"type": "boolean"}
    else:
        return {"type": "string"}

# --- vLLM and Model Setup ---
from openai import OpenAI

model_name = "meta-llama/Llama-3.1-8B-Instruct"

# Set a prompt template (without forced <BLANK> markers)
prompt_template = (
    "Please fill the JSON template for API, and only output the completed unformatted JSON for the following question and templates:"
)

# --- Main Processing Loop ---
# List of dataset names (assumes JSON files are under ./Questions/)
datalst = ['bank', 'shopping', 'logistics', 'aviation', 'hospital', 'gov', 'hr', 'hotel', 'insurance', 'telecommunications']
import openai
import os
from sglang.test.test_utils import is_in_ci

if is_in_ci():
    from patch import launch_server_cmd
else:
    from sglang.utils import launch_server_cmd

from sglang.utils import wait_for_server, print_highlight, terminate_process

os.environ["TOKENIZERS_PARALLELISM"] = "false"


server_process, port = launch_server_cmd(
    "python -m sglang.launch_server --model-path meta-llama/Meta-Llama-3.1-8B-Instruct --host 0.0.0.0"
)

wait_for_server(f"http://localhost:{port}")
client = openai.Client(base_url=f"http://127.0.0.1:{port}/v1", api_key="None")


total_count = 0
total_match = 0
result = []

for data in datalst:
    with open("./Questions/" + data + ".json", 'r') as file:
        questions = json.load(file)
    count = 0
    match = 0
    for q in tqdm(questions, desc=f"Processing {data}"):
        # Work on a copy if needed
        qfinal = copy.deepcopy(q)
        # Process only questions marked as "easy"
        if q.get("difficulty") == "easy":
            count += 1
            tmp,gt=transform_json(q['ground_truth']['parameters'])
                
            temp=json.dumps(tmp)
            # Use the ground truth to derive a JSON schema.
            # (Optionally, you can also create a "blank" version.)
            # blank_version, _ = transform_json(q['ground_truth'])
            # Here we generate a schema from the ground truth object.
            schema = generate_json_schema(q['ground_truth']['parameters'])
            wait_for_server(f"http://localhost:{port}")

            # Construct the prompt: include the question and (optionally) a reference to the template.
            prompt = prompt_template + " " + q['question'][0]['content'] + "\n"+ temp
            client = openai.Client(base_url=f"http://127.0.0.1:{port}/v1", api_key="None")
            try:
                completion = client.chat.completions.create(
                    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0,
                    max_tokens=128,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "foo",
                            # convert the pydantic model to json schema
                            "schema": schema,
                        },
                    },
                )
                generated_json=completion.choices[0].message.content
            except Exception as e:
                generated_json=[]
            # Try to compare generated JSON with ground truth.
            try:
                out=json.loads(generated_json)
            except Exception as e:
                print("Error loading ground truth:", e)
                continue

            if compare_json_with_wildcard(generated_json, gt):
                match += 1
            else:
                print("Prediction mismatch:")
                print("Predicted:", generated_json)
                print("Ground Truth:", gt)
            result.append({"predict": generated_json, "ground_truth": gt})
    total_count += count
    total_match += match
    print(f"Dataset: {data}")
    print("Matched:", match)
    print("Total processed:", count)

print("Overall Results:")
print("Total matched:", total_match)
print("Total processed:", total_count)
writefile("result", result)
