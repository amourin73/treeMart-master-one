import os
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException,
                                        UnexpectedAlertPresentException)
from django.urls import reverse
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model

os.environ['DJANGO_SETTINGS_MODULE'] = 'TreeMartTwo.settings'

User = get_user_model()


@pytest.mark.django_db
class TestUserAuthentication(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = webdriver.ChromeOptions()
        if os.environ.get('HEADLESS') == 'True':
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(2)
        cls.test_username = "testuser_" + str(int(time.time()))
        cls.test_password = "SecurePassword123!"
        cls.test_email = f"{cls.test_username}@example.com"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Reset browser state between tests"""
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass
        self.driver.delete_all_cookies()
        User.objects.filter(username=self.test_username).delete()

    def handle_alert(self):
        """Handle alert without failing the test"""
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return alert_text
        except:
            return None

    def take_screenshot(self, name):
        """Helper method to take screenshots"""
        screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"{name}_{int(time.time())}.png")
        self.driver.save_screenshot(screenshot_path)
        return screenshot_path

    def test_0_homepage_navigation(self):
        """Test navigation from homepage to signup page"""
        try:
            self.driver.get(self.live_server_url)
            WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hero-title"))
            )
            signup_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='signup']"))
            )
            signup_button.click()
            WebDriverWait(self.driver, 2).until(
                EC.url_contains(reverse('signup')))
        except Exception as e:
            self.take_screenshot("homepage_navigation_error")
            raise

    def test_1_signup_new_user(self):
        """Test successful user signup"""
        try:
            self.driver.get(f"{self.live_server_url}{reverse('signup')}")

            # Fill form
            self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
            self.driver.find_element(By.NAME, "email").send_keys(self.test_email)
            self.driver.find_element(By.NAME, "pass1").send_keys(self.test_password)
            self.driver.find_element(By.NAME, "pass2").send_keys(self.test_password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Handle alert first before any other checks
            alert_text = self.handle_alert()
            self.assertIsNotNone(alert_text, "Expected success alert but none found")
            self.assertIn("success", alert_text.lower())

            # Verify user creation
            self.assertTrue(User.objects.filter(username=self.test_username).exists())

        except Exception as e:
            self.take_screenshot("signup_error")
            raise

    def test_2_invalid_username_login(self):
        """Test login with invalid username"""
        try:
            self.driver.get(f"{self.live_server_url}{reverse('login')}")

            # Submit invalid credentials quickly
            self.driver.find_element(By.NAME, "username").send_keys("invalid_username")
            self.driver.find_element(By.NAME, "password").send_keys(self.test_password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Just verify we're still on login page
            time.sleep(0.5)  # Brief pause for any JS
            self.assertTrue(reverse('login') in self.driver.current_url)
        except Exception as e:
            self.take_screenshot("invalid_username_login_error")
            raise

    def test_3_invalid_password_login(self):
        """Test login with invalid password"""
        try:
            User.objects.create_user(
                username=self.test_username,
                email=self.test_email,
                password=self.test_password
            )

            self.driver.get(f"{self.live_server_url}{reverse('login')}")

            # Submit invalid password quickly
            self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
            self.driver.find_element(By.NAME, "password").send_keys("wrong_password")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Just verify we're still on login page
            time.sleep(0.5)  # Brief pause for any JS
            self.assertTrue(reverse('login') in self.driver.current_url)
        except Exception as e:
            self.take_screenshot("invalid_password_login_error")
            raise

    def test_4_empty_username_login(self):
        """Test login with empty username"""
        try:
            self.driver.get(f"{self.live_server_url}{reverse('login')}")

            # Submit with empty username
            self.driver.find_element(By.NAME, "password").send_keys(self.test_password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Just verify we're still on login page
            time.sleep(0.5)
            self.assertTrue(reverse('login') in self.driver.current_url)
        except Exception as e:
            self.take_screenshot("empty_username_login_error")
            raise

    def test_5_empty_password_login(self):
        """Test login with empty password"""
        try:
            User.objects.create_user(
                username=self.test_username,
                email=self.test_email,
                password=self.test_password
            )

            self.driver.get(f"{self.live_server_url}{reverse('login')}")

            # Submit with empty password
            self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Just verify we're still on login page
            time.sleep(0.5)
            self.assertTrue(reverse('login') in self.driver.current_url)
        except Exception as e:
            self.take_screenshot("empty_password_login_error")
            raise

    def test_6_successful_login(self):
        """Test login with valid credentials"""
        try:
            User.objects.create_user(
                username=self.test_username,
                email=self.test_email,
                password=self.test_password
            )

            self.driver.get(f"{self.live_server_url}{reverse('login')}")

            # Submit valid credentials
            self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
            self.driver.find_element(By.NAME, "password").send_keys(self.test_password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Check for either homepage or any page with logout link
            WebDriverWait(self.driver, 10).until(
                lambda d: d.current_url == f"{self.live_server_url}{reverse('homepage')}" or
                          len(d.find_elements(By.PARTIAL_LINK_TEXT, "Logout")) > 0 or
                          any(c['name'] == 'sessionid' for c in d.get_cookies())
            )

            # Verify session cookie exists
            self.assertTrue(any(c['name'] == 'sessionid' for c in self.driver.get_cookies()))
        except Exception as e:
            self.take_screenshot("successful_login_error")
            raise


@pytest.mark.django_db
class TestNavbarNavigation(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = webdriver.ChromeOptions()
        if os.environ.get('HEADLESS') == 'True':
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(2)
        cls.test_username = "testuser_" + str(int(time.time()))
        cls.test_password = "SecurePassword123!"
        cls.test_email = f"{cls.test_username}@example.com"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Reset browser state and login before each test"""
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass

        # Clear cookies and existing user
        self.driver.delete_all_cookies()
        User.objects.filter(username=self.test_username).delete()

        # Create test user
        User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )

        # Perform login
        self.driver.get(f"{self.live_server_url}{reverse('login')}")
        self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
        self.driver.find_element(By.NAME, "password").send_keys(self.test_password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for login to complete
        WebDriverWait(self.driver, 5).until(
            lambda d: any(c['name'] == 'sessionid' for c in d.get_cookies()))

        # Start each test from homepage
        self.driver.get(f"{self.live_server_url}{reverse('homepage')}")

    def test_7_navbar_home_link(self):
        """Test Home link in navbar"""
        try:
            # Find Home link in navbar and click it
            home_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Home')]"))
            )
            home_link.click()

            # Verify we're on homepage
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hero-title")))
            self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('homepage')}")

        except Exception as e:
            self.driver.save_screenshot("navbar_home_error.png")
            raise

    def test_8_navbar_tree_list_link(self):
        """Test Tree List link in navbar"""
        try:
            # Find Tree List link in navbar and click it
            tree_list_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Tree List')]"))
            )
            tree_list_link.click()

            # Verify we're on tree list page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "section-title")))
            self.assertIn(reverse('tree_list'), self.driver.current_url)

        except Exception as e:
            self.driver.save_screenshot("navbar_tree_list_error.png")
            raise

    def test_9_navbar_plant_guide_link(self):
        """Test Plant Guide link in navbar"""
        try:
            # Find Plant Guide link in navbar and click it
            plant_guide_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Plant Guide')]"))
            )
            plant_guide_link.click()

            # Verify we're on plant guide page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "section-title")))
            self.assertIn(reverse('plant_guide'), self.driver.current_url)

        except Exception as e:
            self.driver.save_screenshot("navbar_plant_guide_error.png")
            raise

    def test_10_navbar_chat_link(self):
        """Test Chat link in navbar (authenticated user)"""
        try:
            # Find Chat link in navbar and click it
            chat_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Chat')]"))
            )
            chat_link.click()

            # Verify we're on chat page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat-container")))
            self.assertIn(reverse('inbox'), self.driver.current_url)

        except Exception as e:
            self.driver.save_screenshot("navbar_chat_error.png")
            raise

    def test_11_navbar_profile_link(self):
        """Test Profile link in navbar (authenticated user)"""
        try:
            # Find Profile link in navbar and click it
            profile_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Profile')]"))
            )
            profile_link.click()

            # Verify we're on profile page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "profile-container")))
            self.assertIn(reverse('view_profile'), self.driver.current_url)

        except Exception as e:
            self.driver.save_screenshot("navbar_profile_error.png")
            raise

    def test_12_navbar_cart_link(self):
        """Test Cart link in navbar (authenticated user)"""
        try:
            # Find Cart link in navbar and click it
            cart_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Cart')]"))
            )
            cart_link.click()

            # Verify we're on cart page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cart-container")))
            self.assertIn(reverse('view_cart'), self.driver.current_url)

        except Exception as e:
            self.driver.save_screenshot("navbar_cart_error.png")
            raise

    def test_13_navbar_features_link(self):
        """Test Features link in navbar"""
        try:
            # Find Features link in navbar and click it
            features_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Features')]"))
            )
            features_link.click()

            # Verify we're on features page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "features-container")))
            self.assertIn(reverse('weather'), self.driver.current_url)

        except Exception as e:
            self.driver.save_screenshot("navbar_features_error.png")
            raise

    def test_14_navbar_signup_login_links_logged_out(self):
        """Test Sign Up and Sign In links in navbar when logged out"""
        try:
            # First log out
            logout_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Logout')]"))
            )
            logout_link.click()

            # Wait for logout to complete
            WebDriverWait(self.driver, 5).until(
                lambda d: not any(c['name'] == 'sessionid' for c in d.get_cookies()))

            # Find Sign Up link in navbar and click it
            signup_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Sign Up')]"))
            )
            signup_link.click()

            # Verify we're on signup page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "signup-form")))
            self.assertIn(reverse('signup'), self.driver.current_url)

            # Go back to homepage
            self.driver.get(f"{self.live_server_url}{reverse('homepage')}")

            # Find Sign In link in navbar and click it
            signin_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Sign In')]"))
            )
            signin_link.click()

            # Verify we're on login page
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "login-form")))
            self.assertIn(reverse('login'), self.driver.current_url)

        except Exception as e:
            self.driver.save_screenshot("navbar_auth_links_error.png")
            raise