from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.webdriver import Options
import os
import time
import selenium.common.exceptions
from datetime import datetime
import re
import pandas as pd
from spread_calculator import SpreadBackGenerator
import csv
from enter_credential import SpreadChartLogin 
from enter_spread import ButtonClicker
from selenium.webdriver.common.keys import Keys

# ---------------------- CONFIGURATION ----------------------
ahk_script_path = r"C:\Users\Administrator\Desktop\spreadchart\enterspread.ahk"
enter_credential_script_path = r"C:\Users\Administrator\Desktop\spreadchart\enter credential .ahk"
filename = r"C:\Users\Administrator\Desktop\spreadchart\Output_file.csv"
EMAIL = ""
PASSWORD = ""

sucessfull_login = False

# ---------------------- INIT DRIVER ----------------------

chrome_options = Options()
# chrome_options.add_argument("--start-maximized") 
# chrome_options.add_argument('--headless')  # Run Chrome in headless mode
# chrome_options.add_argument('--disable-gpu')  # Optional: avoids GPU issues on some systems
# chrome_options.add_argument('--window-size=1920,1080')  # Optional: set screen size for rendering
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions") 
chrome_options.add_argument("--disable-popup-blocking") 
chrome_options.add_argument("--no-sandbox") 
chrome_options.add_argument("--disable-dev-shm-usage") 
chrome_options.add_argument("--incognito") 

chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

driver.set_page_load_timeout(60) 
driver.implicitly_wait(10) 
overall_open_value = None
overall_close_value = None
overall_high = float("-inf")
overall_low = float("inf")

def append_to_csv(filename, line_to_write):
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as file:
        file.write(line_to_write)

