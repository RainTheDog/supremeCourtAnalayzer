import configparser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class Timers:

    TIME_TO_WAIT_FOR_DOWNLOAD_TO_COMPLETE_SECONDS = 60
    TIME_TO_WAIT_FOR_ELEMENT_TO_LOAD_SECONDS = 25
    TIME_TO_WAIT_FOR_ELEMENT_TRANSITION_SECONDS = 5
    TIME_TO_WAIT_FOR_ELEMENT_TO_BE_INTERACTABLE_SECONDS = 5
    TIME_TO_WAIT_FOR_ELEMENT_TO_LOAD_SHORT_SECONDS = 5
    TIME_TO_WAIT_FOR_ELEMENT_TO_VANISH_SECONDS = 25
    TIME_TO_WAIT_FOR_EMAIL_SECONDS = 60
    TIME_TO_WAIT_FOR_NEW_TAB_SECONDS = 3
    TIME_TO_DELAY_BETWEEN_LETTERS_MILLISECONDS = 10
    TIME_TO_WAIT_FOR_PROGRESS_BAR_SECONDS = 5
    TIME_TO_WAIT_FOR_UPGRADE_PLAN_SECONDS = 10

    config = configparser.ConfigParser()

    def __init__(self, conf_file_path=None):
        if not conf_file_path:
            conf_file_path = os.path.join(ROOT_DIR, "timers.ini")
        # TODO: add support for reading the file from command line
        self.config.read(conf_file_path)

    def get_timer_from_file(self, timer_name: str) -> int:
        timer_value = self.get_data_from_config_file('timers', timer_name)
        if timer_value is not None:
            return int(timer_value)
        return -1


    def get_time_to_wait_for_download_to_complete_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_download_to_complete_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_DOWNLOAD_TO_COMPLETE_SECONDS

    def get_time_to_wait_for_element_to_load_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_element_to_load_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_ELEMENT_TO_LOAD_SECONDS

    def get_time_to_wait_for_element_transition_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_element_transition_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_ELEMENT_TRANSITION_SECONDS

    def get_time_to_wait_for_element_to_be_interactable_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_element_to_be_interactable_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_ELEMENT_TO_BE_INTERACTABLE_SECONDS

    def get_time_to_wait_for_element_to_load_short_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_element_to_load_short_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_ELEMENT_TO_LOAD_SHORT_SECONDS

    def get_time_to_wait_for_element_to_vanish_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_element_to_vanish_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_ELEMENT_TO_VANISH_SECONDS

    def get_time_to_wait_for_email_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_email_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_EMAIL_SECONDS

    def get_time_to_wait_for_new_tab_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_new_tab_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_NEW_TAB_SECONDS

    def get_time_to_delay_between_letters_milliseconds(self):
        timer_from_file = self.get_timer_from_file("time_to_delay_between_letters_milliseconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_DELAY_BETWEEN_LETTERS_MILLISECONDS

    def get_time_to_wait_for_progress_bar_seconds(self):
        timer_from_file = self.get_timer_from_file("time_to_wait_for_progress_bar_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_PROGRESS_BAR_SECONDS

    def get_time_to_wait_for_upgrade_plan_seconds(self):
        timer_from_file = self.get_timer_from_file("get_time_to_wait_for_upgrade_plan_seconds")
        if timer_from_file > 0:
            return timer_from_file
        return self.TIME_TO_WAIT_FOR_UPGRADE_PLAN_SECONDS


    def get_data_from_config_file(self, master_key: str, secondary_key: str):
        try:
            return self.config[master_key][secondary_key]
        except KeyError:
            return None

