"""
Run: $ python flatten_json.py input_file output_folder
to flatten the JSON in input_file into separate files in output_folder.
"""

import argparse
import collections
import json
import os
import pprint

FILE_NAME_PREFIX = "___"
ID_KEY = "id"
INDEX_KEY = "__index"

def read_json_file(file_name):
    with open(file_name) as f:
        return json.loads(f.read())

# Extends base with new, where both are collections.defaultdict(list).
def extend_flattened_json(base, new):
    for key, val in new.items():
        base[key].extend(val)

# Flattens json_data by building a flat mapping between "nested JSON name" ->
# "list of JSON objects".
def get_flattened_json(json_data, id="", prefix=FILE_NAME_PREFIX, indices=None):
    # Initialize flattened with id and indices
    id = json_data.get(ID_KEY, id)
    flattened = collections.defaultdict(list)
    flattened[prefix] = [{ID_KEY: id}]
    if indices:
        flattened[prefix][0][INDEX_KEY] = indices
    else:
        indices = []
    # Helper to add nested to flattened.
    def add_nested_json(nested, new_prefix, new_indices):
        new = get_flattened_json(nested, id, new_prefix, new_indices)
        extend_flattened_json(flattened, new)
    # Flatten the nested jsons recursively as well as adding the primitive
    # types directly to flattened.
    for key, val in json_data.items():
        new_prefix = prefix + "_" + key
        if isinstance(val, dict):
            add_nested_json(val, new_prefix, indices)
        elif isinstance(val, list) and val and isinstance(val[0], dict):
            for i, nested in enumerate(val):
                add_nested_json(nested, new_prefix, indices + [i])
        else:
            flattened[prefix][0][key] = val
    return flattened

# Writes a new file in output_folder for every nested JSON object in flattened.
def write_output_files(flattened, output_folder):
    for file_name, json_data in flattened.items():
        # Every valid file_name will start with FILE_NAME_PREFIX + "_" because
        # the initial prefix is FILE_NAME_PREFIX and every valid prefix is 
        # built like 'new = old + "_" + key'.
        if not file_name.startswith(FILE_NAME_PREFIX + "_"):
            continue
        file_name = os.path.join(output_folder, 
                                 file_name[len(FILE_NAME_PREFIX)+1:] + ".json")
        with open(file_name, 'w') as outfile:
            json.dump(json_data, outfile)

# Reads input_file, flattens the nested JSON objects, then writes them to
# output_folder.
def main(input_file, output_folder):
    json_data = read_json_file(input_file)
    flattened = get_flattened_json(json_data)
    write_output_files(flattened, output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str,
                        help="The input JSON file.")
    parser.add_argument("output_folder", type=str,
                        help="The folder to write the flattened JSON files.")
    args = parser.parse_args()
    main(args.input_file, args.output_folder)