from src.url_links import query
from src.download_files import get_files_by_year, TypeKeys
import pandas as pd
import numpy as np
from json import loads, dumps


print(get_files_by_year(4, [TypeKeys.URL, TypeKeys.LINK]))

