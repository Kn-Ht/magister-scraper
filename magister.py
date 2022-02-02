if __name__ == "__main__":
    print("this file is a library.\nthis file is not meant to be run.")
    exit(1)

import config
import itertools
import platform
import sys
from os import getcwd, system
from os.path import isfile, join
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, FirefoxOptions

if platform.system() == "Windows":
    DRIVER = join(getcwd(), config.BROWSER)
else:
    DRIVER = join(getcwd(), config.BROWSER)


class DriverNotFoundError(Exception):
    pass


class Cijfer:
    def __init__(self, vak, date, description, cijfer, weging, inhalen) -> None:
        self.vak = vak
        self.date = date
        self.description = description
        self.cijfer = cijfer
        self.weging = weging
        self.inhalen = inhalen

    @property
    def all(self):
        return [
            self.vak,
            self.description,
            self.cijfer,
            self.weging,
            self.date,
            self.inhalen,
        ]


def log(type: str, msg: str):
    print("\033[92m{0} :\033[0m {1}".format(type, msg))


class Magister:
    def __init__(self, school: str, login_data: tuple, nobrowser=True) -> None:
        """arguments:
        * school (string) -> name of the school to log into
        * login_data (tuple) -> tuple with username and password, e.g: ("username", "password")
        * nobrowser (bool) -> if True, make browser window invisible.
        """
        system("cls||clear")

        log("INFO", f"nobrowser = {nobrowser}")

        self.school = school
        self.logindata = login_data

        if not isfile(DRIVER):
            raise DriverNotFoundError("ERROR: driver needs to be in folder.")

        log("INFO", '[driver path] = "{}"'.format(DRIVER))
        firefox_opts = FirefoxOptions()
        firefox_opts.headless = nobrowser

        log("INFO", "starting client...")
        self.driver = Firefox(options=firefox_opts, executable_path=DRIVER)
        print("\n\033[93mloading login page...", end="\033[92m")

    def login(self):

        username, password = self.logindata
        self.driver.get(f"https://{self.school}.magister.net")

        while True:
            try:
                self.driver.find_element_by_id("username")
            except NoSuchElementException:
                pass
            else:
                break
        print("done.\033[0m")

        print("\n\033[93mlogging in...", end="\033[92m")
        self.driver.find_element_by_id("username").send_keys(username)
        self.driver.find_element_by_id("username_submit").click()
        sleep(0.3)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("password_submit").click()
        print("done.\033[0m")

        print("\n\033[93mloading home page...", end="\033[92m")
        while True:
            try:
                self.driver.find_element_by_id("agenda-widget")
            except NoSuchElementException:
                pass
            else:
                break

        print("done.\033[0m")
        """ login successful """

    def agenda_items(self) -> list:
        # TODO implement this
        while True:
            try:
                self.driver.find_element_by_class_name("icon-calendar")
            except NoSuchElementException:
                break

        times = [i.text for i in self.driver.find_elements_by_class_name("les-info")]
        # items = [i.text for i in self.driver.find_elements_by_tag_name("td")]
        print(times)

    def go_home(self):
        while True:
            try:
                btn = self.driver.find_element_by_id("menu-vandaag")
            except NoSuchElementException:
                pass
            else:
                btn.click()
                log("INFO", "went to home page")
                break

    def go_agenda(self):
        while True:
            try:
                btn = self.driver.find_element_by_id("menu-agenda")
            except NoSuchElementException:
                pass
            else:
                btn.click()
                log("INFO", "went to agenda page")
                break

    def go_leermiddelen(self):
        while True:
            try:
                btn = self.driver.find_element_by_id("menu-leermiddelen")
            except NoSuchElementException:
                pass
            else:
                btn.click()
                log("INFO", "went to leermiddelen page")
                break

    def leermiddelen(self) -> dict:
        self.go_leermiddelen()
        for second in range(1, 6):
            print(
                "\033[92mINFO :\033[0m waiting for leermiddelen to load... [{}/5]".format(
                    second
                ),
                end="\r",
            )
            sleep(1)
        print()

        result = [i.text for i in self.driver.find_elements_by_tag_name("td")]

        if not result:
            log("INFO", "no leermiddelen found.")
            return

        leermiddelen = [
            list(y)
            for x, y in itertools.groupby(result, lambda z: z == "Digitaal")
            if not x
        ]
        for (i, _j) in enumerate(leermiddelen):
            leermiddelen[i] = [x for x in leermiddelen[i] if x != ""]

        leermiddelen_dict = []

        # TODO fix links not working in leermiddelen_dict

        for _, item in enumerate(leermiddelen):
            if len(item) != 3:
                continue
            leermiddelen_dict.append(
                {
                    "vak": item[0],
                    "titel": item[1],
                    "url": self.driver.find_elements_by_tag_name("a")(
                        item[1]
                    ).get_attribute("href"),
                    "ean": item[2],
                }
            )

        return leermiddelen_dict

    def cijfers(self, float_notation=",") -> list[Cijfer]:
        """
        retrieve the list of all the latest grades in the 'cijfers' section on the magister homepage.

        arguments:
            - self
            - float_notation (string) -> default ','\n
            if you want to convert your grades into floats (e.g "6.7" -> 6.7) specify float_notation as '.'
        """
        while True:
            try:
                btn = self.driver.find_element_by_id("menu-cijfers")
            except NoSuchElementException:
                pass
            else:
                btn.click()
                log("INFO", "went to 'cijfers'")
                break

        while True:
            try:
                self.driver.find_element_by_tag_name("td")
            except NoSuchElementException:
                pass
            else:
                break

        cijfers = []

        result = [i.text for i in self.driver.find_elements_by_tag_name("td")]

        cijfers_spl = [
            list(y) for x, y in itertools.groupby(result, lambda z: z == "") if not x
        ]
        """
        order: [vak, date, description, cijfer, weging]
        dict return:
            {
                "vak": i[0],
                "date": i[1],
                "description": i[2],
                "cijfer": i[3],
                "weging": i[4],
                "inhalen": i[3] == "Inh"
            }
        """
        for i in cijfers_spl:
            c = (
                Cijfer(i[0], i[1], i[2], i[3].replace(",", "."), i[4], i[3] == "Inh")
                if float_notation != ","
                else Cijfer(i[0], i[1], i[2], i[3], i[4], i[3] == "Inh")
            )
            cijfers.append(c)

        return cijfers

    def cijfers_all(self):
        # NOTE work in progress
        while True:
            try:
                btn = self.driver.find_element_by_id("menu-cijfers")
            except NoSuchElementException:
                pass
            else:
                btn.click()
                log("INFO", "went to 'cijfers'")
                break

        while True:
            try:
                btn = self.driver.find_element_by_tag_name(
                    "dna-button"
                )  # dna-button = 'uitgebreide weergave'
            except NoSuchElementException:
                pass
            else:
                btn.click()
                log("INFO", "went to 'cijfers uitgebreid'")
                break

        while True:
            try:
                self.driver.find_element_by_tag_name("th")
            except NoSuchElementException:
                pass
            else:
                break

        """ loaded uitgebreide cijfers """

        # TODO implement

    def stop(self):
        self.driver.quit()
        log("INFO", "driver stopped, exiting...")
        sys.exit(0)
