from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException



class ButtonClicker:
    def __init__(self, driver, timeout=35):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def slow_type(self, element, text, delay=0.05):
        for char in text:
            element.send_keys(char)
            time.sleep(delay)

    def click_and_enter(self, text, sucessfull_login ,delay=0.05):
        
        self.driver.refresh()
        time.sleep(1)

        graph_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Charts']/ancestor::li"))
        )
        graph_button.click()
        time.sleep(1)

        enter_spread = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"][autocomplete="off"]'))
        )
        time.sleep(1)

        enter_spread.send_keys(Keys.CONTROL, 'a')

        self.slow_type(enter_spread, text, delay)

        select_price = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='actionValue' and contains(text(), 'Seasonality')]"))
        )
        select_price.click()
        time.sleep(0.5)

        price_toggle = self.driver.find_element(
            By.XPATH,
            "//div[@class='label-wrapper' and normalize-space(text())='Price']"
        )
        price_toggle.click()
        time.sleep(0.5)

        price_underlyings = self.driver.find_element(
            By.XPATH,
            "//div[@class='label-wrapper' and normalize-space(text())='Price & underlyings']"
        )
        price_underlyings.click()

        chart_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.chartInput.button-green[value='Chart']"))
        )
        chart_button.click()
        time.sleep(1)

        button_2y = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='tool-button' and normalize-space()='2Y']"))
        )
        time.sleep(1)

        self.driver.execute_script("arguments[0].scrollIntoView(true);", button_2y)

        self.driver.execute_script("arguments[0].click();", button_2y)

        time.sleep(1)

        delete_icons = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "i.icons8-delete-2"))
        )

        target_icon = delete_icons[4]

        target_icon.click()

        time.sleep(1)
