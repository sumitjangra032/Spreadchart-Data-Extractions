from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SpreadChartLogin:
    def __init__(self, driver, email, password, timeout=20):
        self.driver = driver
        self.email = email
        self.password = password
        self.wait = WebDriverWait(driver, timeout)

    def slow_type(self,element, text, delay=0.05):
        for char in text:
            element.send_keys(char)
            time.sleep(delay)

    def login(self):

        login_button = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "user-clicker"))
        )
        login_button.click()

        email_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"][autocomplete="email"]'))
        )
        password_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"][autocomplete="current-password"]'))
        )

        self.slow_type(email_input, self.email)
        self.slow_type(password_input, self.password)

        time.sleep(1)
        password_input.send_keys(Keys.RETURN)

        # self.driver.maximize_window()
        print("✅ Login successful!")
