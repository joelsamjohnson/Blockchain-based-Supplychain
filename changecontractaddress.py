import os
import sys
import argparse

def replace_in_file(file_path, old_address, new_address):
    with open(file_path, 'r', encoding='utf-8') as file:
        contents = file.read()

    contents = contents.replace(old_address, new_address)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(contents)

def replace_address_in_templates(directory, old_address, new_address, file_extension):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extension):
                file_path = os.path.join(root, file)
                replace_in_file(file_path, old_address, new_address)
                print(f'Replaced address in {file_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Replace Ethereum contract address in template files.')
    parser.add_argument('directory', type=str, help='The directory containing the template files.')
    parser.add_argument('old_address', type=str, help='The old contract address to be replaced.')
    parser.add_argument('new_address', type=str, help='The new contract address.')
    parser.add_argument('--ext', type=str, default='.html', help='File extension to search for (default: .html)')

    args = parser.parse_args()

    replace_address_in_templates(args.directory, args.old_address, args.new_address, args.ext)
