import os
from pathlib import Path
import subprocess
from argparse import ArgumentParser
import json
from datetime import datetime, timedelta
from tqdm import tqdm

def get_filepaths(dir):
    filepaths = []
    for filename in os.listdir(DIR):
        ext = filename.split('.')[-1]
        if ext in ['MP4']:
            filepaths.append(Path(filename).resolve())
    return filepaths

def change_creation_time(path):
    GET_METADATA_COMMAND = [
        'ffprobe',
        '-v',
        'quiet',
        str(path),
        '-print_format',
        'json',
        '-show_entries',
        'format_tags=creation_time'
    ]
    result = subprocess.check_output(GET_METADATA_COMMAND)
    result = result.decode('utf-8')
    result = json.loads(result)
    creation_time = result['format']['tags']['creation_time']
    creation_time = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    fixed_creation_time = creation_time + TIME_INCREASE
    formatted_fixed_creation_time = fixed_creation_time.strftime('%Y-%m-%d %H:%M:%S')
    input_name = path.parts[-1]
    output_name = input_name.split('.')[0] + '_fixed.' + input_name.split('.')[-1]
    output_path = path.parent / output_name
    SET_METADATA_COMMAND = [
        'ffmpeg',
        '-v',
        'quiet',
        '-i',
        str(path),
        '-metadata',
        f'creation_time={formatted_fixed_creation_time}',
        '-codec',
        'copy',
        str(output_path)
    ]
    return subprocess.call(SET_METADATA_COMMAND)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dir')
    parser.add_argument('--minutes-increase', type=int, required=True)
    args = parser.parse_args()

    DIR = Path(args.dir).resolve()
    TIME_INCREASE = timedelta(minutes=args.minutes_increase)

    filepaths = get_filepaths(DIR)

    for path in tqdm(filepaths):
        return_code = change_creation_time(path)
        if return_code != 0:
            print(f'FAILURE: {path}')
