import csv
import json
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from fetcher import FetcherActions

def main():
    #url = f'https://supremedecisions.court.gov.il/Home/Download?path={line["file_path"]}&fileName={line["file_name"]}&type=2'
    case_to_debug = 2758
    debug_a_case = False

    source_year = 2018
    source_month = "01"
    source_directory = str(source_year) + "." + source_month
    months = {"01" : "January",
              "02": "February",
              "03": "March",
              "04": "April",
              "05": "May",
              "06": "June",
              "07": "July",
              "08": "August",
              "09": "September",
              "10": "October",
              "11": "November",
              "12": "December",
              }
    month = months[source_month]
    file_name = month + " " + str(source_year) + ".csv"
    my_dict = __restart_dict()
    with open(file_name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, my_dict.keys())
        writer.writeheader()
    chrome_options = Options()
    if not debug_a_case:
        chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    fetcher = FetcherActions(driver)
    # TODO: add dynamic file name from command line
    directory = source_directory
    for filename in os.listdir(directory):
        # print("*****Reading file: " + filename + " *****")
        with open(directory +"/" + filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                json_data = json.loads(line)
                url = f'https://supremedecisions.court.gov.il/Home/Download?path={json_data["Path"]}&fileName={json_data["FileName"]}&type=2'
                case_name_from_json = json_data["CaseName"]
                case_type_from_json = json_data["Type"]
                verdict_date_from_json = json_data["VerdictsDtString"]
                case_number_from_json = json_data["CaseNum"]
                if debug_a_case:
                    if case_number_from_json != case_to_debug:
                        continue
                case_year_from_json = json_data["Year"]

        #    for row in reader:
            # TODO: add wait for page load
                my_dict = __restart_dict()
                fetcher.navigate_to_web_page(url)
                error_text = "The resource cannot be found"
                if error_text in driver.title:
                    break
                case_name_title = fetcher.fetch_case_name_title()
                # print("*****case_id*****")
                # print(case_id)

                my_dict["caseId"] = str(case_number_from_json) + "/" + str(abs(case_year_from_json) % 100)
                my_dict["ISCD_ID"] = str(abs(case_year_from_json) % 100) + str(case_number_from_json).zfill(5)
                my_dict["caseName"] = case_name_from_json
                my_dict["caseCitation"] = case_name_title + " " + case_name_from_json
                my_dict["url"] = url
                column = "Merged"
                merged_cases_num = fetcher.fetch_merged_cases_number()
                if merged_cases_num > 0:
                    my_dict[column] = str(merged_cases_num)
                else:
                    my_dict[column] = ""

                column = "Merged_first"
                my_dict[column] = fetcher.fetch_merged_first_case()

                my_dict["type"] = case_type_from_json
                my_dict["date"] = verdict_date_from_json
                my_dict["caseNum"] = case_number_from_json
                my_dict["year"] = case_year_from_json

                # print("*****Petitioners*****")
                petitioners = fetcher.fetch_petitioners()
                counter = 1
                for petitioner in petitioners:
                    column = "petitioner" + str(counter)
                    my_dict[column] = petitioner
                    counter = counter + 1
                    #print(petitioner)

                # print("*****lawyers_pet*****")
                lawyers_pet = fetcher.fetch_petitioners_lawyers()
                counter = 1
                for lawyerP in lawyers_pet:
                    column = "lawyerP" + str(counter)
                    my_dict[column] = lawyerP
                    counter = counter + 1
                    #print(lawyer)

                # print("*****Respondents*****")
                respondents = fetcher.fetch_respondents()
                counter = 1
                for respondent in respondents:
                    column = "respondent" + str(counter)
                    my_dict[column] = respondent
                    counter = counter + 1
                    # print(respondent)

                # print("*****lawyers_res*****")
                lawyers_res = fetcher.fetch_respondents_lawyers()
                counter = 1
                for lawyerR in lawyers_res:
                    column = "lawyerR" + str(counter)
                    my_dict[column] = lawyerR
                    counter = counter + 1
                    # print(lawyer)

                # print("*****Judges*****")
                judges = fetcher.fetch_judges()
                counter = 1
                judges_counter = 0
                for judge in judges:
                    if "שופט" in judge or "נשיא" in judge:
                        judges_counter = judges_counter + 1
                    column = "justice" + str(counter)
                    my_dict[column] = judge
                    counter = counter + 1

                if judges_counter > 0:
                    column = "Njudges"
                    my_dict[column] = str(judges_counter)

                first_url = url
                url = "https://elyon2.court.gov.il/Scripts9/mgrqispi93.dll?Appname=eScourt&Prgname=GetFileDetails_for_new_site&Arguments=-N%s-%s-0" \
                      % (case_year_from_json, str(case_number_from_json).zfill(6))

                # print("*****Last paragraph*****")
                elements = driver.find_elements_by_tag_name("table")
                for element in elements:
                    text = element.text
                    if "פסק-דין" in text or "פסק דין" in text:
                        print(element.text)
                        print("*****First url*****")
                        if "19083150.O03" in first_url:
                            print("")
                        print(first_url)
                        print("*****Second url*****")
                        print(url)
                        # TODO: Only Final decisions (פס״ד). In case there's no opinion writer - Write "unanimous"
                        column = "JOpinionWriter"
                        my_dict[column] = fetcher.get_j_opinion_writer()

                        # TODO: Count the words in the final decision paragraph
                        column = "Nwords"
                        my_dict[column] = fetcher.get_num_of_words()

                        break

                        # print("*****Last paragraph*****")
                fetcher.navigate_to_web_page(url)

                column = "NPetitioners"
                my_dict[column] = str(len(petitioners))

                column = "NRespondents"
                my_dict[column] = str(len(respondents))

                fetcher.click_on_delemata_tab()

                column = "CourtSourceInstance"
                my_dict[column] = fetcher.get_court_source_instance()

                # TODO: Might be more than one court - Take the upper row
                # https://elyon2.court.gov.il/Scripts9/mgrqispi93.dll?Appname=eScourt&Prgname=GetFileDetails_for_new_site&Arguments=-N2019-008077-0
                column = "CourtSourceDistrict"
                my_dict[column] = fetcher.get_court_source_district()

                column = "DateCaseSource"
                my_dict[column] = fetcher.get_date_case_source()

                column = "NumCaseSource"
                my_dict[column] = fetcher.get_num_case_source()

                fetcher.click_on_general_details_tab()

                column = "DateOpen"
                my_dict[column] = fetcher.get_date_open()

                # An example of confidential case:
                # https://elyon2.court.gov.il/Scripts9/mgrqispi93.dll?Appname=eScourt&Prgname=GetFileDetails_for_new_site&Arguments=-N2019-008301-0
                fetcher.click_on_events_tab()
                # TODO: Get upper row in events
                column = "DateFinalDecision"
                my_dict[column] = fetcher.get_date_final_decision()

                fetcher.click_on_hearings_tab()

                # TODO: Count the rows
                # https://elyon2.court.gov.il/Scripts9/mgrqispi93.dll?Appname=eScourt&Prgname=GetFileDetails_for_new_site&Arguments=-N2010-000002-0
                column = "NumHearings"
                my_dict[column] = fetcher.get_num_hearings()

                # TODO: Related to NumHearings (First)
                column = "DateFArgument"
                my_dict[column] = fetcher.get_date_first_argument()

                # TODO: Related to NumHearings (Last) - What's the difference from final decision?
                column = "DateLArgument"
                my_dict[column] = fetcher.get_date_last_argument()

                # TODO: Discuss with Maoz
                column = "Title"

                # TODO: Discuss with Maoz
                column = "Retired"





                # row_found = False
                # with open(file_name, newline='') as csvfile:
                #     reader = csv.reader(csvfile, delimiter=',')
                #     for row in reader:
                #         if my_dict.get("caseId") in row:
                #             row_found = True
                #             break
                #
                # if not row_found:
                with open(file_name, 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, my_dict.keys())
                    writer.writerow(my_dict)


def __restart_dict():
    return {"caseId": "","ISCD_ID" : "", "caseName": "","caseCitation": "", "url": "",
            "Merged": "", "Merged_first": "", "petitioner1": "", "petitioner2": "", "petitioner3": "",
            "petitionerType1": "", "petitionerType2": "", "petitionerType3": "",
            "lawyerP1": "", "lawyerP2": "", "lawyerP3": "",
            "respondent1": "", "respondent2": "", "respondent3": "",
            "respondentType1": "", "respondentType2": "", "respondentType3": "",
            "lawyerR1": "", "lawyerR2": "", "lawyerR3": "",
            "NPetitioners": "","NRespondents": "", "CourtSourceInstance": "", "CourtSourceDistrict": "",
            "NumCaseSource": "", "DateCaseSource": "", "DateOpen": "",
            "DateFinalDecision": "", "NumHearings": "", "DateFArgument": "",
            "DateLArgument": "", "LIssue": "", "legalProcedure": "",
            "legalProcedureHebrew": "", "LIssueArea": "", "LIssueAreaHebrew": "",
            "issuecourt-1": "", "issuecourt-2": "", "dispositioncourt": "",
            "outcomecourt": "", "winnercourt": "", "Nwords": "",
            "agreedOutcome": "", "Njudges": "", "nMajority": "","nMinority" : "",
            "JOpinionWriter": "","justice1": "", "justice2": "", "justice3": "",
            "justice4": "", "justice5": "", "justice6": "", "justice7": "",
            "justice8": "", "justice9": "", "justice10": "", "justice11": "",
            "type": "", "date": "", "caseNum": "", "year": ""
            }


if __name__ == "__main__":
    main()