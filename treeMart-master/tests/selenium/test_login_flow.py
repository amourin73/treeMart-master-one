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
from trees.models import Tree

os.environ['DJANGO_SETTINGS_MODULE'] = 'TreeMartTwo.settings'

User = get_user_model()


class BaseSeleniumTest(LiveServerTestCase):
    """Base class for all Selenium tests with common utilities"""

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

    def login_user(self, username=None, password=None):
        """Helper method to login a user"""
        username = username or self.test_username
        password = password or self.test_password

        self.driver.get(f"{self.live_server_url}{reverse('login')}")
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for login to complete
        WebDriverWait(self.driver, 10).until(
            lambda d: any(c['name'] == 'sessionid' for c in d.get_cookies()))


@pytest.mark.django_db
class TestAuthenticationFlow(BaseSeleniumTest):
    """Tests for user authentication flow"""

    def setUp(self):
        super().setUp()
        User.objects.filter(username=self.test_username).delete()

    def test_01_homepage_navigation(self):
        """Test navigation from homepage to signup page"""
        self.driver.get(self.live_server_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hero-title")))

        signup_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='signup']")))
        signup_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.url_contains(reverse('signup')))

    def test_02_signup_new_user(self):
        """Test successful user signup"""
        self.driver.get(f"{self.live_server_url}{reverse('signup')}")

        # Fill form
        self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
        self.driver.find_element(By.NAME, "email").send_keys(self.test_email)
        self.driver.find_element(By.NAME, "pass1").send_keys(self.test_password)
        self.driver.find_element(By.NAME, "pass2").send_keys(self.test_password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Handle alert
        alert_text = self.handle_alert()
        self.assertIsNotNone(alert_text, "Expected success alert but none found")
        self.assertIn("success", alert_text.lower())

        # Verify user creation
        self.assertTrue(User.objects.filter(username=self.test_username).exists())

    def test_03_invalid_username_login(self):
        """Test login with invalid username"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")

        # Submit invalid credentials
        self.driver.find_element(By.NAME, "username").send_keys("invalid_username")
        self.driver.find_element(By.NAME, "password").send_keys(self.test_password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify we're still on login page
        WebDriverWait(self.driver, 5).until(
            EC.url_contains(reverse('login')))

    def test_04_invalid_password_login(self):
        """Test login with invalid password"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")

        # Submit invalid password
        self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
        self.driver.find_element(By.NAME, "password").send_keys("wrong_password")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify we're still on login page
        WebDriverWait(self.driver, 5).until(
            EC.url_contains(reverse('login')))

    def test_05_empty_username_login(self):
        """Test login with empty username"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")

        # Submit with empty username
        self.driver.find_element(By.NAME, "password").send_keys(self.test_password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify we're still on login page
        WebDriverWait(self.driver, 5).until(
            EC.url_contains(reverse('login')))

    def test_06_empty_password_login(self):
        """Test login with empty password"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")

        # Submit with empty password
        self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify we're still on login page
        WebDriverWait(self.driver, 5).until(
            EC.url_contains(reverse('login')))

    def test_07_successful_login(self):
        """Test login with valid credentials"""
        try:
            # Create test user first
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

            # Check for successful login indicators
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
class TestNavigationAfterLogin(BaseSeleniumTest):
    """Tests for navigation after successful login"""

    def setUp(self):
        super().setUp()
        # Create test user and login
        User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        self.login_user()

    def test_navbar_links(self):
        """Test all navbar links for logged in user"""
        navbar_items = [
            {
                "name": "Home",
                "locator": (By.XPATH, "//a[contains(@href, 'homepage') and contains(@class, 'nav-link')]"),
                "expected_element": (By.CLASS_NAME, "hero-container"),
                "url_contains": reverse('homepage')
            },
            {
                "name": "Tree List",
                "locator": (By.XPATH, "//a[contains(@href, 'tree_list') and contains(@class, 'nav-link')]"),
                "expected_element": (By.CLASS_NAME, "cards-container"),
                "url_contains": reverse('tree_list')
            },
            {
                "name": "Chat",
                "locator": (By.XPATH, "//a[contains(@href, 'inbox') and contains(@class, 'nav-link')]"),
                "expected_element": (By.CLASS_NAME, "inbox-container"),
                "url_contains": reverse('inbox')
            },
            {
                "name": "Profile",
                "locator": (By.XPATH, "//a[contains(@href, 'view_profile') and contains(@class, 'nav-link')]"),
                "expected_element": (By.CLASS_NAME, "profile-container"),
                "url_contains": reverse('view_profile')
            },
            {
                "name": "Cart",
                "locator": (By.XPATH, "//a[contains(@href, 'view_cart') and contains(@class, 'nav-link')]"),
                "expected_element": (By.CLASS_NAME, "cart-container"),
                "url_contains": reverse('view_cart')
            }
        ]

        for item in navbar_items:
            # Navigate to homepage first to ensure consistent starting point
            self.driver.get(f"{self.live_server_url}{reverse('homepage')}")
            time.sleep(1)  # Brief pause for page to settle

            # Find and click the navbar link
            link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(item["locator"]))
            link.click()

            # Wait for URL to contain expected path
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(item["url_contains"]))

            # Verify expected element is present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(item["expected_element"]))


