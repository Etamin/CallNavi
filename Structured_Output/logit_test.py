from transformers import AutoTokenizer, AutoModelForCausalLM, LogitsProcessor, LogitsProcessorList
import transformers
import torch
import json
import copy
from typing import Any, Tuple
from tqdm import tqdm
import string
model_name = "meta-llama/Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name,device_map="auto")
model = AutoModelForCausalLM.from_pretrained(model_name,device_map="auto",torch_dtype=torch.float16)

if '<BLANK>' not in tokenizer.get_vocab():
    tokenizer.add_special_tokens({'additional_special_tokens': ['<BLANK>']})
    model.resize_token_embeddings(len(tokenizer))
transformers.logging.set_verbosity_error()
prompt_template = """Please fill the JSON template for API, and only output the completed unformatted JSON for the following question:'"""


datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']
def writefile(l,dct):
    stra=json.dumps(dct)
    file=open(l+".json",'w')
    file.write(stra)
    file.close()


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
    # If either value is the wildcard string, they match.
    if isinstance(val1, str) and val1 == "$$$":
        return True
    if isinstance(val2, str) and val2 == "$$$":
        return True

    # If both are dicts, compare keys (order ignored) and then values.
    if isinstance(val1, dict) and isinstance(val2, dict):
        if set(val1.keys()) != set(val2.keys()):
            return False
        for k in val1.keys():
            if not wildcard_compare(val1[k], val2[k]):
                return False
        return True

    # If both are lists, compare ignoring order.
    if isinstance(val1, list) and isinstance(val2, list):
        if len(val1) != len(val2):
            return False
        # Create a copy of list2 items to track matches.
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

    # Otherwise, compare using equality.
    return val1 == val2

def compare_json_with_wildcard(json_obj1: Any, json_obj2: Any) -> bool:
    """
    Compare two JSON objects (or Python dicts) by normalizing them (ignoring object order, case,
    punctuation, and whitespace) and treating any value equal to "$$$" as a wildcard match.
    """
    norm1 = normalize_json(json_obj1)
    norm2 = normalize_json(json_obj2)
    return wildcard_compare(norm1, norm2)

def replace_values_with_blank(obj: Any) -> Any:
    """
    Recursively replace all non-container values with "<BLANK>",
    except for the key "API" where, if its value is a list,
    we keep its first element unchanged.
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            if key == "API" and isinstance(value, list):
                # Keep the first element as is (if exists), blank out the rest.
                if value:
                    new_list = [value[0]]
                    # For any additional elements, process recursively.
                    for elem in value[1:]:
                        new_list.append(replace_values_with_blank(elem))
                    new_dict[key] = new_list
                else:
                    new_dict[key] = value
            else:
                new_dict[key] = replace_values_with_blank(value)
        return new_dict
    elif isinstance(obj, list):
        return [replace_values_with_blank(item) for item in obj]
    else:
        # For any primitive value, return the blank token.
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
      1. All values replaced with "<BLANK>" (except the first API value remains unchanged)
      2. All integer values are converted to strings (other values unchanged)
    """
    blank_version = replace_values_with_blank(input_data)
    int_string_version = convert_int_to_string(input_data)
    
    # Return the JSON strings (optionally with indent=2 for readability)
    return json.dumps(blank_version), json.dumps(int_string_version)


