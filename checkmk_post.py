#!/usr/bin/env python

import json
import requests
import os
import time
import datetime
import pandas as pd
import numpy as np
from Timing import roundups, rounddos
from requests.exceptions import Timeout
import subprocess
from multiprocessing import Process 

current = datetime.datetime.now()
current_5 = current - datetime.timedelta(minutes=5)
start = rounddos(current_5)
start_final = time.mktime(start.timetuple())
start_final = int(start_final)
end = rounddos(current)
end_final = time.mktime(end.timetuple())
end_final = int(end_final)