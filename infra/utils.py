import csv
import os
import random
import re
import shutil
import string
import time
from datetime import datetime

from infra.timers import Timers

timers = Timers()

def get_current_time_in_millis() -> int:
    return int(time.time() * 1000)


def is_time_out(start_time_millis: int, waiting_interval_seconds: int) -> bool:
    end_time = start_time_millis + waiting_interval_seconds*1000
    return get_current_time_in_millis() > end_time


def remove_date_day_suffix(text_to_replace: str) -> str:
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', text_to_replace)


def format_hour(time_to_format: str) -> datetime:
    return datetime.strptime(time_to_format, "%I:%M %p")


def validate_time_in_range(expected_range: str, hours_to_check: str) -> bool:
    start_time = get_start_hour_from_range(hours_to_check)
    end_time = get_end_hour_from_range(hours_to_check)
    result = is_time_in_range(expected_range, start_time)
    if result:
        result = is_time_in_range(expected_range, end_time)
    return result


def get_start_hour_from_range(expected_range: str) -> datetime:
    start_time = get_hour_from_range(expected_range, 0)
    return start_time


def get_end_hour_from_range(expected_range: str) -> datetime:
    start_time = get_hour_from_range(expected_range, 1)
    return start_time


def get_hour_from_range(expected_range: str, time_location: int) -> datetime:
    hours = expected_range.split("-")
    if len(hours) <= time_location:
        print(str(time_location) + " is not within range: " + expected_range)
        return None
    hour = hours[time_location].strip()
    return format_hour(hour)


def is_time_in_range(expected_range, time_to_check) -> bool:
    start_time = get_start_hour_from_range(expected_range)
    end_time = get_end_hour_from_range(expected_range)

    if start_time < end_time:
        return start_time <= time_to_check <= end_time
    else:  # Over midnight
        return time_to_check >= start_time or time_to_check <= end_time


def is_download_present(download_folder_location: str) -> bool:
    return is_extension_present(download_folder_location, ".crdownload")


def is_extension_present(download_folder_location: str, file_extension) -> bool:
    files = os.listdir(download_folder_location)
    for file in files:
        if file_extension in file:
            return True
    return False


def wait_for_file_to_appear_in_folder_by_extension(file_path: str, expected_file_extension: str, wait_time=timers.get_time_to_wait_for_download_to_complete_seconds()) -> bool:
    is_file_extension_exist = is_extension_present(file_path, expected_file_extension)
    start_time = get_current_time_in_millis()
    while not is_file_extension_exist and not is_time_out(start_time, wait_time):
        print("in wait_for_file_by_extension loop")
        time.sleep(1)
        is_file_extension_exist = is_extension_present(file_path, expected_file_extension)

    return is_file_extension_exist


def wait_for_download_to_complete(
        download_folder_location: str, wait_time=timers.get_time_to_wait_for_download_to_complete_seconds()) -> bool:

    is_downloading_file_exist = True
    start_time = get_current_time_in_millis()

    while is_downloading_file_exist and not is_time_out(start_time, wait_time):
        time.sleep(0.5)
        is_downloading_file_exist = is_download_present(download_folder_location)

    end_time = get_current_time_in_millis()
    total_time = (end_time - start_time)/1000
    print("total wait time is was: " + str(total_time))

    return not is_downloading_file_exist


def get_amount_of_files_in_folder(folder_path: str) -> int:
    file_list = os.listdir(folder_path)
    return len(file_list)

def get_csv_headers(csv_file_path):
    with open(csv_file_path) as csv_file:
        reader = csv.reader(csv_file)
        return next(reader)


def get_csv_file_by_partial_name(csv_file_path, partial_csv_name) -> str:
    file_list = os.listdir(csv_file_path)
    for file in file_list:
        if partial_csv_name in file:
            return csv_file_path + "/" + file
    return ''


def validate_csv_headers(csv_file_path: str, expected_list: str) -> bool:
    expected_headers = expected_list.split(",")
    actual_headers = get_csv_headers(csv_file_path)
    for expected_header in expected_headers:
        expected_header = expected_header.strip()
        if expected_header not in actual_headers:
            print(expected_header + " wasn't found on " + csv_file_path)
            return False
    return True


def remove_spaces_from_list(list_to_strip) -> list:
    list_to_strip = [i.strip() for i in list_to_strip]
    return list_to_strip

def compare_str_lists_contains(list1: list, list2:list) -> bool:
    return compare_str_lists(list1, list2, True)


def compare_str_lists(list1: list, list2: list, check_if_contains=False) -> bool:
    if len(list1) != len(list2):
        return False

    list1.sort()
    list2.sort()
    index = 0
    while index < len(list1):
        list1_element = list1[index]
        list2_element = list2[index]
        if check_if_contains:
            if list1_element not in list2_element and list2_element not in list1_element:
                return False
        else:
            if list1_element != list2_element:
                return False
        index = index + 1

    return True

def save_html_file(file_name: str,html_content: str, file_path: str):

    complete_path = os.path.join(file_path, file_name + ".html")

    with open(complete_path, "w") as file:

        file.write(html_content)
        file.close()

    return complete_path


def compare_strings_without_inner_spaces(string_1: str, string_2: str) -> bool:
    return string_1.replace("  ", "") == string_2.replace("  ", "")

def get_user_home_folder():
    return os.path.expanduser("~")

def get_user_default_download_folder():
    user_home_folder = get_user_home_folder()
    return os.path.join(user_home_folder, "Downloads")


def get_latest_file_in_folder(path, file_extension:str=None) -> str:
    files = os.listdir(path)
    max_time = -1
    max_file = ""
    for file in files:
        file_full_path = os.path.join(path, file)
        file_timestamp = os.path.getctime(file_full_path)
        if file_extension:
            if file_extension not in file:
                continue
        if file_timestamp > max_time:
            max_time = file_timestamp
            max_file = file_full_path

    return max_file


def move_file(source, destination):
    shutil.move(source, destination)
