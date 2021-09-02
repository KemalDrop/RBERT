import os
import re
import csv
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SemEvalConverter:

    __seperator__ = {
                        "step": "STEPS",
                        "ingredient": "INGREDIENTS"   
                    }

    def from_tagtog():
        pass

    def from_inception(path:str, recipe_part:str = "step"):
        assert os.path.isdir(path), f"Given path is not a folder {path}"
        assert os.path.basename(path) == "annotation", ("Given folder should match the Inception export file",
                                                        f" ex: path/to/file/annotations/...")
        for dir_path, mid_path, files in os.walk(path):

            # TODO: assumes only one annotator can be converted to multiple annotators
            if not any(os.path.splitext(files)[-1] == ".semeval" for files in files) and len(files) > 0:
                # Check if there is another annotator than Nadia
                tsv_filtered = [f for f in files if os.path.splitext(f) == ".tsv"]
                if len(tsv_filtered) > 1:
                    print(f"More than one annotations detected {dir_path}")
                    continue
                tsv_file = tsv_filtered[0]
                # check tsv column length only once
                control = True
                format_index = None
                all_annotations_path, txt_file_name = os.path.split(dir_path)
                with open(os.path.join(dir_path, tsv_file)) as tsv, open(os.path.join(os.path.split(all_annotations_path)[0], "source", txt_file_name)) as txt_file:
                    part_cont = 0
                    sentence_count = 0
                    temp = []
                    entity_num = []
                    relation_info = {}
                    tsv_reader = csv.reader(tsv, delimiter = "\t")

                    for e, line in enumerate(tsv_reader): # gives lines as a list [["Line1"], ["Line2"], ...]
                        # For not writing if there is a trouble with the file
                        write = True
                        # Inception files should have a first line hard coded as ['#FORMAT=WebAnno TSV 3.3']
                        if e == 0 and not line[0].split("#FORMAT=")[-1] == "WebAnno TSV 3.3":
                            logger.info(f"The file given is not on inception format {tsv_file}")
                            break

                        if len(line) == 1:
                            identifier = line[0].split("|")
                            if len(identifier) > 1:
                                if "#T" in line[0] and "Relation" in identifier[-2]:
                                    relation_format_index = e + 3 # added two because the words are always at the second column and
                                                                  # the relations are e away from words
                                elif "#T" in line[0] and ("Entities" in identifier[-2] or "NERtags" in identifier[-2]):
                                    entity_format_index = e + 2 # same for entities

                        # Check if the format index of a file has been found
                        if not format_index:
                            logging.critical(f"Couldn't determine format index for file: {os.path.join(dir_path, tsv_file)}")
                            break

                        if line[2] == "\xa0":
                            continue

                        # sentence count will be bigger than 0 if the current line is under @@STEPS because it is checked and incremented there 
                        elif len(line) == 0 and sentence_count >= 1:
                            raw_sentence = txt_file[sentence_start:int(line[1].split("-")[-1])]
                            temp_dict = {}

                        if len(line) > 1:
                            # Check if @@STEPS part is starting
                            if line[2] == "@":
                                part_cont += 1
                            elif part_cont > 0 and line[2] == SemEvalConverter.__seperator__[recipe_part]:
                                part_cont += 1
                            elif 3 > part_cont > 0 and line[2] != SemEvalConverter.__seperator__[recipe_part]:
                                part_cont = 0
                        
                            if part_cont > 2: # which means we are in the steps section
                                if line[2] == " " and line[entity_format_index] != "_": # some spaces accidentally annotated as entities so neglect that
                                    continue
                            
                            # this controls just for the first sentence after the @@STEPS
                            if sentence_count == 0:
                                sentence_start = int(line[1].split("-")[0])
                                sentence_count += 1
                                temp_dict = {}

                            start, end = line[1].split("-")
                            temp_dict[line[0]] = {"start_end":[int(start), int(end)], "word":line[2]}

                            try:
                                if line[relation_format_index] != "_":
                                    entity_search = re.search("\[[^\]]*\]", line[entity_format_index])
                                    if entity_search:
                                        span = entity_search.span()
                                        entity_index = line[format_index][span[0]:span[1]]
                                        if entity_index not in entity_num:
                                            entity_num.append(entity_index)
                                            relation_span_start = int(start)
                            except:
                                pass



if __name__ == "__main__":
    SemEvalConverter.from_tagtog()