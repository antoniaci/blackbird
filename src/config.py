import os

# List directory
LIST_DIRECTORY = "data"

# Username List
USERNAME_LIST_URL = (
    "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
)
USERNAME_LIST_FILENAME = "wmn-data.json"
USERNAME_LIST_PATH = os.path.join(os.getcwd(), LIST_DIRECTORY, USERNAME_LIST_FILENAME)
USERNAME_METADATA_LIST_FILENAME = "wmn-metadata.json"
USERNAME_METADATA_LIST_PATH = os.path.join(
    os.getcwd(), LIST_DIRECTORY, USERNAME_METADATA_LIST_FILENAME
)

# Email List
EMAIL_LIST_FILENAME = "email-data.json"
EMAIL_LIST_PATH = os.path.join(os.getcwd(), LIST_DIRECTORY, EMAIL_LIST_FILENAME)

# Logs
LOG_DIRECTORY = "logs"
LOG_FILENAME = "blackbird.log"
LOG_PATH = os.path.join(os.getcwd(), LOG_DIRECTORY, LOG_FILENAME)

# Assets
ASSETS_DIRECTORY = "assets"
FONTS_DIRECTORY = "fonts"
IMAGES_DIRECTORY = "img"


# PDF
FONT_REGULAR_FILE = "Montserrat-Regular.ttf"
FONT_BOLD_FILE = "Montserrat-Bold.ttf"
FONT_NAME_REGULAR = "Montserrat"
FONT_NAME_BOLD = "Montserrat-Bold"

aiModel = None
ai = False
ai_analysis = None
