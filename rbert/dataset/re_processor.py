import os
import csv
import logging
from posixpath import splitext

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
        for file_tuple in os.walk(path):

            # TODO: assumes only one annotator can be converted to multiple annotators
            if all(os.path.splitext(files)[-1] == ".tsv" for files in file_tuple[-1]) and len(file_tuple[-1]) > 0:
                # Check if there is another annotator than Nadia
                if len([f for f in file_tuple[-1] if os.path.splitext(f) == ".tsv"]) > 1:
                    print(f"More than one annotations detected {file_tuple}")
                    continue
                
                # check tsv column length only once
                control = True
                format_index = None
                with open(os.path.join(file_tuple[0], file_tuple[-1][0])) as f:
                    part_cont = 0
                    temp = []
                    entity_num = []
                    tsv_reader = csv.reader(f, delimiter = "\t")

                    for e, line in enumerate(tsv_reader): # gives lines as a list [["Line1"], ["Line2"], ...]
                        # For not writing if there is a trouble with the file
                        write = True
                        # Inception files should have a first line hard coded as ['#FORMAT=WebAnno TSV 3.3']
                        if e == 0 and not line[0].split("#FORMAT=")[-1] == "WebAnno TSV 3.3":
                            logger.info(f"The file given is not on inception format {file_tuple[-1][0]}")
                            break

                        if len(line) == 1:
                            identifier = line[0].split("|")
                            if len(identifier) > 1:
                                if "#T" in line[0] and "Relation" in identifier[-2]:
                                    format_index = e + 3 # added two because the words are always at the second column and
                                                        # the entities are e away from words

                        if len(line) > 1:
                            # Check if the format index of a file has been found
                            if not format_index:
                                logging.critical(f"Couldn't determine format index for file: {os.path.join(file_tuple[0], file_tuple[-1][0])}")
                                break

                            if line[2] == "\xa0":
                                continue

                            # Check if @@STEPS part is starting
                            if line[2] == "@":
                                part_cont += 1
                            elif part_cont > 0 and line[2] == SemEvalConverter.__seperator__[recipe_part]:
                                part_cont += 1
                            elif 3 > part_cont > 0 and line[2] != SemEvalConverter.__seperator__[recipe_part]:
                                part_cont = 0
                        
                            if part_cont > 2: # which means we are in the steps section
                                if line[2] == " " and line[format_index] != "_": # some spaces accidentally annotated as entities so neglect that
                                    continue
                                try:
                                    if line[format_index] != "_":
                                        pass
                                except:
                                    pass



if __name__ == "__main__":
    SemEvalConverter.from_tagtog()