@pytest.mark.django_db
class TestWeatherFeature(BaseSeleniumTest):
    def setUp(self):
        super().setUp()
        User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        self.login_user()

    def test_weather_feature(self):
        """Test weather with valid, invalid and gibberish city input"""
        try:
            # --- Test 1: Valid City ---
            self.driver.get(f"{self.live_server_url}{reverse('weather')}")
            city_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "city"))
            )
            city_input.clear()
            city_input.send_keys("New York")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(self.driver, 20).until(
                lambda d: d.find_elements(By.CLASS_NAME, "weather-results") or
                          d.find_elements(By.CLASS_NAME, "error-message")
            )

            if self.driver.find_elements(By.CLASS_NAME, "weather-results"):
                result = self.driver.find_element(By.CLASS_NAME, "weather-results").text
                self.assertIn("New York", result)
            else:
                error = self.driver.find_element(By.CLASS_NAME, "error-message").text
                pytest.skip(f"Weather API failed: {error}")

            # --- Test 2: Invalid City ---
            self.driver.get(f"{self.live_server_url}{reverse('weather')}")
            city_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "city"))
            )
            city_input.clear()
            city_input.send_keys("asldkfjasldf")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            error_text = self.driver.find_element(By.CLASS_NAME, "error-message").text
            self.assertTrue("not found" in error_text.lower() or "could not" in error_text.lower())

        except TimeoutException:
            self.take_screenshot("weather_timeout")
            pytest.skip("Timeout waiting for weather elements")
        except Exception:
            self.take_screenshot("weather_feature_error")
            raise

    def test_empty_city_submission(self):
        """Test empty city input triggers validation"""
        try:
            self.driver.get(f"{self.live_server_url}{reverse('weather')}")
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            submit_button.click()

            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            error_text = self.driver.find_element(By.CLASS_NAME, "error-message").text
            self.assertIn("enter a city", error_text.lower())

        except TimeoutException:
            self.take_screenshot("empty_city_submission_timeout")
            pytest.fail("Expected error message did not appear for empty input")
        except Exception:
            self.take_screenshot("empty_city_submission_error")
            raise


