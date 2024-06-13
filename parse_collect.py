import os
import re
import json
from collections import defaultdict
import argparse

## use example
## python3 parse_collect.py 

# Parse command line arguments.
parser = argparse.ArgumentParser(description='parse all the json files from the source folder and save them as a jsonl file which serves as the test data')
parser.add_argument('nejm_case_unzip_json', type=str, help='path to the unzip NEJM cases in json format.')
args = parser.parse_args()


## combine all in one loop in a function
def parse_data(json_data):
    # indicator for presentation of case
    found_start_poc = False
    found_end_poc = False
    presention_case = ""
    # indicator for differential diagnosis
    found_start_dd = False
    found_start_ddc = False
    differential_diagnosis = defaultdict(list)
    found_end_dd = False
    found_end_ddc = False

    # indicator for diagnosis options
    found_start_drd = False
    drs_diagnosis = ''
    found_end_drd = False
    # indicator for final diagnosis
    found_start_fd = False
    final_diagnosis = ''
    found_end_fd = False


    for element in json_data["elements"]:
        try:
            ##################
            ## ID and Title ##
            ##################
            ## retrieve id/title 
            if element["TextSize"] == 18:
                title_line= element["Text"]
                year = title_line.split(":")[0].lower().strip().split(" ")[-1].strip().split("-")[-1].strip()
                case_num =  title_line.split(":")[0].lower().strip().split(" ")[-1].strip().split("-")[0].strip().zfill(2)
                id = f"nejm-case-{year}-{case_num}"
                title =  title_line.split(":")[1].strip()
                # print(title_line)

            ##########################
            ## presentation of case ##
            ##########################
            # after the id and title
            # loop through all the elements start with textsize 10.5 and text = 'presentation of case'
            # sub title text size 10.5 (2 exceptions: 2011-29， 2011-30)
            if not found_start_poc and \
                element["TextSize"] in [10.5,9] and \
                    element["Text"].lower().strip() == "presentation of case":
                found_start_poc = True
            # text size 10
            if found_start_poc and element["TextSize"] == 10 : 
                presention_case += element["Text"]
            # stop when reach the next subtitle (size 10.5)
            if found_start_poc and \
                element["TextSize"] in [10.5,9] and \
                element["Text"].lower().strip() != "presentation of case":
                found_start_poc = False
                found_end_poc = True

            ###########################
            ## differential dignosis ##
            ###########################
            # after the presentation of cases
            # loop through all the elements start with textsize 10.5 and text = 'presentation of case'
            # sub title text size 10.5
            # start to look for differential diagnosis
            if not found_start_dd and \
                found_end_poc and \
                    element["TextSize"] == 10.5 and \
                        element["Text"].lower().strip() == "differential diagnosis":
                found_start_dd = True
            
            # reach the next first subtitle, size 9
            # "LineHeight" in element["attributes"].keys() and element["attributes"]["LineHeight"] in [10.5, 10.75] and \
            if found_start_dd and element["TextSize"] == 9 and \
                element["Font"]["name"].lower().strip().endswith("bold") and \
                    "LineHeight" in element["attributes"].keys() and element["attributes"]["LineHeight"] in [10.5, 10.75]:
                first_subtitle = element["Text"].strip()
                differential_diagnosis[first_subtitle] = []
                found_start_ddc = True
            
            # reach the next second subtitle, size 9.5
            if found_start_dd and found_start_ddc and \
                element["TextSize"] == 9.5 and \
                    element["Font"]["name"].lower().strip().endswith("italic"):
                second_subtitle = element["Text"].strip()
                differential_diagnosis[first_subtitle].append(second_subtitle)


            # stop when reach the next subtitle (size 10.5), differential diagnosis exist
            if found_start_dd and \
                element["TextSize"] == 10.5 and \
                    element["Text"].lower().strip() != "differential diagnosis":
                found_start_dd = False
                found_start_ddc = False
                found_end_dd = True
                found_end_ddc = True

            # # stop when reach the next subtitle (size 10.5), differential diagnosis not exist
            if (found_start_dd == False) and \
                (found_end_dd == False) and \
                    element["TextSize"] == 10.5 and \
                        element["Text"].lower().strip() != "differential diagnosis":
                found_start_dd = False
                found_start_ddc = False
                found_end_dd = True
                found_end_ddc = True


            ####################
            ## dr's diagnosis ##
            ####################
            # after the differential diagnosis
            # loop through all the elements start with textsize 10.5 and with the word 'diagnosis' in the text
            if  found_end_dd and \
                element["TextSize"] == 10.5 and \
                    element["Text"].lower().strip() != "final diagnosis" and \
                        re.search('diagnos', element["Text"].lower().strip()) and \
                            element["Text"].lower().strip().startswith("dr."):  
                found_start_drd = True

            if found_start_drd and element["TextSize"] == 10 :
                drs_diagnosis += element["Text"]

            # stop when reach the next subtitle (size 10.5)
            if found_start_drd and \
                element["TextSize"]  == 10.5 and \
                        (not element["Text"].lower().strip().startswith("dr.")):
                # add begining_dd to the dict
                found_start_drd = False
                found_end_drd = True

            # # stop when reach the next subtitle (size 10.5), dr's diagnosis not exist
            if (found_start_drd == False) and \
                (found_end_drd == False) and \
                    element["TextSize"] == 10.5 and \
                        (not element["Text"].lower().strip().startswith("dr.")):
                # add begining_dd to the dict
                found_end_drd = True

            ####################
            ## Final dignosis ##
            ####################
            # after the presentation of cases
            # loop through all the elements start with textsize 10.5 and text = 'presentation of case'
            # sub title text size 10.5
            if not found_start_fd and \
                element["TextSize"] == 10.5 and \
                    element["Text"].lower().strip() in ["final diagnosis","final diagnoses"]:
                found_start_fd = True
            # text size 10
            if found_start_fd and element["TextSize"] == 10 : 
                final_diagnosis += element["Text"]
            # stop when reach the next subtitle (size 10.5)
            if found_start_fd  and element["TextSize"] == 10.5 and \
                element["Text"].lower().strip() not in ["final diagnosis","final diagnoses"]:
                found_start_fd = False
                found_end_fd = True

        except:
            pass

    if final_diagnosis == '':
        final_diagnosis_comb = drs_diagnosis
    else:
        final_diagnosis_comb = final_diagnosis


    return {
        "source": "NEJM case records of the massachusetts general hospital",
        "year": year,
        "case_num": case_num,
        "id": id,
        "title": title,
        "presentation_of_case": presention_case,
        "differential_diagnosis": differential_diagnosis,
        "drs_diagnosis": drs_diagnosis,
        "final_diagnosis": final_diagnosis,
        "final_diagnosis_comb": final_diagnosis_comb
    }





