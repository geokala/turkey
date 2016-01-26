from hitchserve import ServiceBundle
from os import path, system, chdir, remove
from os.path import expanduser
from subprocess import check_call, PIPE
import hitchpostgres
import hitchselenium
import hitchpython
import hitchserve
import hitchsmtp
import hitchtest
import json


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

        #postgres_package = hitchpostgres.PostgresPackage(
            #version=self.settings["postgres_version"],
        #)
        #postgres_package.build()

        turkeydb_filename = path.join(hitchtest.utils.get_hitch_directory(), "turkey.db")

        if path.exists(turkeydb_filename):
            remove(turkeydb_filename)

        with open(path.join(PROJECT_DIRECTORY, "turkey.conf"), "w") as turkey_conf:
            turkey_conf.write(json.dumps({
                "SECRET_KEY": "xxx",
                "DEBUG": False,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///{}".format(turkeydb_filename)
            }))

        chdir(PROJECT_DIRECTORY)
        check_call([self.python_package.python, "manage.py", "db", "upgrade"])

        self.services = ServiceBundle(
            project_directory=PROJECT_DIRECTORY,
            startup_timeout=float(self.settings["startup_timeout"]),
            shutdown_timeout=float(self.settings["shutdown_timeout"]),
        )

        # Docs : https://hitchtest.readthedocs.org/en/latest/plugins/hitchpostgres.html

        # Postgres user and database
        postgres_user = hitchpostgres.PostgresUser("example", "password")

        #self.services['Postgres'] = hitchpostgres.PostgresService(
            #postgres_package=postgres_package,
            #users=[postgres_user, ],
            #port=15432,
            #databases=[hitchpostgres.PostgresDatabase("example", postgres_user), ]
        #)

        # Docs : https://hitchtest.readthedocs.org/en/latest/plugins/hitchsmtp.html
        self.services['HitchSMTP'] = hitchsmtp.HitchSMTPService(port=10025)

        # Docs : https://hitchtest.readthedocs.org/en/latest/plugins/hitchpython.html
        self.services['Flask'] = hitchserve.Service(
            command=[self.python_package.python, "manage.py", "runserver", ],
            directory=PROJECT_DIRECTORY,
            needs=[], #[self.services['Postgres'], ],
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