# 6. Implement a custom logits processor.
#    It works as a state machine:
#     - While in "forced mode," it forces tokens from the current fixed segment.
#     - When not forcing, it lets the model generate freely (filling the blanks).
#     - When the generated token matches the expected token from the next forced segment,
#       it switches back to forced mode.
class TemplateFillingProcessor(LogitsProcessor):
    def __init__(self, prompt_length, forced_segments):
        self.prompt_length = prompt_length  # length (in tokens) of the prompt only
        self.forced_segments = forced_segments  # list of fixed segments (list of token ids)
        self.current_segment = 0  # index in forced_segments we are enforcing
        self.segment_pos = 0      # position within the current forced segment
        self.in_forced_mode = True  # start by enforcing the first fixed segment

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        current_length = input_ids.shape[1]

        # Do not interfere with the prompt.
        if current_length <= self.prompt_length:
            return scores

        # In forced mode, we want to force tokens from the current fixed segment.
        if self.in_forced_mode:
            segment = self.forced_segments[self.current_segment]
            # If we've already generated some tokens in this segment, check if they match.
            if self.segment_pos < len(segment):
                # Check the last generated token.
                last_generated = input_ids[0, current_length - 1].item()
                expected = segment[self.segment_pos]
                if last_generated == expected:
                    self.segment_pos += 1
                    # If we've finished the current fixed segment, switch to free mode.
                    if self.segment_pos >= len(segment):
                        self.in_forced_mode = False
            # If still in forced mode, force the next token.
            if self.in_forced_mode and self.segment_pos < len(segment):
                target_token_id = segment[self.segment_pos]
                forced_scores = torch.full_like(scores, -float('inf'))
                forced_scores[:, target_token_id] = scores[:, target_token_id] + 1000.0
                return forced_scores
            # Otherwise, exit forced mode.
            self.in_forced_mode = False

        # In free mode (for the blank), let the model generate freely.
        # But check if the generated output appears to start the next fixed segment.
        if not self.in_forced_mode:
            # If there is a next fixed segment to enforce...
            if self.current_segment < len(self.forced_segments) - 1:
                next_segment = self.forced_segments[self.current_segment + 1]
                # Check if the last generated token matches the first token of the next fixed segment.
                last_generated = input_ids[0, current_length - 1].item()
                if last_generated == next_segment[0]:
                    # Transition to forcing the next segment.
                    self.current_segment += 1
                    self.segment_pos = 1  # the first token is already generated
                    self.in_forced_mode = True
                    # Force the next token if available.
                    if self.segment_pos < len(next_segment):
                        target_token_id = next_segment[self.segment_pos]
                        forced_scores = torch.full_like(scores, -float('inf'))
                        forced_scores[:, target_token_id] = scores[:, target_token_id] + 1000.0
                        return forced_scores
        return scores

total_count=0
total_match=0
result=[]
for data in datalst:

        with open("./Questions/"+data+".json", 'r') as file:
            question = json.load(file)
        count=0
        match=0
        for q in tqdm(question):
            qfinal=copy.deepcopy(q)
            if q["difficulty"]=="easy":
                count+=1
                tmp,gt=transform_json(q['ground_truth'])
                
                temp=json.dumps(tmp)+"\n<|end_of_text|>"
                prompt=prompt_template+"'"+q['question'][0]['content']+"'; The JSON template is: "+temp
                input_ids = tokenizer.encode(prompt, return_tensors='pt')
                attention_mask = torch.ones_like(input_ids)
                segments = temp.split("<BLANK>")
                # Convert each fixed segment to token IDs.
                forced_segments = [tokenizer.encode(seg, add_special_tokens=False) for seg in segments]
                prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
                processor = TemplateFillingProcessor(prompt_length=len(prompt_ids), forced_segments=forced_segments)
                logits_processor = LogitsProcessorList([processor])
                # 8. Generate output.
                # Set max_length to cover the prompt and enough tokens for the filled template.
                max_length = len(input_ids[0]) + 128
                device = torch.device("cuda")
                input_ids = input_ids.to(device)
                attention_mask = attention_mask.to(device)
                outputs = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    logits_processor=logits_processor,
                    max_length=max_length,
                    do_sample=True,       # Use sampling to let blanks be generated freely.
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=[128001, 128009]
                )

                # 9. Decode and extract the filled template (remove the prompt).
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Remove the prompt and the following space.

                filled_template = generated_text[len(prompt.replace('<BLANK>','').replace('<|end_of_text|>',"")):].strip()
                try:
                    out=json.loads(filled_template)
                except:
                    continue

                if compare_json_with_wildcard(out,gt):
                    match+=1
                else:
                    print(out)
                    print(gt)
                result.append({"predict":out,"ground_truth":gt})

        total_count+=count
        total_match+=match
        print(data)
        print(match)
        print(count)
print("all")
print(total_match)
print(total_count)
writefile("result",result)