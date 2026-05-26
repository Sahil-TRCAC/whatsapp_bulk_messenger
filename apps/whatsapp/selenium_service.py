import os
import time
import base64
import threading
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class WhatsAppSeleniumService:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.driver = None
        self.status = 'disconnected'
        self.phone = None
        self.name = None
        self._monitor_thread = None

    def start_driver(self):
        if self.driver:
            return

        self.status = 'loading'
        logger.info('Starting Chrome driver for WhatsApp Web')

        try:
            options = webdriver.ChromeOptions()
            session_dir = os.path.join(os.getcwd(), '.whatsapp_session')
            options.add_argument(f'--user-data-dir={session_dir}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--window-size=1280,800')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)

            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
            except Exception:
                service = Service()

            self.driver = webdriver.Chrome(
                service=service,
                options=options
            )
            self.driver.get('https://web.whatsapp.com')
            self.status = 'scanning'

            self._monitor_thread = threading.Thread(target=self._monitor_login, daemon=True)
            self._monitor_thread.start()
            logger.info('Chrome driver started, waiting for QR scan')

        except Exception as e:
            logger.error(f'Failed to start Chrome driver: {e}')
            self.status = 'disconnected'
            raise

    def _monitor_login(self):
        while True:
            try:
                if self.driver is None:
                    self.status = 'disconnected'
                    break

                if self.is_logged_in():
                    self.status = 'connected'
                    self._fetch_connected_info()
                    logger.info('WhatsApp Web login detected')
                    break
                else:
                    if self.status == 'connected':
                        self.status = 'scanning'
            except Exception as e:
                logger.warning(f'Monitor login error: {e}')
                if self.driver is None:
                    self.status = 'disconnected'
                    break
            time.sleep(2)

    def _fetch_connected_info(self):
        try:
            time.sleep(2)
            header = self.driver.find_element(By.CSS_SELECTOR, 'header')
            title_elem = header.find_element(By.CSS_SELECTOR, 'span[data-testid="conversation-info-header"]')
            if title_elem:
                self.name = title_elem.text

            self.phone = 'Connected'
        except Exception:
            self.name = 'WhatsApp User'
            self.phone = 'Connected'

    def get_qr_code(self):
        if self.driver is None or self.status != 'scanning':
            return None
        try:
            time.sleep(1)
            canvas = self.driver.find_element(By.CSS_SELECTOR, 'canvas')
            return canvas.screenshot_as_base64
        except NoSuchElementException:
            try:
                return self.driver.get_screenshot_as_base64()
            except Exception:
                return None
        except Exception:
            return None

    def is_logged_in(self):
        indicators = [
            '[data-testid="chat-list-search"]',
            '[data-testid="search"]',
            '[data-testid="chat-list"]',
            'div[aria-label="Chat list"]',
            'div[data-testid="conversation-panel"]',
            'input[aria-label*="Search"]',
            'header[data-testid="sidebar"]',
            'div[role="navigation"]',
            'div[aria-label="New chat"]',
        ]
        for selector in indicators:
            try:
                self.driver.find_element(By.CSS_SELECTOR, selector)
                return True
            except NoSuchElementException:
                continue

        try:
            canvases = self.driver.find_elements(By.CSS_SELECTOR, 'canvas')
            if len(canvases) == 0:
                return True
        except Exception:
            pass

        return False

    def _find_input_box(self):
        selectors = [
            '[data-testid="conversation-compose-box-input"]',
            'div[contenteditable="true"][aria-label*="Type"]',
            'div[contenteditable="true"][aria-placeholder*="Type"]',
            'div[contenteditable="true"]',
        ]
        for selector in selectors:
            try:
                return self.driver.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                continue
        return None

    def _wait_for_chat_load(self):
        selectors = [
            '[data-testid="conversation-compose-box-input"]',
            'div[contenteditable="true"]',
            'div[aria-label*="Type"]',
            'footer',
        ]
        for selector in selectors:
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                return True
            except TimeoutException:
                continue
        raise Exception('Failed to open chat - invalid number or timeout')

    def _search_and_open_chat(self, phone):
        search_selectors = [
            '[data-testid="chat-list-search"]',
            '[data-testid="search"]',
            'input[aria-label*="Search"]',
            'div[contenteditable="true"][aria-label*="Search"]',
        ]
        search_box = None
        for sel in search_selectors:
            try:
                search_box = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                break
            except (TimeoutException, NoSuchElementException):
                continue

        if not search_box:
            raise Exception('Could not find search box')

        search_box.click()
        time.sleep(0.5)

        try:
            search_box.clear()
        except Exception:
            pass
        time.sleep(0.3)

        search_box.send_keys(phone)
        time.sleep(3)

        search_box.send_keys(Keys.ENTER)
        time.sleep(2)

        chat_selectors = [
            '[data-testid="conversation-panel"]',
            '[data-testid="conversation-compose-box-input"]',
            'div[contenteditable="true"]',
            'footer',
        ]
        for sel in chat_selectors:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
                return
            except (TimeoutException, NoSuchElementException):
                continue

        result_selectors = [
            'div[aria-label*="Search results"] div[role="button"]',
            'div[data-testid="chat-list"] div[role="button"]',
            'div[role="option"]',
            'div[role="listitem"]',
        ]
        for sel in result_selectors:
            try:
                items = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if items:
                    items[0].click()
                    time.sleep(2)
                    for check in chat_selectors:
                        try:
                            WebDriverWait(self.driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, check))
                            )
                            return
                        except (TimeoutException, NoSuchElementException):
                            continue
            except NoSuchElementException:
                continue

        raise Exception(f'Could not open chat for {phone}')

    def _type_and_send(self, message):
        box = self._find_input_box()
        if not box:
            raise Exception('Could not find message input box')

        box.click()
        time.sleep(0.3)
        box.send_keys(message)
        time.sleep(0.5)

        send_selectors = [
            '[data-testid="compose-btn-send"]',
            '[data-testid="conversation-send"]',
            'button[aria-label="Send"]',
            'span[data-icon="send"]',
        ]
        sent = False
        for sel in send_selectors:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                btn.click()
                sent = True
                break
            except NoSuchElementException:
                continue

        if not sent:
            box.send_keys(Keys.ENTER)

        time.sleep(2)

    def send_text(self, phone, message):
        if self.driver is None or self.status != 'connected':
            raise Exception('WhatsApp is not connected')

        try:
            self._search_and_open_chat(phone)
            self._type_and_send(message)
            logger.info(f'Message sent to {phone}')
        except Exception as e:
            raise Exception(f'Failed to send message: {e}')

    def send_image(self, phone, image_path, caption=''):
        if self.driver is None or self.status != 'connected':
            raise Exception('WhatsApp is not connected')

        try:
            self._search_and_open_chat(phone)

            clip_selectors = [
                '[data-testid="conversation-clip"]',
                'button[aria-label="Attach"]',
                'span[data-icon="clip"]',
                'div[title="Attach"]',
            ]
            clicked = False
            for sel in clip_selectors:
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                    btn.click()
                    clicked = True
                    break
                except NoSuchElementException:
                    continue
            if not clicked:
                raise Exception('Could not find attach button')

            time.sleep(1)

            file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(os.path.abspath(image_path))
            time.sleep(3)

            if caption:
                caption_selectors = [
                    '[data-testid="conversation-caption-input"]',
                    'div[contenteditable="true"][aria-label*="caption"]',
                    'div[contenteditable="true"][aria-placeholder*="Add"]',
                ]
                for sel in caption_selectors:
                    try:
                        cb = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                        )
                        cb.click()
                        cb.send_keys(caption)
                        break
                    except (TimeoutException, NoSuchElementException):
                        continue

                time.sleep(1)

            send_selectors = [
                '[data-testid="conversation-send"]',
                'button[aria-label="Send"]',
                'span[data-icon="send"]',
            ]
            sent = False
            for sel in send_selectors:
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                    btn.click()
                    sent = True
                    break
                except NoSuchElementException:
                    continue

            if not sent:
                raise Exception('Could not find send button')

            time.sleep(3)
            logger.info(f'Image sent to {phone}')
        except Exception as e:
            raise Exception(f'Failed to send image: {e}')

    def stop_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        self.status = 'disconnected'
        self.phone = None
        self.name = None
        logger.info('Chrome driver stopped')
        try:
            import subprocess
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
            subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], capture_output=True)
        except Exception:
            pass


whatsapp_service = WhatsAppSeleniumService()
