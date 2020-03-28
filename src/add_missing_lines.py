import argparse
import os

import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src.read_localization_file import file_to_keys_and_lines, get_key_value_and_version, BadLocalizationException


def get_args():
    parser = argparse.ArgumentParser(description='Add missing lines to translation files')
    parser.add_argument('source_dir', type=str, help='Directory with source Paradox files')
    parser.add_argument('dest_dir', type=str, help='Directory with destination Paradox files')
    parser.add_argument('-source_lang', type=str, help='Source language when EUIV, HoI4 or Stellaris game')
    parser.add_argument('-dest_lang', type=str, help='Destination language when EUIV, HoI4 or Stellaris game')
    return parser.parse_args()


def add_missing_lines_one_file(source_file_path, dest_file_path, old_lines_file_path):
    dest_texts, dest_first_line = file_to_keys_and_lines(dest_file_path)

    with open(source_file_path, 'r', encoding='utf8') as f:
        source_lines = f.readlines()

    with open(dest_file_path, 'w', encoding='utf8') as f:
        for i in range(len(source_lines)):
            if i == 0:
                f.write(dest_first_line)
            else:
                try:
                    key, value, version = get_key_value_and_version(source_lines[i])
                except BadLocalizationException:
                    f.write(source_lines[i])
                    continue
                if key in dest_texts:
                    f.write(dest_texts[key])
                    del dest_texts[key]
                else:
                    dest_version = '' if version is None else str(version)
                    f.write(' ' + key + ':' + str(dest_version) + ' "' + value + '"\n')
    with open(old_lines_file_path, 'a', encoding='utf8') as f:
        for dest_line in dest_texts.values():
            f.write(dest_line)


def add_missing_lines_imperator(source_dir, dest_dir):
    """
    Add missing lines for Imperator Rome or sooner games
    :param dest_dir:
    :param source_dir:
    :return:
    """
    rel_to_dest_abs_path = dict()
    for root, _, files in os.walk(dest_dir):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            rel_to_dest_abs_path[abs_path[:abs_path.find('_l_')].replace(dest_dir, '')] = abs_path
    for root, _, files in os.walk(source_dir):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            rel_path = abs_path[:abs_path.find('_l_')].replace(source_dir, '')
            if rel_path not in rel_to_dest_abs_path:
                print(f'File {rel_path} doesn\'t exists for destination language')
            else:
                add_missing_lines_one_file(abs_path, rel_to_dest_abs_path[rel_path],
                                          os.path.abspath(os.path.join(dest_dir, '..', 'old_lines.yml')))


def add_missing_lines_eu_hoi_stellaris(source_dir, source_lang, dest_lang):
    """
    Add missing lines for EUIV, HoI4 or Stellaris
    :param source_dir:
    :param source_lang:
    :param dir_lang:
    :return:
    """
    rel_to_dest_abs_path = dict()
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(dest_lang + '.yml'):
                abs_path = os.path.abspath(os.path.join(root, file))
                rel_to_dest_abs_path[abs_path[:abs_path.find('_l_')].replace(source_dir, '')] = abs_path
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(source_lang + '.yml'):
                abs_path = os.path.abspath(os.path.join(root, file))
                rel_path = abs_path[:abs_path.find('_l_')].replace(source_dir, '')
                if rel_path not in rel_to_dest_abs_path:
                    print(f'File {rel_path} doesn\'t exists for destination language')
                else:
                    add_missing_lines_one_file(abs_path, rel_to_dest_abs_path[rel_path],
                                              os.path.abspath(os.path.join(source_dir, '..', 'old_lines.yml')))

if __name__ == '__main__':
    args = get_args()
    if (args.source_lang is None) and (args.dir_lang is None):
        add_missing_lines_imperator(args.source_dir, args.dest_dir)
    else:
        add_missing_lines_eu_hoi_stellaris(args.source_dir, args.source_lang, args.dest_lang)
