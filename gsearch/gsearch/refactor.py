import json
import os
import argparse
from spiders import DATA_FOLDER


def format_file(file, json_file):
    data = []
    UNFORMATTED_JSON_FILE = os.path.join(DATA_FOLDER, file)
    with open(UNFORMATTED_JSON_FILE, 'r') as fp:
        for line in fp:
            line_json = json.loads(line)
            if line_json not in data:
                data.append(line_json)

    FORMATTED_JSON_FILE = os.path.join(DATA_FOLDER, json_file)
    with open(FORMATTED_JSON_FILE, 'w') as fp:
        fp.write(json.dumps(data, indent=4))


def format_company():
    return format_file('company.jl', 'formatted_company.json')


def format_hotels():
    return format_file('hotels.jl', 'formatted_hotels.json')


if __name__ == '__main__':
    print("Warning, if there was an original file here, it would be deleted")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "category",
        help="Pick between `hotel` or `company` ",
        type=str)
    args = parser.parse_args()

    if args.category == 'hotel':
        format_hotels()
    elif args.category == 'company':
        format_company()
    else:
        raise Exception(
            "Invalid or No input, choose between `hotel` or `company`"
        )