def process_json_files(source_folder, output_file):

    # List of all parsed records
    n_processed = 0
    all_parsed_records = []
    exception_files = []

    # Loop through all the files in the source folder
    for filename in os.listdir(source_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(source_folder, filename)
            print(f'Processing file: {file_path}, {n_processed} files processed.')
            
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Apply the parsing function to the data
            try:
                parsed_data = parse_data(data)
                n_processed += 1
            except:
                print(f"Finding exceptions: {filename}")
                exception_files.append(filename)
                continue
            
            # Append the parsed data to the list
            all_parsed_records.append(parsed_data)

    # Write the parsed data to a JSONL file
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in all_parsed_records:
            json_record = json.dumps(record, ensure_ascii=False)
            f.write(json_record + '\n')

    # Write the exception files to a file
    with open('exception_files.txt', 'w') as f:
        for file in exception_files:
            f.write(file + '\n')


# Specify the source folder and the output JSONL file path
# source_folder = '/Users/yuntian/Desktop/Yale/PhD/Year1/Semester2/Rotation3/DiagnosticReasoning/testDataNEJM/pdfExtract/NEJM_case_json_unzip/'
source_folder = args.nejm_case_unzip_json
output_file = 'NEJM_case_test.jsonl'

# Call the function
process_json_files(source_folder, output_file)
