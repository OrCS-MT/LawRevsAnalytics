"""
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




"""**Global Variables**"""

law_reviews_names = {
    'BuffLR': 'Buffalo Law Review',
    'CaliLR': 'California Law Review',
    'CWRLR': 'Case Western Reserve Law Review',
    'CathULR': 'Catholic University Law Review',
    'ChiKLR': 'Chicago-Kent Law Review',
    'ClevSLR': 'Cleveland State Law Review',
    'CorLR': 'Cornell Law Review',
    'DePLR': 'DePaul Law Review',
    'DiLR': 'Dickinson Law Review (Penn State)',
    'FLRL': 'Florida Law Review',
    'FordLR': 'Fordham Law Review',
    'HastLJ': 'Hastings Law Journal',
    'IndLJ': 'Indiana Law Journal',
    'KentuLLJ': 'Kentucky Law Journal',
    'LouisLR': 'Louisiana Law Review',
    'MarqLR': 'Marquette Law Review',
    'MichLR': 'Michigan Law Review',
    'MinnLR': 'Minnesota Law Review',
    'MissLR': 'Missouri Law Review',
    'MontLR': 'Montana Law Review',
    'NCarolLR': 'North Carolina Law Review',
    'NDakoLR': 'North Dakota Law Review',
    'NotDamLR': 'Notre Dame Law Review',
    'SMULR': 'SMU Law Review',
    'SCarolLR': 'South Carolina Law Review',
    'SJohnLR': "St. John's Law Review",
    'UChiLR': 'University of Chicago Law Review',
    'UMiaLR': 'University of Miami Law Review',
    'VandLR': 'Vanderbilt Law Review',
    'WashLeeLR': 'Washington & Lee Law Review',
    'WashLR': 'Washington Law Review'
}

law_reviews_IDs = {
    'BuffLR': 101,
    'CaliLR': 102,
    'CWRLR': 103,
    'CathULR': 104,
    'ChiKLR': 105,
    'ClevSLR': 106,
    'CorLR': 107,
    'DePLR': 108,
    'DiLR': 109,
    'FLRL': 110,
    'FordLR': 111,
    'HastLJ': 112,
    'IndLJ': 113,
    'KentuLLJ': 114,
    'LouisLR': 115,
    'MarqLR': 116,
    'MichLR': 117,
    'MinnLR': 118,
    'MissLR': 119,
    'MontLR': 120,
    'NCarolLR': 121,
    'NDakoLR': 122,
    'NotDamLR': 123,
    'SMULR': 124,
    'SCarolLR': 125,
    'SJohnLR': 126,
    'UChiLR': 127,
    'UMiaLR': 128,
    'VandLR': 129,
    'WashLeeLR': 130,
    'WashLR': 131
}

# *** MAKE SURE TO ASSIGN VALUES TO 'unique_key' AND TO ALL DIRECTORIES
unique_key = "BuffLR"
LR_Name = law_reviews_names[unique_key]
LR_ID = law_reviews_IDs[unique_key]
delay = 30

# Directory containing the PDFs
pdf_dir = f"/content/drive/MyDrive/LRsPr{unique_key}/PDFs"
# Directory containing TXT copies of the PDFs, with fulltext content
fulltext_dir = f"/content/drive/MyDrive/LRsPr{unique_key}/Fulltexts"
# Directory containing the main text and FNs text files of each paper (saved as two txt files, one with _M, the other _FN)
main_fns_texts_dir = f"/content/drive/MyDrive/LRsPr{unique_key}/Main&FNs"
# Directory containing the start/mid/end of each paper
SME_dir = f"/content/drive/MyDrive/LRsPr{unique_key}/SMEText"
# Directory containing the xlsx file with all paper objects
XLSX_dir = f"/content/drive/MyDrive/LRsPr{unique_key}/XLSX"
# Directory containing the xlsx file with all paper objects
logs_dir = f"/content/drive/MyDrive/LRsPr{unique_key}/Logs"

# Fixing paths for log files
critical_errors_log_path = f"{logs_dir}/#CritLogPath.txt"
pdf_to_txt_log_path = f"{logs_dir}/#PDFtoTXTLog.txt"
txt_length_log_path = f"{logs_dir}/#TXTLengthog.txt"
cite_log_path = f"{logs_dir}/#CiteLog.txt"
yearvolpage_log_path = f"{logs_dir}/#YVPLog.txt"
auth_title_text_log_path = f"{logs_dir}/#AuthtitleTextLog.txt"
extract_authors_and_title_log_path = f"{logs_dir}/#ExtractAuthtitleLog.txt"
valid_pdf_path_log_path = f"{logs_dir}/#ValidPdfPathLog.txt"
main_fns_text_division_log_path = f"{logs_dir}/#Mainfns_textDivisionLog.txt"
first_last_fns_log_path = f"{logs_dir}/#FirstLastFNsLog.txt"
ACK_log_path = f"{logs_dir}/#ACKLog.txt"
SME_log_path = f"{logs_dir}/#SMELog.txt"
main_reorg_log_path = f"{logs_dir}/#MainReOrgLog.txt"
XLSX_log_path = f"{logs_dir}/#XLSXLog.txt"




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

#Function - Print a List of LRPaper Objects
def print_LRPapers_list(papers):
    """
    Print all attributes for all LRPaper objects in a given list.

    Args:
    papers (list): A list of LRPaper objects.
    """
    for paper in papers:
        paper.print_attributes()
        print("\n")

#Function - Print Bold
def print_bold(text):
    """
    Print provided text in bold.

    Args:
    text (str): The text to be printed in bold.
    """

    # The ANSI escape code for bold text is '\033[1m'
    # '\033[0m' resets the style back to normal
    print('\033[1m' + text + '\033[0m')


#Function - Clean Double-spaces, Leading/Trailing Spaces, Empty Lines
def remove_edge_spaces(text):
    """Remove leading and trailing spaces from the text."""
    return text.strip()

def remove_empty_lines(text):
    """Remove empty lines from the text."""
    return re.sub(r'\n\s*\n', '\n', text)

def clean_line_spaces(text):
    """Remove leading and trailing spaces from each line in the text."""
    return '\n'.join([line.strip() for line in text.split('\n')])

def reduce_spaces(text):
    """Replace multiple spaces with a single space in the text."""
    return re.sub(r' +', ' ', text)

def clean_text(text):
    """
    Clean text by removing leading and trailing spaces, empty lines, and extra spaces within lines.

    Args:
    text (str): The text to be cleaned.

    Returns:
    str: The cleaned text.
    """
    text = remove_edge_spaces(text)
    text = remove_empty_lines(text)
    text = clean_line_spaces(text)
    text = reduce_spaces(text)
    return text

