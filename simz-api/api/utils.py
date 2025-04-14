import os
import json
from collections import defaultdict
from pydantic import ValidationError
from .componentT import ComponentRegisterType

def load_regcomp_data():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dir_locate = os.path.join(project_dir, "../../test/compTest/")
    dir_locate = os.path.abspath(dir_locate)  # Get absolute path
    # dir_locate = 'home/antiloger/Projects/SimZ/SimZ_GUI/test/compTest/'
    data_dict = defaultdict(lambda: defaultdict(dict))

    if not os.path.exists(dir_locate):
        print(f"Directory not found: {dir_locate}")
    else:
        print(f"Loading files from: {dir_locate}")

    for root, _, files in os.walk(dir_locate):
        for file in files:
            if file == "registerdata.json":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)
                        valid_data = ComponentRegisterType.model_validate(data)
                        category = valid_data.category
                        comp_type = valid_data.typeName
                        data_dict[category][comp_type] = valid_data.model_dump()

                except (json.JSONDecodeError, IOError, ValidationError) as e:
                    print(f"Error loading file {file_path}", e)

    return data_dict