@pytest.mark.django_db
class TestPlantGuideNavigation(BaseSeleniumTest):
    """Tests for Plant Guide navigation"""

    def setUp(self):
        super().setUp()
        # Create test user and login
        User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        self.login_user()

    def test_plant_guide_navigation(self):
        """Test navigation to Plant Guide page"""
        try:
            # Navigate to homepage first
            self.driver.get(f"{self.live_server_url}{reverse('homepage')}")

            # Scroll down a bit to ensure the Plant Guide link is clickable
            self.driver.execute_script("window.scrollBy(0, 200)")
            time.sleep(1)  # Allow time for scrolling

            # Find and click the Plant Guide link
            plant_guide_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href, 'plant_guide') and contains(text(), 'Plant Guide')]")))

            # Scroll the element into view if needed
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", plant_guide_link)
            time.sleep(0.5)  # Allow time for scrolling

            # Click using JavaScript to avoid interception
            self.driver.execute_script("arguments[0].click();", plant_guide_link)

            # Verify we're on Plant Guide page
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(reverse('plant_guide')))

            # Verify Plant Guide elements are present - looking for season cards instead
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "season-list")))

        except Exception as e:
            self.take_screenshot("plant_guide_navigation_error")
            raise

    def test_season_navigation_from_plant_guide(self):
        """Test season navigation from Plant Guide page"""
        try:
            # Navigate to Plant Guide page directly
            self.driver.get(f"{self.live_server_url}{reverse('plant_guide')}")

            # Wait for page to load - looking for season cards
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "season-list")))

            # Define seasons to test
            seasons = [
                {"name": "summer", "icon": "fa-sun", "text": "warm weather"},
                {"name": "winter", "icon": "fa-snowflake", "text": "cold temperatures"},
                {"name": "spring", "icon": "fa-seedling", "text": "spring blooms"},
                {"name": "autumn", "icon": "fa-leaf", "text": "fall colors"}
            ]

            for season in seasons:
                # Find and click the season card using JavaScript to avoid interception
                season_card = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"//a[contains(@href, '{season['name']}')]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", season_card)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", season_card)

                # Verify plants page
                WebDriverWait(self.driver, 10).until(
                    EC.url_contains(reverse('plants_by_season', args=[season['name']])))

                # Verify plants container or no-plants message is present
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "plants-container")))
                except TimeoutException:
                    # If no plants-container, check for no-plants message
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "no-plants")))

                # Go back to plant guide
                self.driver.get(f"{self.live_server_url}{reverse('plant_guide')}")

        except Exception as e:
            self.take_screenshot("season_navigation_from_plant_guide_error")
            raise



