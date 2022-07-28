# remove empty files
# remove numbers from file name

import os
import re
import models.file_model as models
# import json
import commentjson
import utils.utils as utils

class CleanService:
    def __init__(self, dataset_location: str) -> None:
        self.dataset_location = dataset_location

    def __get_files(self) -> list[str]:
        ret: list[str] = []
        for path in os.listdir(self.dataset_location):
        # check if current path is a file
            if os.path.isfile(os.path.join(self.dataset_location, path)):
                ret.append(path)

        return ret

    # clean names, remove empty files and convert json to text
    def get_file_models(self) -> list[list[models.FileModel], list[str]]:
        files = self.__get_files()

        ret: list[models.FileModel] = []
        failed_list: list[str] = []

        tot_files = len(files)
        files_processed = 0 
        utils.print_progress_bar(files_processed, tot_files, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for file_path in files:
            files_processed += 1
            utils.print_progress_bar(files_processed, tot_files, prefix = f'Progress:', suffix = 'Complete', length = 50)
            # print(file_path,'\n')
            file = open(os.path.join(self.dataset_location, file_path), "r", encoding='utf-8')
            try:
                file_content = file.read()
            except:
                print(f'Not able to read file {file}')
                failed_list.append(file_path)
                ret.append(models.FileModel(filename=clean_name, json_content=None, location=file_path))
                continue

            if (file_content.strip() != ''):
                clean_name = self.remove_numbers_from_string(file_path)
                file.seek(0)

                try:
                    _ = commentjson.load(file)
                    json_content: str = self.extract_words_from_json_string(json_str=file_content)
                    ret.append(models.FileModel(filename=clean_name, json_content=json_content, location=file_path))
                except:
                    failed_list.append(file_path)
                    print(f'Not able to load json file {file}')
                    ret.append(models.FileModel(filename=clean_name, json_content=None, location=file_path))

        return [ret, failed_list]

    def remove_numbers_from_string(self, inp_string: str) -> str:
        return ''.join([i for i in inp_string if not i.isdigit()])

    def extract_words_from_json_string(self, json_str: str) -> str:
        symbols_to_remove = ['{', '}', '"', ":", ",", '[', ']']
        big_regex = re.compile('|'.join(map(re.escape, symbols_to_remove)))
        ret = big_regex.sub(" ", json_str).strip()

        return ' '.join(ret.split())

