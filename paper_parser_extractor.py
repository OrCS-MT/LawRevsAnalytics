"""paper_parser_extractor.py

# **Module Description**

Article Data Extractor
This module provides functionalities for extracting specific information from Law Reviews Papers (PDF format).
The module includes functions for parsing PDF files, processing the extracted data, organizing it into a structured format, and creating a tailor-made class object for further data mining.

Features:
- Load and parse PDF files.
- Extract text and metadata from PDFs.
- Cleaning, preprocessing, and reorganizing of source files and extracted data.
- A class-based approach to handle different text sources efficiently.

Dependencies:
This module requires specific third-party libraries, which should be installed and imported at the beginning of the script.

Note:
This script is designed with best practices in Python programming, ensuring readability, maintainability, and efficient performance.
The code is fully documented for ease of understanding and further modification.
"

"""

### PIP, Imports
import copy
import os
import time
import string
import datetime
import re
import sys



### **Class *LRPaper***

class LRPaper:
    """
    Represents a Law Review paper, containing various metadata and textual components.
    """

    def __init__(self, doc_id=None, filename=None, doc_type=None, number_of_pages=None, journal=None, year=None, first_page=None, vol=None,
                 vol_start_index = None, authors_title_text=None, title=None, authors=None, PDF=None, full_text=None, cite_line=None,
                 length_original=None, length_reorg=None, main_text=None,fns_text=None, main_text_length=None, fns_text_length=None,
                 total_fns=None,fns_words_ratio=None, main_fns_portions=None, general_length_problem_flag = True, start=None, mid=None, end=None, short_SME_flag = False, SME=None,
                 first_fn_num=None, first_fn_text=None, last_fn_num=None, last_fn_text=None, acknowledgement=None, 
                 acknowledgement_length=None, reorg_acknowledgment=None, reorg_acknowledgment_length=None, ACK_length_problem_flag=False):
        """
        Initialize an LRPaper object with the provided attributes.
        """
        self.doc_id = doc_id
        self.filename = filename
        self.doc_type = doc_type
        self.number_of_pages = number_of_pages
        self.journal = journal
        self.year = year
        self.first_page = first_page
        self.vol = vol
        self.vol_start_index = vol_start_index # Index in the line of the first char of the volume Number
        self.authors_title_text = authors_title_text # string containing the authors & title
        self.title = title
        self.authors = authors
        self.PDF = PDF # path to the PDF file of the paper
        self.full_text = full_text # path to the fulltext txt file of the paper
        self.cite_line = cite_line # string containing the Bluebook citation of the paper
        self.length_original = length_original
        self.length_reorg = length_reorg
        self.main_text = main_text
        self.fns_text = fns_text
        self.total_fns = total_fns
        self.fns_words_ratio = fns_words_ratio
        self.main_fns_portions = main_fns_portions
        self.general_length_problem_flag = length_problem_flag # initialized as TRUE to reflect a problem with the length of the text; when the text length is ok, change value to FALSE
        self.start = start
        self.mid = mid
        self.end = end
        self.short_SME_flag = short_SME_flag
        self.SME = SME
        self.main_text_length = main_text_length
        self.fns_text_length = fns_text_length
        self.first_fn_num = first_fn_num
        self.first_fn_text = first_fn_text
        self.last_fn_num = last_fn_num
        self.last_fn_text = last_fn_text
        self.acknowledgment = acknowledgment
        self.acknowledgment_length = acknowledgement_length
        self.reorg_acknowledgment = reorg_acknowledgment             
        self.reorg_acknowledgment_length = reorg_acknowledgment_length
        self.ACK_length_problem_flag = ACK_length_problem_flag                     
    

    def print_attributes(self):
        """
        Print all attributes of the LRPaper instance.
        """
        attributes = vars(self)  # 'vars' returns the __dict__ attribute of an object.
        for attribute, value in attributes.items():
            print(f"{attribute}: {value}")


    def to_dict(self):
        """
        Convert the LRPaper instance attributes to a dictionary.
        """
        return vars(self)


# Check the LRPaper class
instance = LRPaper()
instance.print_attributes()


### **Functions**

#Function - Create (overwrite) Log File
def write_log_file(message, log_path):
    """
    Create a log file (and overwrite an existing one).

    Args:
    - message (str): The first message to be logged.
    - log_path (str): Path to the log file where the message will be logged.
    """
    with open(log_path, 'w', encoding='utf-8') as log_file:
        now = datetime.datetime.now()
        log_file.write(f"{now}: {message}")


#Function - Log Error
def log_error(message, log_path):
    """
    Log an error message to the specified log file.

    Args:
    - message (str): The error message to be logged.
    - log_path (str): Path to the log file where the error will be logged.
    """
    with open(log_path, 'a', encoding='utf-8') as log_file:
        now = datetime.datetime.now()
        log_file.write(f"{now}: {message}")

#Function - Create Directory (if missing)
def create_directory_if_not_exists(directory):
    """
    Create a directory at the specified path if it does not already exist.

    Args:
    directory (str): The path of the directory to be created.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")