try:
    print("[i] Navigating to URL...")
    driver.get('https://app.spreadcharts.com/')
    
    # --- Ensure window is active and visible ---
    driver.switch_to.window(driver.current_window_handle) # Switch to the current window handle
    driver.set_window_position(0, 0) # Move window to top-left corner
    # driver.fullscreen_window() # Ensure browser is fullscreen after navigation

    # Inject JavaScript to try and hide automation flag (if website checks window.navigator.webdriver)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    session = driver.execute_cdp_cmd
    print("[i] Waiting for initial page JavaScript to execute...")
    time.sleep(5) 

    # ---------------------- RUN AHK SCRIPTS ----------------------
    print("[i] Running enter credential script...") 

    login_manager = SpreadChartLogin(driver, EMAIL, PASSWORD)
    login_manager.login()
    time.sleep(2) 
    sucessfull_login = True

    def draw_marker(driver, chart_element, x_offset, y_offset, color='blue'):
         driver.execute_script("""
        const marker = document.createElement('div');
        marker.className = 'hover-marker';
        marker.style.position = 'absolute';
        marker.style.zIndex = '9999';
        marker.style.width = '6px';
        marker.style.height = '6px';
        marker.style.borderRadius = '50%';
        marker.style.backgroundColor = arguments[3];

        const rect = arguments[0].getBoundingClientRect();
        marker.style.left = (rect.left + arguments[1]) + 'px';
        marker.style.top = (rect.top + arguments[2]) + 'px';

        document.body.appendChild(marker);
        """, chart_element, x_offset, y_offset, color)
         
    driver.execute_script("""
        let counter = document.getElementById('counter-div');
        if (!counter) {
            counter = document.createElement('div');
            counter.id = 'counter-div';
            document.body.appendChild(counter);
        }

        counter.innerText = 'Waiting...';
        counter.style.position = 'fixed';
        counter.style.top = '10px';
        counter.style.left = '10px';
        counter.style.padding = '15px 25px';
        counter.style.fontSize = '22px';
        counter.style.backgroundColor = 'yellow';
        counter.style.color = 'black';
        counter.style.zIndex = '999999999';  // max z-index
        counter.style.border = '4px solid red';
        counter.style.borderRadius = '10px';
        counter.style.boxShadow = '0 0 20px red';
        counter.style.pointerEvents = 'none';
        counter.style.display = 'block';
    """)


    print("[DEBUG] Injecting counter...")
    driver.execute_script("""
        let counter = document.createElement('div');
        counter.id = 'counter-div';
        counter.innerText = 'Ready';
        counter.style.cssText = `
            position: fixed;
            top: 20px;
            left: 20px;
            background: lime;
            color: black;
            padding: 10px 20px;
            font-size: 20px;
            border: 3px solid black;
            z-index: 999999;
            pointer-events: none;
        `;
        document.body.appendChild(counter);
    """)

    # ---------------------- SETUP ----------------------
    os.makedirs("chart_debug_screens", exist_ok=True)

    wait = WebDriverWait(driver, 10) # Increased to 10 seconds for tooltip visibility
    spread_pair = ""
    # ---------------------- DATA EXTRACTION ----------------------
    spread_file = pd.read_csv(r"C:\Users\Administrator\Desktop\spreadchart\spread_file.csv")
    main_spread_list = spread_file['Spread'].unique()
    counter = 0
    for main_spread in main_spread_list:
        print("counter : " , counter + 1)

        trade = spread_file['Trade'].iloc[counter] 
        counter += 1
        append_to_csv(filename=filename,line_to_write="\n")
        
        print(main_spread)
        # print("Spread","Open","High","Low","Close")

        append_to_csv(filename=filename,line_to_write=main_spread)
        append_to_csv(filename=filename,line_to_write="\nSpread,Trade,Open,High,Low,Close")

        sample_date = "Jan 01, 2028"
        parsed_date = datetime.strptime(sample_date, "%b %d, %Y")

        generator = SpreadBackGenerator(main_spread)
        back_date_spreads_list = generator.generate(8)
        back_date_spreads_list.insert(0, main_spread)
        # print(back_date_spreads_list)
        for spread in back_date_spreads_list:
            # print("spread",spread)
            match_1 = re.match(r'[-+]?\s*\d+\*\w{3}\d{2}', spread)
            if match_1:
                first_contract = match_1.group(0)

            data_dict = {}
            date_list = []
            value_list = []
            last_value = None
            ExitDate_confirmed = False
            cutoff_date = datetime.strptime("Jan 01, 2001", "%b %d, %Y")

            

            print("[i] Running spread entry script...")
            clicker = ButtonClicker(driver)
            spread_entry = clicker.click_and_enter(spread,sucessfull_login)
            time.sleep(1) 

            driver.execute_script("""
            let counter = document.getElementById('counter-div');
            if (!counter) {
                counter = document.createElement('div');
                counter.id = 'counter-div';
                document.body.appendChild(counter);
            }
            counter.innerText = 'Loading...';
            counter.style.cssText = `
                position: fixed;
                top: 20px;
                left: 20px;
                background: yellow;
                color: black;
                padding: 10px 20px;
                font-size: 20px;
                border: 3px solid red;
                z-index: 999999;
                pointer-events: none;
                display: block;
                `;
            """)

            driver.execute_script("""
                const counter = document.getElementById('counter-div');
                if (counter) {
                    counter.innerText = 'Spread #' + arguments[0];
                }
            """, counter)

            driver.execute_script("""
                const counter = document.getElementById('counter-div');
                if (counter) {
                    counter.style.border = '3px solid red';
                }
            """)



            driver.execute_script("""
            if (!document.getElementById('mouse-dot')) {
                const dot = document.createElement('div');
                dot.id = 'mouse-dot';
                dot.style.position = 'fixed';
                dot.style.width = '10px';
                dot.style.height = '10px';
                dot.style.borderRadius = '50%';
                dot.style.background = 'red';
                dot.style.zIndex = 9999;
                dot.style.pointerEvents = 'none';
                document.body.appendChild(dot);
            }
            """)
            chart = driver.find_elements(By.CLASS_NAME, 'chart-wrapper')
            # driver.execute_script("""
            #     arguments[0].style.border='3px solid red';
            #     arguments[0].style.backgroundColor='rgba(255,0,0,0.2)';
            # """, chart[0])
            chart_element = chart[0]
            chart_x = chart_element.location['x']
            chart_y = chart_element.location['y']
            # print("chart size :" , chart[0].size)

            for x in range(chart_element.size['width']-75, 0, -1):
                try:   
                    abs_x = chart_x + x
                    abs_y = chart_y + 300

                    driver.execute_script("""
                        const dot = document.getElementById('mouse-dot');
                        if (dot) {
                            dot.style.left = arguments[0] + 'px';
                            dot.style.top = arguments[1] + 'px';
                        }
                    """, abs_x, abs_y)

                    session("Input.dispatchMouseEvent", {
                        "type": "mouseMoved",
                        "x": abs_x,
                        "y": abs_y,
                        "button": "none"
                    })
                    try:
                        date_div = wait.until(EC.visibility_of_element_located(
                            (By.CLASS_NAME, "amcharts-chart-div")
                        ))
                    except selenium.common.exceptions.TimeoutException:
                        print(f"[!] Tooltip not visible at x={x}, skipping...")
                        driver.save_screenshot(f"chart_debug_screens/no_tooltip_x{x}.png")
                        continue
                    
                    text = date_div.text.strip()
                    if text :
                        parts = text.split('\n')

                        for part in parts:
                            part = part.strip()

                            if ":" in part and any(char.isdigit() for char in part):
                                spread_pair = part.split(":")[0]
                                last_value = part.split(":")[-1].strip()

                            elif last_value is not None and "," in part:
                                # print("Saved:", spread_pair, part, last_value)
                                parsed_date = datetime.strptime(part, "%b %d, %Y")
                                # print("parsed_date" , parsed_date) 
                                date_list.append(parsed_date)
                                value_list.append(last_value)

                                if("Sep" in part):
                                    ExitDate_confirmed = True
                                    cutoff_date_exit = datetime.strptime(part, "%b %d, %Y")

                                if(ExitDate_confirmed and "Jul" in part):
                                    cutoff_date_entry = datetime.strptime(part, "%b %d, %Y")

                                if(ExitDate_confirmed and "Jun" in part):
                                    cutoff_date = datetime.strptime(part, "%b %d, %Y")
                                    

                    # print("cutoff_date",cutoff_date)
                    if parsed_date <= cutoff_date:
                        print(f"Reached cutoff: {part} at x={x}")
                        data_dict["Date"] = date_list
                        data_dict["Value"] = value_list

                        data_df = pd.DataFrame(data_dict)
                        data_df["Value"] = data_df['Value'].astype("float")

                        # print(data_df)
                        data_df['Date'] = pd.to_datetime(data_df['Date'])
                        filtered_df = data_df[(data_df['Date'] >= cutoff_date_entry) & (data_df['Date'] <= cutoff_date_exit)].copy()
                        # print(filtered_df)
                        if not filtered_df.empty:
                            filtered_df.sort_values(by = "Date" , inplace=True)
                            filtered_df.reset_index(drop=True,inplace=True)
                            # filtered_df.to_csv("temp.csv")
                            overall_open_value = filtered_df['Value'].iloc[0]
                            overall_close_value= filtered_df['Value'].iloc[-1]
                            overall_high = filtered_df['Value'].max()
                            # print("max index ",filtered_df['Value'].idxmax())
                            # print("min index ",filtered_df['Value'].idxmin())

                            overall_low  = filtered_df['Value'].min()
                        break
                
                except selenium.common.exceptions.MoveTargetOutOfBoundsException:
                    print(f"[!] Skipped invalid offset (MoveTargetOutOfBoundsException): x={x}")
                    continue
                except Exception as e:
                    print(f"[!] General error at x={x}: {e}")
                    continue

            line_to_write_ = f"\n{spread_pair},{trade},{(overall_open_value)},{(overall_high)},{(overall_low)},{(overall_close_value)}" 
            append_to_csv(filename=filename,line_to_write=line_to_write_)
            # print(line_to_write_)

except selenium.common.exceptions.TimeoutException:
    print("[CRITICAL] Page did not load within the specified timeout. Check URL or network.")
except Exception as e:
    print(f"[CRITICAL] An error occurred during initial setup or navigation: {e}")

finally:
    driver.quit()

