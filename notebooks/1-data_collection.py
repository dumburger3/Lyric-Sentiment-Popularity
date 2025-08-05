import billboard
import lyricsgenius
import pandas as pd
import numpy as np
import time
import os
from dotenv import load_dotenv

load_dotenv()

GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

