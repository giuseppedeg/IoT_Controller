import json
import sys
import os

def resource_path(relative_path):      
    """ Get absolute path to resource, works for dev and for PyInstaller """       
    try: # PyInstaller creates a temp folder and stores path in _MEIPASS           
        base_path = sys._MEIPASS       
    except Exception:           
        base_path = os.path.abspath(".")       
    return os.path.join(base_path, relative_path)


CONFIG_CF = "data/config.json"

if os.path.exists(CONFIG_CF):
    with open(CONFIG_CF, 'r') as file:
        json_config = json.load(file)
else:
    json_config = {}

RESULTS_PROTOCOL_FOLDER = "results"

MAX_ID_LEN = 4

ACTIVITES_PATH = "data/inkml_file"

DEFAULT_RES_TMP = resource_path("in_data/.tmp")

if "DEFAULT_ORDER" in json_config:
    DEFAULT_ORDER = json_config['DEFAULT_ORDER']
else:
    DEFAULT_ORDER = []

DEFAULT_IMAGE = resource_path('in_data/Image/def_img.bmp')
END_ACQUISITION_IMAGE = resource_path('in_data/Image/stop_acquisition.bmp')
END_ACQUISITION_INKML = resource_path('in_data/stop_acquisition.inkml')

DEFAULT_SUBJ = "DEFAULT_SUBJ"

if "ELEMENTS_TO_RECORD" in json_config:
    ELEMENTS_TO_RECORD = json_config['ELEMENTS_TO_RECORD']
else:
    ELEMENTS_TO_RECORD = 1

if "ELEMENTS_TO_RECORD_SPECIFIC" in json_config:
    ELEMENTS_TO_RECORD_SPECIFIC = json_config['ELEMENTS_TO_RECORD_SPECIFIC']
else:
    ELEMENTS_TO_RECORD_SPECIFIC = {}

ICON_IMG = resource_path("in_data/Image/256x256.png")

# COLORI!!
# buttons
COLOR_BKGR_RIOTBUTTON = "#f7f7f7"
COLOR_FRGR_RIOTBUTTON = "#000000"

COLOR_BKGR_SENDNEXTBUTTON = "#31e1e1"
COLOR_FRGR_SENDNEXTBUTTON = "#000000"

COLOR_BKGR_SENDBUTTON = "#4dcf47"
COLOR_FRGR_SENDBUTTON = "#000000"

COLOR_BKGR_STOPBUTTON = "#d95b41"
COLOR_FRGR_STOPBUTTON = "#000000"

COLOR_BKGR_UNDOBUTTON = "#494444"
COLOR_FRGR_UNDOBUTTON = "#FCFCFC"

# info pane
COLOR_BKGR_OUTLABEL = "#3b3434"
COLOR_FRGR_OUTLABEL = "#f7f7f7"
COLOR_FRGR_ERROR_OUTLABEL = "#de2f09"
COLOR_FRGR_GREEN_OUTLABEL = "#5be654"


# controller.py

SAVE_FILE = resource_path("in_data/assets/save.txt")