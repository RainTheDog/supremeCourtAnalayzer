import time
import traceback

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, \
    StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common import action_chains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote import webelement
from selenium.webdriver.remote.webelement import WebElement

from infra.timers import Timers
from infra.utils import get_current_time_in_millis, is_time_out


class Actions:
    
    timers = Timers()
    
    def __init__(self, browser: webdriver):
        self.actions_driver = browser

    def get_current_url(self) -> str:
        return self.actions_driver.current_url

    # In case the navigation will fail Selenium will throw an exception
    def navigate_to_web_page(self, url: str) -> bool:
        self.actions_driver.get(url)
        return True

    def _get_element(self, by: By, value: str) -> WebElement:
        try:
            return self.actions_driver.find_element(by, value)
        except NoSuchElementException:
            return None

    def get_element_by_id(self, resource_id: str) -> WebElement:
        return self._get_element(By.ID, resource_id)

    def get_element_by_css_selector(self, css_selector: str) -> WebElement:
        return self._get_element(By.CSS_SELECTOR, css_selector)

    def get_element_by_class_name(self, class_name: str) -> WebElement:
        return self._get_element(By.CLASS_NAME, class_name)

    def get_element_by_name(self, name: str) -> WebElement:
        return self._get_element(By.NAME, name)

    def get_element_by_xpath(self, xpath: str) -> WebElement:
        return self._get_element(By.XPATH, xpath)

    def get_element_by_tag_name(self, tag_name: str) -> WebElement:
        return self._get_element(By.TAG_NAME, tag_name)

    def get_element_by_partial_id(self, resource_partial_id: str) -> WebElement:
        value = "//*[contains(@id, '" + resource_partial_id + "')]"
        return self._get_element(By.XPATH, value)

    def _get_displayed_element(self, by: By, value: str) -> WebElement:
        try:
            elements = self._get_elements(by, value)
            for element in elements:
                is_displayed = self.is_element_displayed(element)
                if is_displayed:
                    return element
            return None
        except NoSuchElementException:
            return None

    def get_displayed_element_by_class_name(self, class_name: str) -> WebElement:
        return self._get_displayed_element(By.CLASS_NAME, class_name)

    def get_displayed_element_by_css_selector(self, css_selector: str) -> WebElement:
        return self._get_displayed_element(By.CSS_SELECTOR, css_selector)

    def _get_displayed_sub_element(self, parent: webelement, by: By, value: str) -> WebElement:
        try:
            elements = self._get_sub_elements(parent, by, value)
            for element in elements:
                is_displayed = self.is_element_displayed(element)
                if is_displayed:
                    return element
            return None
        except NoSuchElementException:
            return None

    def get_displayed_sub_element_by_class_name(self, parent, class_name: str) -> WebElement:
        return self._get_displayed_sub_element(parent, By.CLASS_NAME, class_name)


    def _get_elements(self, by: By, resource_value: str) -> list:
        try:
            web_elements: list = self.actions_driver.find_elements(by, resource_value)
            return web_elements
        except NoSuchElementException:
            return None

    def get_elements_by_class_name(self, class_name: str) -> list:
        return self._get_elements(By.CLASS_NAME, class_name)

    def get_elements_by_css_selector(self, css_selector: str) -> list:
        return self._get_elements(By.CSS_SELECTOR, css_selector)

    def get_elements_by_tag_name(self, tag_name: str) -> list:
        return self._get_elements(By.TAG_NAME, tag_name)

    def get_elements_by_partial_id(self, resource_partial_id: str) -> list:
        value = "//*[contains(@id, '" + resource_partial_id + "')]"
        return self._get_elements(By.XPATH, value)

    def get_element_text(self, element: WebElement) -> str:
        try:
            if element:
                text = element.text
                if not text:
                    return str.strip(self.get_element_attribute(element, "textContent"))
                else:
                    return str.strip(text)
            else:
                return ''
        except Exception:
            return ''

    def get_element_text_by_class_name(self, class_name: str) -> str:
        element = self.get_element_by_class_name(class_name)
        return self.get_element_text(element)

    def get_element_text_by_css_selector(self, css_selector: str) -> str:
        element = self.get_element_by_css_selector(css_selector)
        return self.get_element_text(element)

    def _get_sub_element(self, parent_element: WebElement, by: By, attribute_name: str) -> WebElement:
        if parent_element is None:
            return None
        try:
            return parent_element.find_element(by=by, value=attribute_name)
        except NoSuchElementException:
            return None

    def get_sub_element_by_id(self, parent_element: WebElement, element_id: str) -> WebElement:
        return self._get_sub_element(parent_element, By.ID, element_id)

    def get_sub_element_by_class_name(self, parent_element: WebElement, class_name: str) -> WebElement:
        return self._get_sub_element(parent_element, By.CLASS_NAME, class_name)

    def get_sub_element_by_css_selector(self, parent_element: WebElement, css_selector: str) -> WebElement:
        return self._get_sub_element(parent_element, By.CSS_SELECTOR, css_selector)

    def get_sub_element_by_tag_name(self, parent_element: WebElement, tag_name: str) -> WebElement:
        return self._get_sub_element(parent_element, By.TAG_NAME, tag_name)

    def get_sub_element_by_name(self, parent_element: WebElement, element_name: str) -> WebElement:
        return self._get_sub_element(parent_element, By.NAME, element_name)

    def _get_sub_elements(self, parent_element: WebElement, by: By, resource_value: str) -> list:
        try:
            if parent_element:
                return parent_element.find_elements(by, resource_value)
            return None
        except NoSuchElementException:
            return None

    def get_sub_elements_by_class_name(self, parent_element: WebElement, class_name: str) -> list:
        return self._get_sub_elements(parent_element, By.CLASS_NAME, class_name)

    def get_sub_elements_by_css_selector(self, parent_element: WebElement, css_selector: str) -> list:
        return self._get_sub_elements(parent_element, By.CSS_SELECTOR, css_selector)

    def get_sub_elements_by_tag_name(self, parent_element: WebElement, tag_name: str) -> list:
        return self._get_sub_elements(parent_element, By.TAG_NAME, tag_name)


    def get_element_parent(self, child_element: WebElement) -> WebElement:
        return self._get_sub_element(child_element, By.XPATH, "..")

    def _clear_text(self, element: WebElement) -> bool:
        element.clear()
        element_text = self.get_element_text(element)
        return element_text == ''

    def _clear_text_by_id(self, resource_id: str) -> bool:
        element = self.get_element_by_id(resource_id)
        return self._clear_text(element)

    def _insert_text(self, element: WebElement, text_to_insert: str,
                     delay_in_milliseconds: int = timers.get_time_to_delay_between_letters_milliseconds()) -> bool:
        if element:
            self._clear_text(element)
            for c in text_to_insert:
                element.send_keys(c)
                time.sleep(delay_in_milliseconds / 1000)
            return True
        return False

    def insert_text_by_id(self, resource_id: str, text_to_insert: str) -> bool:
        element = self.get_element_by_id(resource_id)
        return self._insert_text(element, text_to_insert)

    def insert_text_by_partial_id(self, resource_partial_id: str, text_to_insert: str) -> bool:
        element = self.get_element_by_partial_id(resource_partial_id)
        return self._insert_text(element, text_to_insert)

    def insert_text_by_css_selector(self, css_selector: str, text_to_insert: str,
                                    delay_in_milliseconds: int = None) -> bool:
        delay_in_milliseconds = delay_in_milliseconds or self.timers.get_time_to_delay_between_letters_milliseconds()

        element = self.get_element_by_css_selector(css_selector)
        return self._insert_text(element, text_to_insert, delay_in_milliseconds)

    def insert_text_by_name(self, element_name: str, text_to_insert: str, delay_in_milliseconds: int = None) -> bool:
        delay_in_milliseconds = delay_in_milliseconds or self.timers.get_time_to_delay_between_letters_milliseconds()

        element = self.get_element_by_name(element_name)
        return self._insert_text(element, text_to_insert, delay_in_milliseconds)

    def click_on_element(self, element: WebElement) -> bool:
        try:
            if element:
                element.click()
                return True
            return False
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            return False

    def click_until_interactable(self, element: WebElement) -> bool:
        element_is_interactable = False
        start_time = get_current_time_in_millis()
        counter = 1
        if element:
            while not element_is_interactable and not is_time_out(
                    start_time, self.timers.get_time_to_wait_for_element_to_be_interactable_seconds()):
                try:
                    element.click()
                    element_is_interactable = True
                except ElementNotInteractableException as e:
                    counter = counter + 1
        return element_is_interactable

    def click_on_body(self) -> bool:
        body_element = self.get_element_by_tag_name("body")
        return self.click_on_element(body_element)


    def click_on_element_by_id(self, element_id: str) -> bool:
        element = self.get_element_by_id(element_id)
        return self.click_on_element(element)

    def click_on_element_by_class_name(self, class_name: str) -> bool:
        element = self.get_element_by_class_name(class_name)
        return self.click_on_element(element)

    def click_on_element_by_name(self, name: str) -> bool:
        element = self.get_element_by_name(name)
        return self.click_on_element(element)

    def click_on_element_by_css_selector(self, selector: str) -> bool:
        element = self.get_element_by_css_selector(selector)
        return self.click_on_element(element)

    def click_on_element_by_xpath(self, xpath: str) -> bool:
        element = self.get_element_by_xpath(xpath)
        return self.click_on_element(element)

    def click_on_element_by_tag_name(self, tag_name: str) -> bool:
        element = self.get_element_by_tag_name(tag_name)
        return self.click_on_element(element)

    def click_on_sub_element_by_class_name(self, parent: webelement, class_name: str) -> bool:
        element = self.get_sub_element_by_class_name(parent, class_name)
        return self.click_on_element(element)

    def click_on_sub_element_by_tag_name(self, parent: webelement, tag_name: str) -> bool:
        element = self.get_sub_element_by_tag_name(parent, tag_name)
        return self.click_on_element(element)

    def click_on_sub_element_by_css_selector(self, parent: webelement, css_selector: str) -> bool:
        element = self.get_sub_element_by_css_selector(parent, css_selector)
        return self.click_on_element(element)


    def _wait_for_element(
            self, by: By, resource_value: str, check_is_displayed: bool,
            parent_element: webelement = None,
            time_out_in_seconds: int = timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        start_time = get_current_time_in_millis()
        is_found = False

        while not is_found and not is_time_out(start_time, time_out_in_seconds):
            if parent_element:
                element = self._get_sub_element(parent_element, by, resource_value)
            else:
                element = self._get_element(by, resource_value)

            if element:
                if check_is_displayed:
                    is_found = self.is_element_displayed(element)
                else:
                    is_found = True

        end_time = get_current_time_in_millis()
        wait_duration_in_seconds = (end_time - start_time) / 1000
        log(DebugLevel.INFO, "The total wait time was " + str(wait_duration_in_seconds))

        return is_found

    def wait_for_element_to_be_displayed_by_id(
            self, resource_id: str, timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self._wait_for_element(by=By.ID, resource_value=resource_id, check_is_displayed=True,
                                      time_out_in_seconds=timeout_in_seconds)

    def wait_for_element_to_be_displayed_by_class_name(
            self, class_name: str, timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self._wait_for_element(by=By.CLASS_NAME, resource_value=class_name, check_is_displayed=True,
                                      time_out_in_seconds=timeout_in_seconds)

    def wait_for_element_to_be_displayed_by_css_selector(
            self, css_selector: str, timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self._wait_for_element(by=By.CSS_SELECTOR, resource_value=css_selector, check_is_displayed=True,
                                      time_out_in_seconds=timeout_in_seconds)

    def wait_for_element_to_be_displayed_by_partial_id(
            self, resource_partial_id: str, timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        value = "//*[contains(@id, '" + resource_partial_id + "')]"
        return self._wait_for_element(by=By.XPATH, resource_value=value,
                                      check_is_displayed=True, time_out_in_seconds=timeout_in_seconds)

    def wait_for_element_to_be_displayed_by_partial_class_name(
            self, resource_partial_class_name: str, timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        value = "//*[contains(@class, '" + resource_partial_class_name + "')]"
        return self._wait_for_element(by=By.XPATH, resource_value=value,
                                      check_is_displayed=True, time_out_in_seconds=timeout_in_seconds)

    def wait_for_element_to_be_displayed_by_tag_name(
            self, tag_name: str,
            timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self._wait_for_element(by=By.TAG_NAME, resource_value=tag_name, check_is_displayed=True,
                                      time_out_in_seconds=timeout_in_seconds)

    def wait_for_element_to_be_displayed_by_name(
            self, name: str,
            timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self._wait_for_element(by=By.NAME, resource_value=name, check_is_displayed=True,
                                      time_out_in_seconds=timeout_in_seconds)

    def wait_for_sub_element_to_be_displayed_by_class_name(
            self, parent_element: webelement, class_name: str,
            timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self._wait_for_element(by=By.CLASS_NAME, resource_value=class_name, check_is_displayed=True,
                                      parent_element=parent_element, time_out_in_seconds=timeout_in_seconds)

    def wait_for_sub_element_to_be_displayed_by_css_selector(
            self, parent_element: webelement, css_selector: str,
            timeout_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self._wait_for_element(by=By.CSS_SELECTOR, resource_value=css_selector, check_is_displayed=True,
                                      parent_element=parent_element, time_out_in_seconds=timeout_in_seconds)

    def wait_for_element_text(
            self, element, time_out_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        start_time = get_current_time_in_millis()

        while not is_time_out(start_time, time_out_in_seconds):
            text = self.get_element_text(element)
            if text:
                return True

        return False

    def wait_for_text_to_change_by_class_name(
            self, text_before: str, class_name: str,
            time_out_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        return self.wait_for_text_to_change(text_before, By.CLASS_NAME, class_name, time_out_in_seconds)

    def wait_for_text_to_change(
            self, text_before, by: By, resource_value, time_out_in_seconds=timers.get_time_to_wait_for_element_to_load_seconds()) -> bool:
        start_time = get_current_time_in_millis()

        while not is_time_out(start_time, time_out_in_seconds):
            element = self._get_element(by, resource_value)
            text_after = self.get_element_text(element)
            if text_before != text_after:
                return True

        return False

    # This method will wait for the element which its size might change during transition
    def wait_for_element_to_complete_transition(
            self, element: webelement,
            time_out_in_seconds=timers.get_time_to_wait_for_element_transition_seconds()) -> bool:
        start_time = get_current_time_in_millis()

        element_y_before = self.get_element_y(element)
        # Since the element is in transition, we want to wait to sample it's height again
        time.sleep(0.1)
        element_y_after = self.get_element_y(element)

        while element_y_before != element_y_after and not is_time_out(start_time, time_out_in_seconds):
            element_y_before = element_y_after
            time.sleep(0.1)
            element_y_after = self.get_element_y(element)

        return element_y_before == element_y_after

    def wait_for_element_to_expand(
            self, element: webelement,
            time_out_in_seconds=timers.get_time_to_wait_for_element_transition_seconds()) -> bool:
        start_time = get_current_time_in_millis()

        element_height_before = self.get_element_height(element)
        # Since the element is in transition, we want to wait to sample it's height again
        time.sleep(0.1)
        element_height_after = self.get_element_height(element)

        while element_height_before != element_height_after and not is_time_out(start_time, time_out_in_seconds):
            element_height_before = element_height_after
            time.sleep(0.1)
            element_height_after = self.get_element_height(element)

        return element_height_before == element_height_after

    def is_element_displayed(self, element: WebElement) -> bool:
        try:
            if element:
                return element.is_displayed()
            else:
                return False
        except (StaleElementReferenceException, NoSuchElementException):
            return False

    def is_element_enabled(self, element: WebElement) -> bool:
        try:
            if element:
                return element.is_enabled()
            else:
                return False
        except StaleElementReferenceException:
            return False

    def _is_element_disabled(self, element: WebElement) -> bool:
        return not self.is_element_enabled(element)

    def _wait_for_element_to_vanish(self, element_to_vanish: WebElement,
                                    timeout=timers.get_time_to_wait_for_element_to_vanish_seconds()) -> bool:
        start_time = get_current_time_in_millis()
        is_found = self.is_element_displayed(element_to_vanish)

        while is_found and not is_time_out(start_time, timeout):
            is_found = self.is_element_displayed(element_to_vanish)

        end_time = get_current_time_in_millis()
        wait_duration_in_seconds = (end_time - start_time) / 1000
        log(DebugLevel.INFO, "The total wait for vanish time was " + str(wait_duration_in_seconds))

        return not is_found

    def scroll_to_bottom_of_element(self, element: WebElement) -> bool:
        # TODO: change to js executor
        self.actions_driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_page(self) -> bool:
        action = action_chains.ActionChains(self.actions_driver)
        action.key_down(Keys.CONTROL).send_keys(Keys.END).perform()

    # This method doesn't support multi selection
    def select_value_from_drop_down_list_by_class_name(
            self, drop_down_list: WebElement, list_items_class_name: str, values: str, list_trigger_css_selector=None) -> bool:
        class_to_css_selector = "[class='" + list_items_class_name + "']"
        return self.open_drop_down_and_select_value(drop_down_list, class_to_css_selector, values, list_trigger_css_selector)

    def open_drop_down(self, drop_down_list: WebElement, drop_down_items: list, list_trigger_css_selector=None) -> bool:
        is_displayed = self.is_element_displayed(drop_down_list)
        if not is_displayed:
            self.move_to_element(drop_down_list)
        result = False

        # Click to open the list. We wait because we need to give the list time to open
        if list_trigger_css_selector:
            result = self.click_on_sub_element_by_css_selector(drop_down_list, list_trigger_css_selector)
        if len(drop_down_items) > 0 and not result:
            result = self.click_on_element(drop_down_list)
            if not result:
                result = self.click_on_element(drop_down_items[0])
                if not result:
                    self.move_to_element(drop_down_list)
                    result = self.click_on_element(drop_down_list)

        # TODO: check if sleep can be changed to "wait for dropdown to open" - aria-expanded="false"
        time.sleep(1)
        return result

    def open_drop_down_and_select_value(
            self, drop_down_list: WebElement, list_items_css_selector: str, value: str, list_trigger_css_selector = None) -> bool:
        drop_down_items = self.get_sub_elements_by_css_selector(drop_down_list, list_items_css_selector)

        result = self.open_drop_down(drop_down_list, drop_down_items, list_trigger_css_selector)
        if not result:
            log(DebugLevel.ERROR, "Failed to open drop down list")
            return False

        return self.select_value_from_drop_down_list(drop_down_list, drop_down_items, value)

    def select_value_from_drop_down_list(
            self, drop_down_list: WebElement, drop_down_items: list, value: str) -> bool:

        for drop_down_item in drop_down_items:
            element_text = self.get_element_text(drop_down_item)
            if element_text in value:
                return self.click_on_element(drop_down_item)

        return False

    def move_to_element(self, element: WebElement) -> bool:
        # TODO: change to js executor
        self.actions_driver.execute_script("arguments[0].scrollIntoView(false);", element)

    def hover_on_element(self, element: WebElement) -> bool:
        try:
            action = action_chains.ActionChains(self.actions_driver)
            action.move_to_element(element).perform()
            return True
        except StaleElementReferenceException:
            return False

    def get_element_attribute(self, element: webelement, attribute_name: str) -> str:
        if element:
            return element.get_attribute(attribute_name)
        return ''

    def get_element_css_property(self, element: webelement, css_property: str) -> str:
        return element.value_of_css_property(css_property)

    def get_web_element_as_image(self, element: webelement):
        # TODO: change to js executor
        return self.actions_driver.execute_script(
                "return arguments[0].toDataURL('image/png').substring(21);", element)

    def click_on_item_in_list_by_css_selector(self, css_selector: str, item_text: str) -> bool:
        return self._click_on_item_in_list(By.CSS_SELECTOR, css_selector, item_text)

    def _click_on_item_in_list(self, by: By, resource_value: str, item_text: str) -> bool:
        items = self._get_elements(by, resource_value)

        for item in items:
            element_text = self.get_element_text(item)
            if item_text in element_text:
                return self.click_on_element(item)

        return False

    def get_window_handles(self) -> list:
        return self.actions_driver.window_handles

    def get_current_window_handle(self) -> str:
        return self.actions_driver.current_window_handle

    def switch_to_window_handle_by_title(self, window_title: str):
        window_handles = self.get_window_handles()
        for window_handle in window_handles:
            self.switch_to_window_handle(window_handle)
            current_page_title = self.get_page_title()
            if window_title in current_page_title:
                return True

        return False

    def switch_to_window_handle(self, required_window_handle: str) -> bool:
        self.actions_driver.switch_to.window(required_window_handle)
        current_window_handle = self.get_current_window_handle()
        return required_window_handle == current_window_handle

    def open_new_tab(self) -> bool:
        window_handles_count_before = self.get_window_handles_count()
        self.actions_driver.execute_script("window.open('');")
        window_handles_count_after = self.get_window_handles_count()
        return window_handles_count_after > window_handles_count_before

    def open_link_in_new_tab(self, link: str) -> bool:
        result = self.open_new_tab()
        if result:
            self.switch_to_new_tab()
            result = self.navigate_to_web_page(link)

        return result

    def switch_to_new_tab(self, previous_tab: str = None):
        result = self.wait_for_new_tab()
        if previous_tab:
            tabs = self.actions_driver.window_handles
            for tab in tabs:
                if tab != previous_tab:
                    self.actions_driver.switch_to.window(tab)
        else:
            self.actions_driver.switch_to.window(self.actions_driver.window_handles[-1])

    def wait_for_new_tab(self) -> bool:
        how_many_tabs_before = self.get_window_handles_count()
        how_many_tabs_after = self.get_window_handles_count()
        start_time = get_current_time_in_millis()
        while how_many_tabs_before == how_many_tabs_after and not is_time_out(start_time, self.timers.get_time_to_wait_for_new_tab_seconds()):
            print("#Before " + str(how_many_tabs_before))
            how_many_tabs_after = self.get_window_handles_count()
            print("#After " + str(how_many_tabs_before))

        return how_many_tabs_after > how_many_tabs_after

    def get_page_title(self) -> str:
        return self.actions_driver.title

    def close_current_tab(self) -> bool:
        window_handles_count_before = self.get_window_handles_count()
        if window_handles_count_before < 1:
            return False
        self.actions_driver.close()
        window_handles_count_after = self.get_window_handles_count()
        return window_handles_count_before > window_handles_count_after

    def get_window_handles_count(self) -> int:
        return len(self.get_window_handles())

    def get_element_y(self, element: webelement) -> int:
        try:
            return element.location_once_scrolled_into_view['y']
        except (StaleElementReferenceException, AttributeError):
            return -1

    def get_element_height(self, element: webelement) -> int:
        try:
            return element.size['height']
        except (StaleElementReferenceException,ElementNotInteractableException):
            return -1

    def get_window_height(self) -> int:
        return self.actions_driver.get_window_size()['height']

    def get_window_width(self) -> int:
        return self.actions_driver.get_window_size()['width']

    def scroll_y_by(self, scroll_y_by: int):
        self.actions_driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)

    def wait_for_element_to_be_within_screen(self, element: webelement) -> bool:
        current_element_y = self.get_element_y(element)
        element_height = self.get_element_height(element)
        element_total_height = current_element_y + element_height
        screen_height = self.get_window_height()

        start_time = get_current_time_in_millis()

        while element_total_height > screen_height and not is_time_out(
                start_time, self.timers.get_time_to_wait_for_element_to_load_seconds()):
            current_element_y = self.get_element_y(element)
            element_total_height = current_element_y + element_height

        return element_total_height < screen_height

    def click_escape_key(self):
        action = action_chains.ActionChains(self.actions_driver)
        action.send_keys(Keys.ESCAPE).perform()

    def click_on_element_with_javascript(self, element: webelement):
        self.actions_driver.execute_script("arguments[0].click();", element)


''' - FOR FUTURE USE
    def get_element_location_x(self, element: webelement):
        return element.location['x']

    def get_element_location_y(self, element: webelement) -> int:
        try:
            return element.location['y']
        except StaleElementReferenceException:
            return -1
            
        def click_middle_screen(self):
        window = self.actions_driver.get_window_size()
        action = action_chains.ActionChains(self.actions_driver)
        action.move_by_offset(window.get("height") / 2, window.get("width") / 2)
        action.click()
        action.perform()
'''


