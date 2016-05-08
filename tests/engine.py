from hitchserve import ServiceBundle
from os import path, system, chdir, remove
from os.path import expanduser
from subprocess import check_call, PIPE
from selenium.common.exceptions import NoSuchElementException
import hitchpostgres
import hitchselenium
import hitchpython
import hitchserve
import hitchsmtp
import hitchtest
import json
import urllib
import datetime
import sqlite3


# Get directory above this file
PROJECT_DIRECTORY = path.abspath(path.join(path.dirname(__file__), '..'))

class ExecutionEngine(hitchtest.ExecutionEngine):
    """Python engine for running tests."""

    def set_up(self):
        """Set up your applications and the test environment."""
        self.python_package = hitchpython.PythonPackage(
            python_version=self.settings['python_version']
        )
        self.python_package.build()
        self.python_package.verify()

        check_call([
            self.python_package.pip, "install", "-r",
            path.join(PROJECT_DIRECTORY, "requirements.txt")
        ])

        self.turkeydb_file = path.join(hitchtest.utils.get_hitch_directory(), "turkey-test.db")
        self.turkeydb_file_pre_existing = True
        self.turkey_conf_file = path.join(PROJECT_DIRECTORY, "turkey-test.conf")

        assert not path.exists(self.turkeydb_file), (
            "Test turkeyDB already exists at {path}, "
            "please move or delete.".format(
                path=self.turkeydb_file,
            )
        )
        self.turkeydb_file_pre_existing = False

        with open(self.turkey_conf_file, "w") as turkey_conf:
            turkey_conf.write(json.dumps({
                "SECRET_KEY": "xxx",
                "LISTEN_IP": "127.0.0.1",
                "LISTEN_PORT": 5000,
                "DEBUG": False,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///{}".format(self.turkeydb_file)
            }))

        chdir(PROJECT_DIRECTORY)
        check_call([self.python_package.python, "manage.py", "db", "upgrade"])

        self.services = ServiceBundle(
            project_directory=PROJECT_DIRECTORY,
            startup_timeout=float(self.settings["startup_timeout"]),
            shutdown_timeout=float(self.settings["shutdown_timeout"]),
        )

        # Docs : https://hitchtest.readthedocs.org/en/latest/plugins/hitchsmtp.html
        self.services['HitchSMTP'] = hitchsmtp.HitchSMTPService(port=10025)

        # Docs : https://hitchtest.readthedocs.org/en/latest/plugins/hitchpython.html
        self.services['Flask'] = hitchserve.Service(
            command=[self.python_package.python, "manage.py", "runserver", ],
            directory=PROJECT_DIRECTORY,
            needs=[],
            log_line_ready_checker=lambda line: "Running on" in line,
        )

        # Docs : https://hitchtest.readthedocs.org/en/latest/plugins/hitchselenium.html

        self.services['Firefox'] = hitchselenium.SeleniumService(
            xvfb=self.settings.get("xvfb", False) or self.settings.get("quiet", False),
            no_libfaketime=True,
        )

        self.services.startup(interactive=False)

        # Docs : https://hitchtest.readthedocs.org/en/latest/plugins/hitchselenium.html
        self.driver = self.services['Firefox'].driver

        self.webapp = hitchselenium.SeleniumStepLibrary(
            selenium_webdriver=self.driver,
            wait_for_timeout=5,
        )

        self.click = self.webapp.click
        self.should_not_appear = self.webapp.should_not_appear
        self.wait_to_appear = self.webapp.wait_to_appear
        self.wait_to_contain = self.webapp.wait_to_contain
        self.wait_for_any_to_contain = self.webapp.wait_for_any_to_contain
        self.click_and_dont_wait_for_page_load = self.webapp.click_and_dont_wait_for_page_load

        # Configure selenium driver
        screen_res = self.settings.get(
            "screen_resolution", {"width": 1024, "height": 768, }
        )
        self.driver.set_window_size(
            int(screen_res['width']), int(screen_res['height'])
        )
        self.driver.set_window_position(0, 0)
        self.driver.implicitly_wait(2.0)
        self.driver.accept_next_alert = True

        chdir(PROJECT_DIRECTORY)

    def button_is_disabled(self, item):
        button = self.driver.find_element_by_id(item)
        # Using .is_enabled while disabled is true returns True as well,
        # so we'll check for it this way instead
        assert button.get_attribute('disabled') == 'true'

    def navigate_to(self, target):
        self.driver.get(target)

    def task_has_recent_progress_entries(self, task_id, expected_count):
        recent_progress = self.webapp.driver.find_elements_by_class_name(
            'task_{task}_recent_progress'.format(task=task_id),
        )
        assert len(recent_progress) == int(expected_count)

    def click_go_on_break_for_today(self):
        today = urllib.parse.quote_plus(datetime.datetime.strftime(
            datetime.datetime.today(),
            '%Y %b %d',
        ))

        break_id = 'go_on_break_{date}'.format(date=today)
        self.webapp.click(break_id)

    def generate_all_lower_128_unicode_string(self):
        return ''.join([
            chr(i) for i in range(0,128)
        ])

    def generate_first_50_lower_128_unicode_string(self):
        return ''.join([
            chr(i) for i in range(0,50)
        ])

    def generate_second_50_lower_128_unicode_string(self):
        return ''.join([
            chr(i) for i in range(50,100)
        ])

    def generate_remaining_lower_128_unicode_string(self):
        return ''.join([
            chr(i) for i in range(100,128)
        ])

    def generate_big_unicode_string(self, length=50):
        # Uses largest UTF-8 character
        return ''.join([
            chr(0x10FFFF) for in in range(length)
        ])

    # TODO: Function to fill named field with lower 128 strings and strings of
    # arbitrary length

    def complete_task_yesterday(self):
        yesterday = urllib.parse.quote_plus(datetime.datetime.strftime(
            datetime.datetime.today() - datetime.timedelta(days=1),
            '%Y %b %d',
        ))

        complete_id = 'complete_{date}'.format(date=yesterday)
        self.webapp.click(complete_id)
        self.webapp.click('complete-task')

    def go_on_task_break_yesterday(self):
        yesterday = urllib.parse.quote_plus(datetime.datetime.strftime(
            datetime.datetime.today() - datetime.timedelta(days=1),
            '%Y %b %d',
        ))

        break_id = 'go_on_break_{date}'.format(date=yesterday)
        self.webapp.click(break_id)
        self.webapp.click('confirm-break')

    def navigate_to_break_for_today_by_id(self, base_url, task_id):
        today = urllib.parse.quote_plus(datetime.datetime.strftime(
            datetime.datetime.today(),
            '%Y %b %d',
        ))

        holiday_link = 'task_break/{task_id}/{today}'.format(
            task_id=task_id,
            today=today,
        )

        target = urllib.parse.urljoin(base_url, holiday_link)

        self.navigate_to(target)

    def fail_when_clicking(self, item):
        """Fail if there is no failure when clicking an element"""
        self.webapp.click(item)

        try:
            self.driver.find_element_by_class_name("http-error")
        except NoSuchElementException:
            raise RuntimeError(
                "Clicking {} should not have succeeded".format(item)
            )

    def fail_to_navigate_to(self, target):
        """Fail if there is no failure when navigating to a URL"""
        self.navigate_to(target)

        try:
            self.driver.find_element_by_class_name("http-error")
        except NoSuchElementException:
            raise RuntimeError(
                "Navigating to {} should not have succeeded".format(target)
            )

    def set_task_creation_date_earlier(self, task_id, days_in_the_past):
        """Set a task to have been created earlier."""
        creation = datetime.datetime.today() - datetime.timedelta(
            days=days_in_the_past,
        )

        conn = sqlite3.connect(self.turkeydb_file)
        conn.execute(
           'update tasks set creation_time=? where id=?',
           (creation, task_id)
        )
        conn.commit()

    def _should_not_appear(self, item):
        """Only raise exception if element does appear."""
        from selenium.common.exceptions import TimeoutException
        try:
            self.wait_to_appear(item)
            raise RuntimeError("Item {} appeared".format(item))
        except TimeoutException:
            pass

    def historic_task_count_is(self, expected_count):
        """Check that the number of historic tasks on the page matches the
           expected amount."""
        historic_tasks = self.webapp.driver.find_elements_by_class_name(
            'historic-task'
        )
        actual_count = len(historic_tasks)
        expected = int(expected_count)
        assert actual_count == expected, "Expected %s, saw %s" % (
            expected,
            actual_count,
        )

    def active_tasks_id_order_is(self, expected_order):
        """Get all task IDs by task_X_history buttons and check they're in the
           expected order."""
        buttons =  self.webapp.driver.find_elements_by_class_name('btn')
        task_history_buttons = [
            button.get_attribute('id')
            for button in buttons
            if 'task' in button.get_attribute('id')
            and 'history' in button.get_attribute('id')
        ]
        task_order = [
            int(task.split('_')[1])
            for task in task_history_buttons
        ]

        # Make sure the expected order uses integers to avoid difficult to
        # comprehend errors
        expected_order = [int(item) for item in expected_order]

        assert task_order == expected_order, 'Order was: %s. Expected: %s' % (
            task_order,
            expected_order
        )

    def pause(self, message=None):
        """Pause test and launch IPython"""
        if hasattr(self, 'services'):
            self.services.start_interactive_mode()
        self.ipython(message)
        if hasattr(self, 'services'):
            self.services.stop_interactive_mode()

    def load_website(self):
        """Navigate to website in Firefox."""
        self.driver.get("http://localhost:5000")

    def fill_form(self, **kwargs):
        """Fill in a form with id=value."""
        for element, text in kwargs.items():
            self.driver.find_element_by_id(element).send_keys(text)
        
    def wait_for_email(self, containing=None):
        """Wait for email."""
        self.services['HitchSMTP'].logs.out.tail.until_json(
            lambda email: containing in email['payload'] or containing in email['subject'],
            timeout=45,
            lines_back=1,
        )
    
    def confirm_emails_sent(self, number):
        """Count number of emails sent by app."""
        assert len(self.services['HitchSMTP'].logs.json()) == int(number)

    # Can also specify minutes and hours... probably not useful yet?
    def time_travel(self, days=""):
        """Get in the Delorean, Marty!"""
        self.services.time_travel(days=int(days))

    def connect_to_kernel(self, service_name):
        """Connect to IPython kernel embedded in service_name."""
        self.services.connect_to_ipykernel(service_name)

    def on_failure(self):
        """Runs if there is a test failure"""
        if not self.settings['quiet']:
            if self.settings.get("pause_on_failure", False):
                self.pause(message=self.stacktrace.to_template())

    def on_success(self):
        """Runs when a test successfully passes"""
        if self.settings.get("pause_on_success", False):
            self.pause(message="SUCCESS")

    def tear_down(self):
        """Run at the end of all tests."""
        if hasattr(self, 'services'):
            self.services.shutdown()
        try:
            remove(self.turkey_conf_file)
        except FileNotFoundError:
            pass
        if not self.turkeydb_file_pre_existing:
            try:
                remove(self.turkeydb_file)
            except FileNotFoundError:
                pass
