from selenium.webdriver.remote import webelement

from infra.actions import Actions

judges_keywords = ["בפני","לפני"]
petitioners_keywords = ["המאשי","התובע","המבקש","העורר","העותר","מערער"]
respondents_keywords = ["הנאש","הנתבע","המשיב"]
lawyers_keywords = ["בשם"]


class FetcherActions(Actions):


    def fetch_case_name_title(self) -> str:
        case_element = self.get_element_by_name("casename_body")
        case_text = self.get_element_text(case_element)
        if len(case_text) > 0:
            return case_text

        return self.get_element_text_by_class_name("FileNumber")

    def fetch_judges(self) -> list:
        table_body = self.__get_table(judges_keywords)
        return self.__get_names(table_body,judges_keywords)

    def fetch_petitioners(self) -> list:
        table_body = self.__get_table(petitioners_keywords)
        return self.__get_names(table_body, petitioners_keywords)

    def fetch_respondents(self) -> list:
        table_body = self.__get_table(respondents_keywords)
        return self.__get_names(table_body, respondents_keywords)

    def fetch_petitioners_lawyers(self) -> list:
        return self.__fetch_lawyers(True)

    def fetch_respondents_lawyers(self) -> list:
        return self.__fetch_lawyers(False)

    def __fetch_lawyers(self, search_for_petitioner) -> list:
        lawyers = []
        tables = self.__get_tables(lawyers_keywords)
        if len(tables) > 0:
            for table in tables:
                table_body = self.get_sub_element_by_tag_name(table, "tbody")
                names_cells = self.get_sub_elements_by_tag_name(table_body, "td")
                if len(names_cells) == 2 and len(tables) == 1:
                    return self.__get_lawyers_edge_case(names_cells, search_for_petitioner)
                else:
                    names_texts = self.__get_names(table_body, "")
                    start_append = False
                    for name in names_texts:
                        is_petitioners_keyword = self.__check_is_a_keyword(petitioners_keywords, name)
                        if is_petitioners_keyword:
                            if search_for_petitioner:
                                start_append = True
                            else:
                                start_append = False
                            continue
                        is_respondents_keyword = self.__check_is_a_keyword(respondents_keywords, name)
                        if is_respondents_keyword:
                            if search_for_petitioner:
                                start_append = False
                            else:
                                start_append = True
                            continue
                        if start_append and (not is_petitioners_keyword or not is_respondents_keyword):
                            lawyers.append(name.replace(",", " "))
        else:
            rows = self.__get_special_rows(lawyers_keywords)
            for row in rows:
                row_text = self.get_element_text(row)
                if search_for_petitioner:
                    if self.__check_is_a_keyword(petitioners_keywords, row_text):
                        lawyers.append(row_text.replace(",", " "))
                else:
                    if self.__check_is_a_keyword(respondents_keywords, row_text):
                        lawyers.append(row_text.replace(",", " "))
        return lawyers

    def __get_lawyers_edge_case(self, names_cells, search_for_petitioner):
        lawyers = []
        if search_for_petitioner:
            titles = self.get_sub_elements_by_class_name(names_cells[0], "bodyRuller")
            respondents_index = self.__get_petitioner_lawyers_index(titles)

            names = self.get_sub_elements_by_class_name(names_cells[1], "bodyRuller")
            if respondents_index == 0:
                respondents_index = len(names)
            for start_index in range(respondents_index):
                name_text = self.get_element_text(names[start_index])
                if len(name_text) > 0:
                    lawyers.append(name_text.replace(",", " "))
        else:
            titles = self.get_sub_elements_by_class_name(names_cells[0], "bodyRuller")
            respondents_index = self.__get_respondent_lawyers_index(titles)
            if respondents_index > 0:
                names = self.get_sub_elements_by_class_name(names_cells[1], "bodyRuller")
                for index in range(respondents_index, len(names)):
                    name_text = self.get_element_text(names[index])
                    if len(name_text) > 0:
                        lawyers.append(name_text.replace(",", " "))
        return lawyers

    def __get_respondent_lawyers_index(self, names):
        for i in range(len(names)):
            name_text = self.get_element_text(names[i])
            is_respondents_keyword = self.__check_is_a_keyword(respondents_keywords, name_text)
            if len(name_text) > 0 and is_respondents_keyword:
                return i

        return -1

    def __get_petitioner_lawyers_index(self, names):
        for i in range(len(names)):
            name_text = self.get_element_text(names[i])
            is_petitioner_keyword = self.__check_is_a_keyword(petitioners_keywords, name_text)
            if len(name_text) > 0 and is_petitioner_keyword:
                return i

        return -1

    def __check_is_a_keyword(self, expected_keywords, actual_keyword):
        for keyword in expected_keywords:
            if keyword in actual_keyword or actual_keyword in keyword:
                return True
        return False

    def __get_table(self, keywords: list):
        table_elements = self.get_elements_by_class_name("MsoNormalTable")
        for table_element in table_elements:
            table_text = self.get_element_text(table_element)
            for keyword in keywords:
                if keyword in table_text:
                    return self.get_sub_element_by_tag_name(table_element, "tbody")
        return None

    def __get_tables(self, keywords: list):
        tables = []
        table_elements = self.get_elements_by_class_name("MsoNormalTable")
        for table_element in table_elements:
            table_text = self.get_element_text(table_element)
            for keyword in keywords:
                if keyword in table_text:
                    tables.append(table_element)
        return tables

    def __get_special_rows(self, keywords: list):
        rows = []
        rows_elements = self.get_elements_by_class_name("Ruller3")
        for rows_element in rows_elements:
            row_text = self.get_element_text(rows_element)
            for keyword in keywords:
                if keyword in row_text:
                    rows.append(rows_element)
        return rows

    def __get_names(self, table_body: webelement, keywords: list) -> list:
        names_texts = []
        names_cells = self.get_sub_elements_by_tag_name(table_body, "td")
        if names_cells is not None:
            for names_cell in names_cells:
                names = self.get_sub_elements_by_class_name(names_cell, "bodyRuller")
                if names is None:
                    names = self.get_sub_elements_by_class_name(names_cell,"MsoNormal")
                for name in names:
                    name_text = self.get_element_text(name)
                    is_a_keyword = False
                    for keyword in keywords:
                        if keyword in name_text:
                            is_a_keyword = True

                    if not is_a_keyword and len(name_text) > 0:
                        names_texts.append(name_text.replace(",", " "))

        return names_texts

    def click_on_general_details_tab(self):
        menu_link = self.get_element_by_css_selector("a[href='#menu1']")
        self.click_on_element(menu_link)

    def click_on_delemata_tab(self):
        menu_link = self.get_element_by_css_selector("a[href='#menu3']")
        self.click_on_element(menu_link)

    def click_on_hearings_tab(self):
        menu_link = self.get_element_by_css_selector("a[href='#menu4']")
        self.click_on_element(menu_link)

    def click_on_events_tab(self):
        menu_link = self.get_element_by_css_selector("a[href='#menu5']")
        self.click_on_element(menu_link)

    '''
    The name of the court whose decision the Israeli Supreme Court is reviewing. This variable classifies the court whose decision the Israeli Supreme Court is reviewing according to the following procedure: In criminal, civil or administrative appeals, it specifies the court system in which the appealed case was last decided, according to the details of the appealed case transferred to the Supreme Court’s secretariat. Tracing to gradual and constant changes in first instance jurisdiction in administrative matters, the distinction between “District Court – General” and “District Court – Administrative” is not always consistent among the court’s secretariat staff. We note that our coding reflects the classification made by the court, even if their classification is inaccurate.
In HCJ cases, the variable specifies a specialized tribunal only in cases in which at least one of the petitioners identifies the relevant tribunal. Our coding in this respect is limited to the petitioner’s decision to include the relevant tribunal as one of the respondents to the petition. A missing value is registered otherwise, indicating that the Israeli Supreme Court is the first (and last) judicial instance hearing the case, as in most HCJ cases.
Variable values are:

·         Antitrust Tribunal

·         Court of Admiralty

·         District Court - Administrative

·         District Court – General

·         Labor Court

·         Magistrate Court

·         Military Court

·         Religious Court

·         Standard Contracts Court
    '''
    def get_court_source_instance(self):
        text = self.get_element_text_by_css_selector("td[class='courtName']")
        if len(text) > 0:
            return text.split(" ")[0]

    def get_court_source_instance(self):
        text = self.get_element_text_by_css_selector("td[class='courtName']")
        if len(text) > 0:
            return text.split(" ")[0]

    '''
     CourtSourceDistrict - The name of the geographic district of the court whose decision the Israeli Supreme Court is reviewing. A missing value is registered in all HCJ cases as the Israeli Supreme Court is generally the first (and last) judicial instance hearing these cases (see CourtSourceInstance). Additionally, we note that HCJ petitions against specialized tribunals are mostly filed against a national level (appeal level) tribunal, rather than geographical relevant court
Variable values are:

·         Central

·         Beersheba

·         Haifa

·         Jerusalem

·         Nazareth

·         Tel Aviv
    '''
    def get_court_source_district(self):
        text = self.get_element_text_by_css_selector("td[class='courtName']")
        if len(text.split()) > 0:
            if len(text.split()) > 2:
               return text.split(" ")[1] + " " + text.split(" ")[2]
            return text.split(" ")[1]

    '''
     A unique docket number for the original case the Israeli Supreme Court is reviewing. 
     The labeling is standardized by the Israeli judiciary and comprises a procedural 
     classification, serial number, dash and the month and year of case opening 
     in the lower court instance. In older cases, opened at the court of origin prior to 2009, 
     the labeling could also appear in one of the following formats: XXXXXX/YY or 00-XXXXXX/YY.
    '''
    def get_num_case_source(self):
        return self.get_element_text_by_css_selector("td[data-label='מ.תיק דלמטה']")

    def get_date_case_source(self):
        return self.get_element_text_by_css_selector("td[data-label='ת.החלטה']")

    '''
     The day, month and year of the final decision by the lower court in 
     the case the Israeli Supreme Court is reviewing. This variable has no entry for HCJ cases
    '''
    def get_date_case_source(self):
        return self.get_element_text_by_css_selector("td[data-label='ת.החלטה']")


    def __get_label_value(self,label_title):
        labels = self.get_elements_by_class_name("caseDetails-label")
        for label in labels:
            label_text = self.get_element_text(label)
            if label_title in label_text:
                parent = self.get_element_parent(label)
                return self.get_sub_element_by_class_name(parent, "caseDetails-info")

        return None

    # The day, month and year of the case filing in the Israeli Supreme Court.
    def get_date_open(self):
        label_value_element = self.__get_label_value("תאריך הגשה")
        return self.get_element_text(label_value_element)

    #  The day, month and year of the final closing decision rendered in the case.
    def get_date_final_decision(self):
       decisions = self.__get_all_decisions()
       if len(decisions) <= 0:
           return ""
       last_decision_element = decisions[0]
       final_decision_date_element = self.get_sub_element_by_css_selector(last_decision_element,"td[data-label='תאריך']")
       final_decision_date = self.get_element_text(final_decision_date_element)
       return final_decision_date

    def __get_all_decisions(self):
        tab_main_container = self.get_element_by_id("menu5")
        event_rows = self.get_sub_elements_by_tag_name(tab_main_container, "tr")
        decisions = []
        if event_rows is not None:
            for event_row in event_rows:
                event = self.get_sub_element_by_class_name(event_row, "main-event")
                event_text = self.get_element_text(event)
                if "דין" in event_text:
                    decisions.append(event_row)

        return decisions


    def __get_actual_hearings(self):
        tab_main_container = self.get_element_by_id("menu4")
        hearings = self.get_sub_elements_by_tag_name(tab_main_container, "tr")
        actual_hearings = []
        if hearings is not None:
            for hearing in hearings:
                status = self.get_sub_element_by_css_selector(hearing, "td[data-label='סטטוס']")
                status_text = self.get_element_text(status)
                if "התקיים" in status_text:
                    actual_hearings.append(hearing)

        return actual_hearings

    # A counter for the number of times the Israeli Supreme Court heard oral arguments in the case.
    def get_num_hearings(self):
        hearings = self.__get_actual_hearings()
        return len(hearings)
        # tab_main_container = super().get_element_by_id("menu5")
        # table = super().get_sub_element_by_tag_name(tab_main_container,"tbody")
        # hearings = super().get_sub_elements_by_tag_name(table,"tr")
        # if hearings is None:
        #     return 0
        # return len(hearings)

    def get_date_first_argument(self):
        hearings = self.__get_actual_hearings()
        if len(hearings) <= 0:
            return ""
        first_argument_element = hearings[0]
        first_argument_date_element = self.get_sub_element_by_css_selector(first_argument_element,
                                                                           "td[data-label='תאריך']")
        first_argument_date = self.get_element_text(first_argument_date_element)
        return first_argument_date

    def get_date_last_argument(self):
        hearings = self.__get_actual_hearings()
        if len(hearings) <= 0:
            return ""
        last_argument_element = hearings[len(hearings)-1]
        last_argument_date_element = self.get_sub_element_by_css_selector(last_argument_element,
                                                                               "td[data-label='תאריך']")
        last_argument_date = self.get_element_text(last_argument_date_element)
        return last_argument_date

        # tab_main_container = super().get_element_by_id("menu5")
        # if tab_main_container is None:
        #     print("")
        # table = super().get_sub_element_by_tag_name(tab_main_container, "tbody")
        # hearings = super().get_sub_elements_by_tag_name(table,"td[data-label='תאריך']")
        # if hearings is None:
        #     return ""
        # first_hearing = hearings[len(hearings)-1]
        # return super().get_element_text(first_hearing)

    def get_j_opinion_writer(self):
        writer_element = self.get_element_by_name("Writer_Name")
        writer_parent = self.get_element_parent(writer_element)
        writer_text = self.get_element_text(writer_parent)
        if len(writer_text) == 0 or 'השופט' not in writer_text:
            return "unanimous"
        return writer_text

    def get_num_of_words(self):
        writer_element = self.get_element_by_name("Writer_Name")
        writer_element_y = 0
        if writer_element is None:
            possible_elements = self.get_elements_by_tag_name("p")
            for possible_element in possible_elements:
                element_text = self.get_element_text(possible_element)
                if "פסק-דין" == str.strip(element_text):
                    writer_element_y = possible_element.location.get("y")
                    break
        else:
            writer_element_y = writer_element.location.get("y")

        possible_elements = self.get_elements_by_tag_name("p")
        actual_elements = []
        for possible_element in possible_elements:
            element_y = possible_element.location.get("y")
            if element_y > writer_element_y:
                actual_elements.append(possible_element)

        text = ""
        for actual_element in actual_elements:
            element_text = self.get_element_text(actual_element)
            text += element_text

        return len(text.split())



    def fetch_merged_cases_number(self):
        cases = self.get_elements_by_class_name("FileNumber")
        if len(cases) > 1:
            return len(cases)
        return 0

    def fetch_merged_first_case(self):
        if self.fetch_merged_cases_number() > 0:
            cases = self.get_elements_by_class_name("FileNumber")
            first_merged_case_element = cases[0]
            return self.get_element_text(first_merged_case_element)
        return ""
