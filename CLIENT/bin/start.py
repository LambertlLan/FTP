# __author: Lambert
# __date: 2017/9/19 15:12
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from client_core import main

if __name__ == "__main__":
    main.run()