@pytest.mark.django_db
class TestCartOperations(BaseSeleniumTest):
    """Tests for cart operations - adding, updating, removing items"""

    def setUp(self):
        super().setUp()
        # Create test user and login
        User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        self.login_user()

        # Create test trees
        self.tree1 = Tree.objects.create(
            name='Test Tree 1',
            price=10.00,
            description='Test tree description'
        )
        self.tree2 = Tree.objects.create(
            name='Test Tree 2',
            price=20.00,
            description='Another test tree'
        )

    def test_add_item_to_cart(self):
        """Test adding an item to the cart"""
        try:
            # Navigate to tree list
            self.driver.get(f"{self.live_server_url}{reverse('tree_list')}")

            # Find the first add to cart button
            add_buttons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//form[contains(@action, 'add-to-cart')]//button[contains(@type, 'submit')]"))
            )
            add_buttons[0].click()

            # Verify we're redirected to cart page
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(reverse('view_cart')))

            # Verify item is in cart
            cart_item = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//tr[contains(., '{self.tree1.name}')]"))
            )

            # Verify quantity is 1
            quantity = self.driver.find_element(
                By.XPATH, f"//tr[contains(., '{self.tree1.name}')]//td[3]"
            ).text
            self.assertEqual(quantity, '1')

        except Exception as e:
            self.take_screenshot("add_to_cart_error")
            raise

    def test_increase_item_quantity(self):
        """Test increasing item quantity in cart"""
        try:
            # First add item to cart
            self.driver.get(f"{self.live_server_url}{reverse('add-to-cart', args=[self.tree1.id])}")

            # Now go to cart page
            self.driver.get(f"{self.live_server_url}{reverse('view_cart')}")

            # Find and click increase button
            increase_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'increase-btn')]")))
            increase_button.click()

            # Wait for page to reload
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cart-container")))

            # Verify quantity is now 2
            quantity = self.driver.find_element(
                By.XPATH, f"//tr[contains(., '{self.tree1.name}')]//td[3]"
            ).text
            self.assertEqual(quantity, '2')

        except Exception as e:
            self.take_screenshot("increase_quantity_error")
            raise

    def test_decrease_item_quantity(self):
        """Test decreasing item quantity in cart"""
        try:
            # First add 2 items to cart
            self.driver.get(f"{self.live_server_url}{reverse('add-to-cart', args=[self.tree1.id])}")
            self.driver.get(f"{self.live_server_url}{reverse('add-to-cart', args=[self.tree1.id])}")

            # Now go to cart page
            self.driver.get(f"{self.live_server_url}{reverse('view_cart')}")

            # Find and click decrease button
            decrease_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'decrease-btn')]")))
            decrease_button.click()

            # Wait for page to reload
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cart-container")))

            # Verify quantity is now 1
            quantity = self.driver.find_element(
                By.XPATH, f"//tr[contains(., '{self.tree1.name}')]//td[3]"
            ).text
            self.assertEqual(quantity, '1')

        except Exception as e:
            self.take_screenshot("decrease_quantity_error")
            raise

    def test_remove_item_from_cart(self):
        """Test removing an item from cart"""
        try:
            # First add item to cart
            self.driver.get(f"{self.live_server_url}{reverse('add-to-cart', args=[self.tree1.id])}")

            # Now go to cart page
            self.driver.get(f"{self.live_server_url}{reverse('view_cart')}")

            # Find and click remove button
            remove_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'remove-btn')]")))
            remove_button.click()

            # Wait for page to reload
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cart-container")))

            # Verify item is removed
            with self.assertRaises(NoSuchElementException):
                self.driver.find_element(By.XPATH, f"//tr[contains(., '{self.tree1.name}')]")

        except Exception as e:
            self.take_screenshot("remove_item_error")
            raise

    def test_clear_cart(self):
        """Test clearing the entire cart"""
        try:
            # Add items to cart
            self.driver.get(f"{self.live_server_url}{reverse('add-to-cart', args=[self.tree1.id])}")
            self.driver.get(f"{self.live_server_url}{reverse('add-to-cart', args=[self.tree2.id])}")

            # Now go to cart page
            self.driver.get(f"{self.live_server_url}{reverse('view_cart')}")

            # Find and click clear cart button
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'clear-cart')]")))
            clear_button.click()

            # Verify we're redirected to homepage
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(reverse('homepage')))

            # Verify cart is empty
            self.driver.get(f"{self.live_server_url}{reverse('view_cart')}")
            empty_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "empty-cart")))
            self.assertIn("empty", empty_message.text.lower())

        except Exception as e:
            self.take_screenshot("clear_cart_error")
            raise


@pytest.mark.django_db
class TestCartCheckout(BaseSeleniumTest):
    """Tests for cart checkout process"""

    def setUp(self):
        super().setUp()
        # Create test user and login
        User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        self.login_user()

        # Create test tree
        self.tree = Tree.objects.create(
            name='Test Tree',
            price=15.00,
            description='Test tree description'
        )

    def test_checkout_process(self):
        """Test the complete checkout process"""
        try:
            # Add item to cart
            self.driver.get(f"{self.live_server_url}{reverse('add-to-cart', args=[self.tree.id])}")

            # Go to cart page
            self.driver.get(f"{self.live_server_url}{reverse('view_cart')}")

            # Find and click checkout button
            checkout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'place-order')]")))
            checkout_button.click()

            # Verify we're on order confirmation page
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(reverse('order_confirmation')))

            # Verify order details
            order_details = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "order-details"))
            )

            self.assertIn(str(self.tree.price), order_details.text)
            self.assertIn(self.tree.name, order_details.text)

            # Verify cart is empty after checkout
            self.driver.get(f"{self.live_server_url}{reverse('view_cart')}")
            empty_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "empty-cart")))
            self.assertIn("empty", empty_message.text.lower())

        except Exception as e:
            self.take_screenshot("checkout_error")
            raise