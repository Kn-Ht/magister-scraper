from platform import system
from getpass import getuser

running_windows = system() == "Windows"

class Browsers:
    firefox = "geckodriver.exe" if running_windows else "geckodriver"
    chrome  = "chromedriver.exe" if running_windows else "chromedriver"
    opera = "operadriver.exe"

class Locations:
    operaGX = f"C:\\Users\\{getuser()}\\AppData\\Local\\Programs\\Opera GX\\opera.exe"

# -------------------------------------------------- #
"""
if using chrome:
    BROWSER = Browsers.chrome
if using operaGX:
    BROWSER = Browsers.opera
if using firefox:
    BROWSER = Browsers.firefox
"""
BROWSER = Browsers.chrome

# school name, example: SCHOOL = "osghengelo"
SCHOOL = "osghengelo"

LOGIN = (
    "username",
    "password"
)
