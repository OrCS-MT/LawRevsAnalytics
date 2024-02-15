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
pip install PyMuPDF pypdf2 pdfminer.six
pip install numpy scipy
pip install scikit-image Pillow
pip install tqdm

import copy
import os
import time
import string
import datetime
import re
import sys
import threading
import contextlib
import multiprocessing
from typing import Optional
import PyPDF2
import fitz
from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_pages
import numpy as np
from skimage import measure
from PIL import Image
import pandas as pd
from tqdm.notebook import tqdm




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

#Function - Print the number of all files of specific format in a folder
def count_specific_files(path, suffix):
    """
    Count the number of files with a given suffix in the given path.

    Args:
    path (str): Path of the folder to search in.
    suffix (str): The desired file format to count, e.g., '.pdf'. The suffix should be lowercase.

    Returns:
    int: Number of files matching the suffix found. In case of an error, it prints a message and returns None.
    """
    file_count = 0
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith(suffix):
                    file_count += 1
        return file_count

    except Exception as e:
        print(f"Error encountered in count_specific_files funtion: {e}")
        return None

#Function - Save LRPapers Dictionary to XLSX
def save_papers_to_xlsx(papers, save_path, output_name, log_path, chunk_size=10000):
    """
    Save a list of LRPaper objects to an XLSX file in chunks.

    Args:
    - papers (list): List of LRPaper objects.
    - save_path (str): Directory path where the XLSX file will be saved.
    - output_name (str): String to be included in the filename before the timestamp.
    - log_path (str): Path to the log file where errors will be logged.
    - chunk_size (int): Number of rows per chunk in the XLSX file.

    Returns:
    None: Prints the path to the saved file upon completion.
    """

    papers_dicts = convert_papers_to_dicts(papers, log_path)
    df = pd.DataFrame(papers_dicts)

    current_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    file_path = f"{save_path}/{output_name}_{current_time}.xlsx"

    # calculates the number of chunks (incl. if the last one has less than 10,000 items)
    num_chunks = len(df) // chunk_size + (len(df) % chunk_size > 0)

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for i in range(num_chunks):
            try:
                df_chunk = df[i*chunk_size:(i+1)*chunk_size]
                df_chunk.to_excel(writer, index=False, startrow=i*chunk_size)
            except Exception as e:
                log_error(f"Problem writing chunk {i+1} to XLSX. Error: {str(e)}\n", log_path)

    print(f"Data saved to {file_path}")


#Function - Get a Number of PDF Pages
def get_num_of_pages(pdf_path):
    """
    Determine the number of pages in a PDF file.

    Args:
    pdf_path (str): The file path of the PDF.

    Returns:
    int: The number of pages in the PDF. Returns None if the file cannot be read or is not a valid PDF.
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error in get_num_of_pages funtion: {e}\n Could not read the file {pdf_path}\n")
        return None

#Function - Count Words in title Page
def count_words_in_title_page(pdf_path):
    """
    Count the number of words on the first page (title page) of a PDF file.

    Args:
    pdf_path (str): The file path of the PDF.

    Returns:
    int: The number of words on the first page. Returns None if the text cannot be extracted or if there's an error.
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            first_page = reader.pages[0]
            text = first_page.extract_text()
            words = text.split()
            return len(words)

    except Exception as e:
        print(f"Error in count_words_in_title_page funtion: {e}\n Could not read the file {pdf_path}\n")
        return None

#Function - Extract full text from PDF
"""
Input - PDF file
Outupt - TXT file
"""

def extract_text_from_pdf(pdf_path, txt_path, pdf_to_txt_log_path):
    """
    Extract text from a PDF and save it to a text file.
    This function runs in a separate process.

    Args:
    - pdf_path (str): The file path of the PDF.
    - txt_path (str): The path where the extracted text should be saved.
    - pdf_to_txt_log_path (str): Path to the log file for recording the process.

    Returns:
    str: "Success" if extraction is successful, None otherwise.
    """
    try:
        # Extract text from PDF
        text = extract_text(pdf_path)

        # Save the extracted text to a text file
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

        log_error("Successfully extracted text.\n\n", pdf_to_txt_log_path)
        return "Success"

    except Exception as e:
        log_error(f"ERROR WITH TEXT EXTRACTION: {str(e)} \n for file: {pdf_path}\n\n", pdf_to_txt_log_path)
        print(f"Error processing {pdf_path}: {str(e)}\n\n")
        return None


def extract_text_from_pdf_with_timeout(pdf_path, txt_path, pdf_to_txt_log_path, timeout=30):
    """
    Attempt to extract text from a PDF file within a specified timeout.

    Args:
    - pdf_path (str): The file path of the PDF.
    - txt_path (str): The path where the extracted text should be saved.
    - pdf_to_txt_log_path (str): Path to the log file for recording the process.
    - timeout (int): The maximum time in seconds to wait for the extraction process.

    Returns:
    None: The function does not return a value but logs the outcome.
    """
    proc = multiprocessing.Process(target=extract_text_from_pdf, args=(pdf_path, txt_path, pdf_to_txt_log_path))
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        log_error(f"TIMEOUT ERROR: Failed to process {pdf_path} within {timeout} seconds\n\n.", pdf_to_txt_log_path)
        print(f"Timeout error: Failed to process {pdf_path} within {timeout} seconds.\n\n")

#Function - Extract Word-length of a Paper (based on TXT file)
def count_words_in_file(file_path, log_path):
    """
    Count the number of words in a text file.

    Args:
    file_path (str): The path to the text file.
    log_path (str): Path to the log file for recording errors.

    Returns:
    int: The number of words in the file, or None if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            words = file_content.split()
            return len(words)

    except FileNotFoundError:
        error_message = f"ERROR: Could not count words since the file {file_path} does not exist.\n\n"
        print(error_message)
        log_error(error_message, log_path)
        return None

    except Exception as e:
        error_message = f"ERROR: Could not count words of {file_path}. The error: {str(e)}\n\n"
        print(error_message)
        log_error(error_message, log_path)
        return None

#Function - count words in a string variable
def count_words_in_string(text):
    """
    Count the number of words in a given string.

    Args:
    text (str): The string to be analyzed.

    Returns:
    int: The number of words in the string.
    """
    words = text.split()
    if len(words) == 0:
        return None
    else:
        return len(words)


#Function - Extract citation info from TXT
"""Input - TXT file
Outupt - TXT file"""
def extract_citation_line(paper, cite_log_path):
    """
    Extract a specific citation line from a text file and update the 'cite_line' attribute of the LRPaper object.

    Args:
    paper (LRPaper): The LRPaper object whose citation line is to be extracted.
    cite_log_path (str): Path to the log file for recording the process.

    Returns:
    None: The function updates the LRPaper object and logs the outcome.
    """
    txt_path = paper.full_text
    try:
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            lines = txt_file.readlines()
            cite_start = next((i for i, line in enumerate(lines) if line.startswith("Recommended")), None)

            # Adjust cite_start to skip repeated "Recommended" lines or empty lines
            while cite_start is not None and (lines[cite_start].startswith("Recommended") or not lines[cite_start].strip()):
                cite_start += 1

            cite_end_pattern = re.compile(r'\(\d{4}\)')
            cite_end = next((i for i, line in enumerate(lines) if cite_end_pattern.search(line)), None)

            if cite_start is not None and cite_end is not None and cite_end >= cite_start:
                citation_content = ''.join(lines[cite_start:cite_end+1])
                citation_content = ' '.join(citation_content.split())   # Clean up the content
                paper.cite_line = citation_content # Update the object's attribute
                log_error(f"Successfully extracted citation for {txt_path}.\n\n", cite_log_path)
            else:
                raise ValueError("Citation pattern not found")

    except Exception as e:
        paper.cite_line = "***NO CITATION PATTERN WAS FOUND***"
        log_error(f"ERROR: {str(e)} while processing {txt_path}.\n\n", cite_log_path)
        print(f"ERROR while processing {txt_path}. \n The Error - {str(e)}\n\n")


#Function - Find year, First Page, and volume
def extract_year_from_citation(citation_line):
    """
    Extract the year from a citation line (helper for extract_doc_id_YVP_from_cite_line).

    Args:
    citation_line (str): The citation line from which the year is to be extracted.

    Returns:
    year_num (int): The year extracted from the citation line as an integer.
    doc_id_year (str): The year extracted from the citation line as a string,
                       suitable for use in constructing a document ID.
    """
    year_pattern = re.compile(r'\((\d{4})\)')
    year_match = year_pattern.search(citation_line)
    if year_match:
        year_num = int(year_match.group(1))
        doc_id_year = year_match.group(1)  # String representation for the doc_id
        return year_num, doc_id_year
    else:
        raise ValueError("Year not found in the citation. Thus, skipped also Volume and FirstPage.")


def extract_first_page_from_citation(citation_line, year):
    """
    Extract the first page number from a citation line (helper for extract_doc_id_YVP_from_cite_line).

    Args:
    citation_line (str): The citation line from which the first page number is to be extracted.
    year (int): The year of the publication to assist in locating the first page number.

    Returns:
    int: The first page number extracted from the citation line.
    """
    first_page_pattern = re.compile(r'(\d+)\s+\(' + re.escape(str(year)) + r'\)')
    first_page_match = first_page_pattern.search(citation_line)
    if first_page_match:
        return int(first_page_match.group(1))
    else:
        raise ValueError("First page not found in the citation. Thus, skipped also Volume.")

def extract_volume_from_citation(citation_line, first_page):
    """
    Extract the volume number and its start index from a citation line (helper for extract_doc_id_YVP_from_cite_line).

    Args:
    citation_line (str): The citation line from which the volume number is to be extracted.
    first_page (int): The first page number to assist in locating the volume number.

    Returns:
    volume_num (int): The volume number as an integer.
    doc_id_vol (str): The volume number as a string, padded to ensure three digits,
                      suitable for use in constructing a document ID.
    vol_start_index (int): The start index of the volume number in the citation line.
    """
    volume_pattern = re.compile(r'(\d+)\D+' + re.escape(str(first_page)))
    volume_match = volume_pattern.search(citation_line)
    if volume_match:
        volume_num = int(volume_match.group(1))
        doc_id_vol = volume_match.group(1).zfill(3)  # Ensuring three digits for the doc_id
        vol_start_index = volume_match.start(1)      # Start index of the volume in the citation line
        return volume_num, doc_id_vol, vol_start_index
    else:
        raise ValueError("Volume not found in the citation.")


def extract_doc_id_YVP_from_cite_line(paper, LR_ID, counter, yearvolpage_log_path):
    """
    Extract metadata from the citation line of a paper and construct a document ID.

    Args:
    paper (LRPaper): The LRPaper object.
    LR_ID (int): Identifier for LR.
    counter (int): A counter value.
    yearvolpage_log_path (str): Path to the log file for recording the process.

    Returns:
    None: The function updates the LRPaper object and logs the outcome.
    """
    LR_ID_str = str(LR_ID)
    counter_str = str(counter)

    try:
        citation_line = paper.cite_line.strip()

        try:
            paper.year, doc_id_year = extract_year_from_citation(citation_line)
        except Exception as e:
            paper.year, paper.first_page, paper.vol, paper.vol_start_index = None, None, None, None
            paper.doc_id = int(LR_ID_str + "0000" + "000" + counter_str)  # Seven zeros in a row --> indicating an error via doc_id.
            log_error(f"ERROR with {paper.full_text}: {str(e)}\nCould not extract Year of publication for {paper.full_text}, with doc_id: {paper.doc_id}\n\n", yearvolpage_log_path)
            print(f"ERROR with {paper.full_text}: {str(e)}\nCould not extract Year of publication for {paper.full_text}, with doc_id: {paper.doc_id}\n\n")
            return

        try:
            paper.first_page = extract_first_page_from_citation(citation_line, paper.year)
        except Exception as e:
            paper.first_page, paper.vol, paper.vol_start_index = None, None, None
            paper.doc_id = int(LR_ID_str + doc_id_year + "000" + counter_str)
            log_error(f"ERROR with {paper.full_text}: {str(e)}\nCould not extract First Page for {paper.full_text}, with doc_id: {paper.doc_id}\n\n", yearvolpage_log_path)
            print(f"ERROR with {paper.full_text}: {str(e)}\nCould not extract First Page for {paper.full_text}, with doc_id: {paper.doc_id}\n\n")
            return

        try:
            paper.vol, doc_id_vol, paper.vol_start_index = extract_volume_from_citation(citation_line, paper.first_page)
        except Exception as e:
            paper.vol, paper.vol_start_index = None, None
            paper.doc_id = int(LR_ID_str + doc_id_year + "000" + counter_str)
            log_error(f"ERROR with {paper.full_text}: {str(e)}\nCould not extract Volume for {paper.full_text}, with doc_id: {paper.doc_id}\n\n", yearvolpage_log_path)
            print(f"ERROR with {paper.full_text}: {str(e)}\nCould not extract Volume for {paper.full_text}, with doc_id: {paper.doc_id}\n\n")
            return

        paper.doc_id = int(LR_ID_str + doc_id_year + doc_id_vol + counter_str)

    except Exception as ex:
        paper.year, paper.first_page, paper.vol, paper.vol_start_index = None, None, None, None
        paper.doc_id = int(LR_ID_str + "0000" + "000" + counter_str)  # Seven zeros in a row --> indicating an error via doc_id.
        log_error(f"ERROR with {paper.full_text}: {str(ex)}\nCould not extract Citation Line Pattern for {paper.full_text}, with doc_id: {paper.doc_id}\n\n", yearvolpage_log_path)
        print(f"ERROR with {paper.full_text}: {str(ex)}\nCould not extract Citation Line Pattern for {paper.full_text}, with doc_id: {paper.doc_id}\n\n")

#Function - Generates authors & title Line (authors_title_text)
def create_author_title_line(paper, vol_start_index, auth_title_text_log_path):
    """
    Extract and format the author and title line from the paper's citation line.

    Args:
    paper (LRPaper): The LRPaper object.
    vol_start_index (int): The index where the volume information starts in the citation line.
    auth_title_text_log_path (str): Path to the log file for recording errors.

    Returns:
    None: The function updates the 'authors_title_text' attribute of the LRPaper object.
    """
    try:
        # Extract the required part of the text from 'cite_line'
        author_title_text = paper.cite_line[:vol_start_index]
        last_comma_index = author_title_text.rfind(',')
        if last_comma_index != -1:
            author_title_text = paper.cite_line[:last_comma_index]

        # Replace multiple spaces with a single one, replace every ", " with a new line, remove leading/trailing spaces from each line, and uppercase text.
        author_title_text = ' '.join(author_title_text.split())
        author_title_text = author_title_text.replace(", ", "\n")
        author_title_text = "\n".join([line.strip() for line in author_title_text.split("\n")])
        author_title_text = author_title_text.upper()

        paper.authors_title_text = author_title_text

    except Exception as e:
        paper.authors_title_text = None
        error_message = f"ERROR: {str(e)} \nAn error occurred while extracting the author/title line for {paper.full_text} (doc_id: {paper.doc_id}).\n\n"
        print(error_message)
        log_error(error_message, auth_title_text_log_path)

#Function - Extract authors & title (extracting from authors_title_text)
def extract_authors_and_title(paper, extract_authors_and_title_log_path):
    """
    Extract and assign authors and title from the 'authors_title_text' attribute of a paper object.

    Args:
    paper (LRPaper): The LRPaper object from which authors and title are to be extracted.
    extract_authors_and_title_log_path (str): Path to the log file for recording errors.

    Returns:
    None: The function updates the 'authors' and 'title' attributes of the LRPaper object.
    """
    temp_authors_title = getattr(paper, 'authors_title_text', None)
    curr_authors = None
    curr_title = None

    try:
        if temp_authors_title and isinstance(temp_authors_title, str):
            lines = temp_authors_title.strip().split('\n')

            if '&' in temp_authors_title: # Check if "&" character is present in the text
                if '&' in lines[0]:  # If "&" is in the first line, split the authors
                    authors = [author.strip() for author in lines[0].split('&')]
                    curr_authors = authors
                    curr_title = ', '.join(line.strip() for line in lines[1:]) # Combine the remaining lines into the title, replacing new lines with ", "
                else:  # "&" present, but not in the first line (i.e., more than two authors OR '&' in the title) - need to be treated differently.
                    log_error(f"Unexpected format: '&' is present, but NOT in the first line: {temp_authors_title}\nPassing this LRPaper to the funtion 'multipleauthors_OR_ampersand_extract_authors_and_title'", extract_authors_and_title_log_path)
                    paper.authors, paper.title = multipleauthors_OR_ampersand_extract_authors_and_title(paper, extract_authors_and_title_log_path)
                    return

            else:  # "&" not present at all, thus the first line is the single author's name
                curr_authors = [lines[0].strip()]
                curr_title = ', '.join(line.strip() for line in lines[1:]) # Combine the remaining lines into the title, replacing new lines with ", "

        else: # If 'temp_authors_title' is not valid, raise an error to trigger the error handling
            raise ValueError(f"Invalid 'authors_title_text' attribute. Currently, authors_title_text holds the value: {paper.authors_title_text}")

    except Exception as e:
        curr_authors = None
        curr_title = None
        error_message = f"ERROR: Could not identify authors and title for {paper.full_text}. (doc_id: {paper.doc_id}).\nError Type: {str(e)}\n\n"
        print(error_message)
        log_error(error_message, extract_authors_and_title_log_path)

    paper.authors, paper.title = curr_authors, curr_title


#Function - Alternative Function for Extracting Authors, Titles ---> IN CASES OF '&' WITHIN THE TITLE (after the 1st line)
def multipleauthors_OR_ampersand_extract_authors_and_title(paper, extract_authors_and_title_log_path):
    try:
        tmp_authors, tmp_title = None, None
        authors_error, title_error = False, False
        log_error(f"Processing authors and title for {paper.filename} via the alternative function ('multipleauthors_OR_ampersand_extract_authors_and_title').", extract_authors_and_title_log_path)
        with open(paper.PDF, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata
    except Exception as e:
        error_message = f"ERROR: Problem with accessing the PDF file *OR* in reading it. Error type: {str(e)}\n\n"
        log_error(error_message, extract_authors_and_title_log_path)
        return tmp_authors, tmp_title

    try:
        tmp_authors = metadata.get('/Author')
        if tmp_authors:
            tmp_authors = tmp_authors.replace(", and ", ";")
            tmp_authors = tmp_authors.replace(" and ", ";")
            tmp_authors = tmp_authors.replace(", & ", ";")
            tmp_authors = tmp_authors.replace(" & ", ";")
            tmp_authors = tmp_authors.replace(", ", ";")
            tmp_authors = tmp_authors.split(";")
    except Exception as e:
        authors_error = True

    try:
        tmp_title = metadata.get('/Title')
    except Exception as e:
        title_error = True

    error_message = ""
    if authors_error and title_error:
        error_message = f"ERROR: Could not identify authors AND title for {paper.full_text} via the alternative function. (doc_id: {paper.doc_id}).\nError Type: {str(e)}\n\n"
    elif authors_error:
        error_message = f"ERROR: Found title, BUT could not identify authors for {paper.full_text} via the alternative function. (doc_id: {paper.doc_id}).\nError Type: {str(e)}\n\n"
    elif title_error:
        error_message = f"ERROR: Found authors, BUT could not identify title for {paper.full_text} via the alternative function. (doc_id: {paper.doc_id}).\nError Type: {str(e)}\n\n"

    if error_message:
        print(error_message)
        log_error(error_message, extract_authors_and_title_log_path)

    return tmp_authors, tmp_title


#Function - Find Horozontal Lines in a Page
### Try to tweak the following varialbes to make a more/less stringency with line detection: (1)tolerance (2)connectivity (3)length > height * 20 [change the number to higher/lower ratio] (4)gray_image < 1 (raise 1 to get more hues of color and set them as black)
### IMPROVMENT: more stringent and accurate detection by limiting line y-position in the document (line is only valid if it lower than XXX) ---> Can add this condition after the line of "height <= line_thickness_tolerance and length > height * 20"
def find_horizontal_lines(current_page_num, image_np, blindspot, grayscale_threshold, thickness_tolerance, min_length):### A higher number for line_thickness_tolerance means the function will be less strict and consider thicker shapes as potential lines.
                                                              ### Conversely, a lower number means the function will be more stringent, only accepting very thin, almost perfect lines
                                                              ### This tolerance is measured in pixels, which are the tiny dots that make up an image on the screen. So, "1" means one pixel
                                                              ### maybe change thickness for different journals
    """
    Find horizontal lines in an image based on specific criteria.

    Args:
    current_page_num (int): The current page number being processed.
    image_np (numpy.ndarray): The image in which to find horizontal lines.
    blindspot (float): The proportion of the image to ignore from the top.
    grayscale_threshold (int): The threshold value to convert the image to binary.
    thickness_tolerance (int): The tolerance for the thickness of the lines.
    min_length (int): The minimum length for a region to be considered a line.

    Returns:
    list: A list of tuples, each representing the position and length of a detected horizontal line.
    """
    image_height = image_np.shape[0] # shape[0] holds the height (number of rows)
    min_distance_from_top = blindspot * image_height # calculate min distance from top, based on blindspot and the image_height

    gray_image = np.mean(image_np, axis=2) # Convert the image to grayscale; axis=2 means collapsing each 3D RGB represented pixel into a 2D BW pixel (resulting in a grayscale image)

    ###Check
    #max_value, min_value = np.max(gray_image), np.min(gray_image)
    #print(f"Grayscale Threshold is currently: {grayscale_threshold}\n Max value: {max_value}, Min value: {min_value}")

    # Create a binary image based on the grayscale threshold
    binary_image = gray_image < grayscale_threshold  #  Black is represented by 0, White is represented by 255
                                    # Setting here a higher number means 'catching' more cases (not necessarily correct ones, as we get farther from Black)

    # Label connected regions in the binary image
    labels = measure.label(binary_image, connectivity=2) # "2" (or 8-connectivity) means that a pixel can be connected to another if it is touching it from any side or even just a corner. It's the more inclusive option, allowing diagonal connections.
                                                          # "1" (or 4-connectivity) would mean pixels have to be touching sides, not just corners, to be considered connected.
                                                          # Implications: "2" means more shapes will be considered single regions because it allows for diagonal connections. "1"  means fewer shapes will be grouped together, possibly leading to more, smaller regions.
    props = measure.regionprops(labels)

    # Identify horizontal lines from labeled regions
    horizontal_lines = []
    for region in props:
        min_row, min_col, max_row, max_col = region.bbox
        height = max_row - min_row
        length = max_col - min_col

        # Check if region meets the criteria for a horizontal line (low height compared to length)
        if (height <= thickness_tolerance and # Condition for thickness tolerance
           length > min_length and # Condition for minimum length
           min_row > min_distance_from_top): # Condition to avoid blindspot area
            horizontal_lines.append((min_row, length))
            ###Check
            #print(f"Page {current_page_num+1}: Length {length}, Height {height}, Minimal allowed length = {min_length}")
            #print(f"Detected line thickness: \n{height}")

    return horizontal_lines


#Function - Process FNs and Main
def fns_and_main_processing(paper, main_fns_texts_dir, main_fns_text_division_log_path, first_last_fns_log_path,
                            blindspot_area, zoom, grayscale_threshold, thickness_tolerance, min_length):
    """
    Process the given paper's PDF to separate the main text and footnotes.

    Args:
    paper (LRPaper): The paper object containing the PDF path.
    main_fns_texts_dir (str): Directory where the extracted texts will be saved.
    main_fns_text_division_log_path (str): Log file path for this processing step.
    first_last_fns_log_path (str): Log file path for first and last footnotes.
    blindspot_area (float): Area at the top of the page to ignore when finding lines.
    zoom (float): Zoom level for rendering the page.
    grayscale_threshold (int): Threshold for converting the image to binary.
    thickness_tolerance (int): Tolerance for the thickness of detected lines.
    min_length (int): Minimum length for a line to be considered.

    Returns:
    main_txt_path (str): Path to the file where the merged main text of the document is saved.
    fns_txt_path (str): Path to the file where the merged footnotes text of the document is saved.
    """
    main_txt_path = fns_txt_path = None

    if paper.PDF is None:
        print("Error: PDF attribute is None for paper:", paper.full_text)
        log_error("Error: PDF attribute is None for paper: "+paper.full_text+"\n", main_fns_text_division_log_path)
        return main_txt_path, fns_txt_path

    complete_main_text, complete_fns_text = [], []

    try:
        with fitz.open(paper.PDF) as pdf_document:
            num_pages = len(pdf_document)
            log_error("Currently processing file: "+paper.full_text+"\n", main_fns_text_division_log_path)

            for current_page_num in range(1, num_pages): # 1 here skips the title page
                #print(f"Processing text on page {current_page_num+1}")
                page = pdf_document[current_page_num] # If encountering a problem, change to "page = pdf_document.load_page(current_page_num)"
                mat = fitz.Matrix(zoom, zoom) # Render the page as an image using the zoom factor (zooming the picture [via matrix])
                pix = page.get_pixmap(matrix=mat, alpha=False) # representing the actual image
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # Convert the PyMuPDF pixmap to a PIL (Python Image Library) Image
                image_np = np.array(image) # Convert the image to a NumPy array for analysis

                # Process each page based on whether it is the first page or not (if first page -> delibartely ignore the blindspot area ; otherwise, no need for a blindspot)
                horizontal_lines = find_horizontal_lines(current_page_num, image_np, blindspot_area if current_page_num == 1 else 0, grayscale_threshold, thickness_tolerance, min_length)

                if not horizontal_lines: # i.e., horizontal_lines is an empty list, namely, no separating line was found
                    log_error(f"ATTENTION: No separating line found on page {current_page_num+1}.\n", main_fns_text_division_log_path)
                    #print(f"ATTENTION: No separating line found on page {current_page_num+1}.")

                    try:
                        #print(f"Therefore, assiging all text on page {current_page_num+1} as Main Text.")
                        text_above = page.get_text()
                        #print(f"The text that was identified on page {current_page_num+1} is: \n", text_above)
                        complete_main_text.append(text_above)
                    except: # probably an empty page
                        #print(f"No text was found on page {current_page_num+1}, so moving forward.")
                        complete_main_text.append("\n")
                    continue  # continue to the next page of this file

                else:
                    #print(f"Found a separating line on page {current_page_num+1}.")
                    longest_line = max(horizontal_lines, key=lambda x: x[1])  # The line with the maximum length
                    line_position_pdf = longest_line[0] / zoom  # Approximate position in the PDF coordinates
                    # VERIFICATION print(longest_line[1])
                    # VERIFICATION print(f"The most prominent horizontal line is at position {line_position_pdf} (length: {longest_line[1]/zoom} pixels)")
                    # Find the text above and below the horizontal line
                    text_above, text_below = "", ""

                    # Define the area above the horizontal line for text extraction
                    # Ensure this rect is correctly defined with proper coordinates
                    rect_above_line = fitz.Rect(0, 0, page.rect.width, line_position_pdf)
                    # Extract text from the area above the horizontal line
                    text_above = page.get_text("text", clip=rect_above_line)
                    complete_main_text.append(text_above)

                    # Define the area below the horizontal line for text extraction
                    # Ensure this rect is correctly defined with proper coordinates
                    rect_below_line = fitz.Rect(0, line_position_pdf, page.rect.width, page.rect.height)
                    # Extract text from the area below the horizontal line
                    text_below = page.get_text("text", clip=rect_below_line)
                    complete_fns_text.append(text_below)

                    #print(f"The text above the line on page {current_page_num+1} is:\n {text_above} \n\n\n.")
                    #print(f"The text below the line on page {current_page_num+1} is:\n {text_below} \n\n\n.")

                #print(f"*******Finished text extraction for page {current_page_num+1}.*******")

            merged_main_text = "".join(complete_main_text)
            #print(f"All Main Text on file {paper.filename}: \n {merged_main_text}")
            merged_fns_text = "".join(complete_fns_text)
            #print(f"All FNs Text on file {paper.filename}: \n {merged_fns_text}")
            #VERIFICATION print(merged_main_text)
            #VERIFICATION print(merged_fns_text)
            main_txt_path = os.path.join(main_fns_texts_dir, (paper.filename + "_M"+ ".txt"))
            fns_txt_path = os.path.join(main_fns_texts_dir, (paper.filename + "_FN"+ ".txt"))

            with open(main_txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(merged_main_text)

            with open(fns_txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(merged_fns_text)

            # logging finish point of processing Main and FNs text for this PDF file
            log_error(f" Finished processing Main and FNs text for file: {paper.full_text}\n\n", main_fns_text_division_log_path)

    except Exception as e:
        main_txt_path=None
        fns_txt_path=None
        log_error(f" ERROR: Could not open/read PDF for file: {paper.full_text}\n\n", main_fns_text_division_log_path)
        print(f" ERROR {str(e)}: Could not open/read PDF for file {paper.full_text}\n\n")

    return main_txt_path, fns_txt_path


def fns_and_main_processing_with_timeout(paper, main_fns_texts_dir, main_fns_text_division_log_path, first_last_fns_log_path,
                                         blindspot_area, zoom, grayscale_threshold, thickness_tolerance, min_length, timeout=60):

    # This internal function will be run in a separate process and is designed to put its return values into a queue
    def process_wrapper(queue, *args):
        result = fns_and_main_processing(*args)  # calling the original function with the arguments passed to the process
        queue.put(result)

    # Create a queue to share results
    result_queue = multiprocessing.Queue()

    # Set up the process with the wrapper function and pass the necessary arguments
    proc_args = (paper, main_fns_texts_dir, main_fns_text_division_log_path, first_last_fns_log_path,
                 blindspot_area, zoom, grayscale_threshold, thickness_tolerance, min_length)
    proc = multiprocessing.Process(target=process_wrapper, args=(result_queue, *proc_args))

    proc.start()  # start the process
    proc.join(timeout)  # Allow the process to run for 'timeout' seconds

    if proc.is_alive():
        # If the process is still running after 'timeout' seconds, terminate it
        proc.terminate()
        proc.join()  # Ensure all resources are cleaned up

        # Log the timeout error
        log_error(f"TIMEOUT ERROR: Failed to process {paper.full_text} within {timeout} seconds.\n\n", main_fns_text_division_log_path)
        print(f"Timeout error: Failed to process {paper.full_text} within {timeout} seconds.\n")
        main_txt_path = fns_txt_path = None  # You might want to handle this case differently, depending on your needs

    else:
        # If the process finished successfully, retrieve the results from the queue
        main_txt_path, fns_txt_path = result_queue.get()  # This will block until there are items in the queue

        # Now, you can return these values to the caller, or do additional processing
    return main_txt_path, fns_txt_path


#Function - Clear journal Name from main_text
def clear_journal_name(paper, main_fns_text_division_log_path):
    """
    Remove instances of the journal's name from the main text of a paper and update the main text length.

    Args:
    paper (LRPaper): The paper object containing the journal name and main text file path.
    main_fns_text_division_log_path (str): Path to the log file for recording errors.

    Returns:
    None: The function updates the 'main_text' and 'main_text_length' attributes of the paper object.
    """
    if (paper.main_text is None) or (paper.journal is None):
        error_message = f"ERROR: Journal or main_text is None, thus unable to clear journal name for: {paper.full_text}\n\n"
        print(error_message)
        log_error(error_message, main_fns_text_division_log_path)
        return

    #CEHCK print("Main Length pre - ", paper.main_text_length)
    try:
        with open(paper.main_text, 'r', encoding='utf-8') as file:
            file_content = file.read()
    except Exception as e:
        error_message = f"ERROR: {str(e)}\nCould not open/read main_text file for: {paper.full_text}.\n\n"
        print(error_message)
        log_error(error_message, main_fns_text_division_log_path)
        return

    # removing journal name and updating the main_text file
    try:
        # pattern is the word to remove (journal), case insensitivity
        pattern = re.compile(re.escape(paper.journal), re.IGNORECASE)
        updated_content = pattern.sub('', file_content)
        with open(paper.main_text, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        paper.main_text_length = count_words_in_file(paper.main_text, main_fns_text_division_log_path)

    #CHECK print("Main Length post - ", paper.main_text_length)

    except Exception as e:
        error_message = f"ERROR {str(e)}: Error while removing journal name / rewriting the main_text file for: {paper.full_text}.\n\n"
        print(error_message)
        log_error(error_message, main_fns_text_division_log_path)
        return

#Function - Find First, Last, and Total FNs
def extract_first_last_total_fns(paper, first_last_fns_log_path):
    """
    Extract the first and last footnotes and the total number of footnotes from a paper.

    Args:
    paper (Paper): The paper object containing the footnotes text file path.
    first_last_fns_log_path (str): Path to the log file for recording errors.

    Returns:
    None: The function updates the 'first_fn_num', 'last_fn_num', 'total_fns', 'first_fn_text', and 'last_fn_text' attributes of the paper object.
    """
        # helper func - check sequential triplet
    def is_sequential(sub_list):
        """
        Check if a sublist of footnotes is sequential.
        Args:
        sub_list (list): A list of footnote tuples.
        Returns:
        bool: True if the footnotes are sequential, False otherwise.
        """
        return all(sub_list[i][0] + 1 == sub_list[i + 1][0] for i in range(len(sub_list) - 1))

    # helper func - remove duplications
    def remove_duplicates(sorted_list):
        """
        Remove duplicate entries from a sorted list of footnotes.
        Args:
        sorted_list (list): A sorted list of footnote tuples.
        Returns:
        list: A deduplicated list of footnotes.
        """
        if len(sorted_list) <= 1:
            return sorted_list

        deduplicated_list = [sorted_list[0]]
        existing_keys = {sorted_list[0][0]}  # Set containing the keys of the tuples already added

        for element in sorted_list[1:]:
            if element[0] not in existing_keys:
                deduplicated_list.append(element)
                existing_keys.add(element[0])

        return deduplicated_list


    if not paper.fns_text:  # empty path
        print("Path is empty\n")
        log_error("Path is empty\n\n", first_last_fns_log_path)
        return

    try:
        first_fn = last_fn = total_fn = None
        with open(paper.fns_text, 'r', encoding='utf-8') as file:
            fns_lines = file.readlines()

        # Define the regex pattern for footnotes, ensuring there's a period (with optional space) after the number
        pattern = re.compile(r'^\s*(\d{1,3}) ?\.(.*)', re.MULTILINE)

        matches = []
        for line in fns_lines:
            match = pattern.match(line)
            if match:
                # match.group(0) is the entire matched string (the full line here)
                full_line = match.group(0).strip()
                # match.group(1) is the number, we convert it to an integer
                footnote_number = int(match.group(1))
                matches.append((footnote_number, full_line))

        matches.sort(key=lambda x: x[0])  # Sorting by the first element of the tuple
        matches = remove_duplicates(matches)

        if not matches:
            return

        # Find the first sequence of three sequential numbers
        for i in range(len(matches) - 2):
            if is_sequential(matches[i:i + 3]):
                first_fn = matches[i][0]
                break

        # Find the last sequence of three sequential numbers
        for i in range(len(matches) - 3, -1, -1):
            if is_sequential(matches[i:i + 3]):
                last_fn = matches[i + 2][0]  # This is the last number of the found sequence
                break

        # Additional checks if necessary
        if len(matches) > 3 and first_fn is not None and last_fn is not None:
            if last_fn <= first_fn:
                first_fn = None
                last_fn = None

        paper.first_fn_num = first_fn
        paper.last_fn_num = last_fn
        if paper.last_fn_num >= paper.first_fn_num:
            paper.total_fns = paper.last_fn_num - paper.first_fn_num + 1

        for match in matches:
            if match[0] == first_fn:
                paper.first_fn_text = match[1]  # The text of the footnote
                #print(paper.first_fn_text)
                break

        for i in range(len(matches) - 1, -1, -1):
            match = matches[i]
            if match[0] == last_fn:
                paper.last_fn_text = match[1]  # The text of the footnote
                #print(paper.last_fn_text)
                break

    except Exception as e:
        error_message = f"ERROR: Could not process the FNs order/counting/text for {paper.full_text}.\n"
        print(error_message)
        log_error(error_message+"\n", first_last_fns_log_path)
        paper.first_fn_num = paper.last_fn_num = paper.total_fns = paper.first_fn_text = paper.last_fn_text = None

#Function - Extract acknowledgment Paragraph
def extract_acknowledgment_text(paper, ACK_log_path):
    """
    Extract the acknowledgment text from the footnotes of a paper.

    Args:
    paper (Paper): The paper object containing the footnotes text file path and first footnote text.
    ACK_log_path (str): Path to the log file for recording errors.

    Returns:
    None: The function updates the 'acknowledgment' attribute of the paper object.
    """
    block_pattern = re.compile(r'^\s*(\d{1,3}) ?\.', re.MULTILINE)
    try:
        if (paper.fns_text is None) or (paper.first_fn_text is None):
            return

        with open(paper.fns_text, 'r', encoding='utf-8') as txt_file:
            all_fn_text = txt_file.read()
            #print("looking for the following text:", paper.first_fn_text)
            if paper.first_fn_text in all_fn_text:
                first_fn_index = all_fn_text.find(paper.first_fn_text)
                ACK_text = all_fn_text[:first_fn_index]
                ACK_text = clean_text(ACK_text)
                #print("After cleaning:", ACK_text,"\n\n")
                if not ACK_text or ACK_text.isspace(): # ACK_text is empty or includes only spaces, thus practically empty.
                    #print("This ACK is empy!\n\n")
                    ACK_text = "No acknowledgment Text"
                else: # ACK_text is not empty or just spaces
                    # Cheking if the ACK_text is actually a false positive in the shape of fns from a previous paper or text mis-extraction
                    for line in ACK_text.split('\n'):
                        if block_pattern.match(line):
                            # If any line matches the pattern, set ACK_text to the specified value
                            ACK_text = "No acknowledgment Text"
                            break

            else:
                ACK_text = None
                message = f"ATTENTION: Could not find the first FN in the FNs text! File: {paper.full_text}.\n"
                print(message)
                log_error(message+"\n", ACK_log_path)

    except Exception as e:
        ACK_text = None
        error_message = f"ERROR {str(e)} while processing acknowledgment information for {paper.full_text}.\n"
        print(error_message)
        log_error(error_message+"\n", ACK_log_path)

    paper.acknowledgment = ACK_text


#Function - Splitting and Extracting start/mid/end
def split_start_mid_end(paper, SME_log_path, SME_dir):
    """
    Split the main text of a paper into start, middle, and end segments, and save them to separate files.

    Args:
    paper (Paper): The paper object containing the main text file path and filename.
    SME_log_path (str): Path to the log file for recording errors.
    SME_dir (str): Directory path where the segmented files will be saved.

    Returns:
    None: The function updates the 'start', 'mid', and 'end' attributes of the paper object with file paths.
    """
    if (paper.main_text is None) or (paper.main_text_length is None):
        message = f"Skip Message: No main_text for file {paper.full_text}.\n"
        log_error(message+"\n", SME_log_path)
        return

    try:
        with open(paper.main_text, 'r', encoding='utf-8') as text_file:
            main_text = text_file.read()

        # Check if empty, or just whitespace
        if not main_text or len(main_text.strip()) == 0 or main_text.isspace() or paper.main_text_length < 100:
            message = f"ATTENTION: main_text seems to be empty or extremely short! File skipped: {paper.full_text}."
            print(message)
            log_error(message, SME_log_path)
            return

        words = main_text.split(' ')
        main_text_length = len(words)
        start, mid, end = "", "", ""

        # Create start, mid, end files
        # If the text length is 4500 words or more
        if main_text_length >= 4500:
            start = " ".join(words[:1500])
            mid_start = (main_text_length - 1500) // 2
            mid_end = mid_start + 1500
            mid = ' '.join(words[mid_start:mid_end])
            end = " ".join(words[-1500:])

        # Text is shorter than 4500 words
        else:
            paper.short_SME_flag = True
            one_third = main_text_length // 3
            start = " ".join(words[:one_third])
            mid = " ".join(words[one_third:one_third*2])
            end = " ".join(words[one_third*2:])

        # Save the segments into files
        if all([start, mid, end]): # if any is None, skip this part
            start_path = os.path.join(SME_dir, f"{paper.filename}_start.txt")
            mid_path = os.path.join(SME_dir, f"{paper.filename}_mid.txt")
            end_path = os.path.join(SME_dir, f"{paper.filename}_end.txt")
            with open(start_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(start)
            with open(mid_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(mid)
            with open(end_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(end)

            paper.start, paper.mid, paper.end = start_path, mid_path, end_path

    except Exception as e:
        message = f"ERROR {str(e)}\nwhile processing start / mid / end text for file {paper.full_text}.\n\n"
        print(message)
        log_error(message, SME_log_path)
        paper.start = paper.mid = paper.end = None


#Function - Merge start + mid + end into one file
def merge_SME(paper, SME_dir, SME_log_path, ignore_factor = 0.6):
    """
    Merge the start, middle, and end text segments of a paper into a single file.

    Args:
    paper (Paper): The paper object with paths to the text segments and flags.
    SME_dir (str): Directory where the merged file will be saved.
    SME_log_path (str): Path to the log file for recording errors.
    ignore_factor (float): Factor to determine how much of the start and end segments to ignore in short SME merging.

    Returns:
    None: The function updates the 'SME' attribute of the paper object with the merged file path.
    """

    def read_partial_file(file_path, exclude_start=None, exclude_end=None):
        """
        Reads a file and returns its content, excluding certain portions if specified.

        Args:
        file_path (str): The path to the text file.
        exclude_start (int, optional): Number of words to exclude from the start.
        exclude_end (int, optional): Number of words to exclude from the end.

        Returns:
        str: The modified content of the file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.read().split()
            if exclude_start:
                words = words[exclude_start:]
            if exclude_end:
                words = words[:-exclude_end] if exclude_end else words
            return ' '.join(words)

    # Check if any of the file paths are None
    if any(getattr(paper, attr) is None for attr in ['start', 'mid', 'end']):
        missing_attributes = [attr for attr in ['start', 'mid', 'end'] if getattr(paper, attr) is None]
        message = f"Skipped the file {paper.filename}: The following attributes are None: {', '.join(missing_attributes)}\n"
        print(message)
        log_error(message+"\n", SME_log_path)
        return

    # Check if general_length_problem_flag is True
    if paper.general_length_problem_flag:
        message = f"Skipped the file {paper.filename}: The general_length_problem_flag is set to TRUE.\n"
        print(message)
        log_error(message+"\n", SME_log_path)
        return

    # Define the separator pattern
    separator = "\n" + ".....\n" * 5 ### here I removed "\n" at the end
    # Construct the full path for the new file
    merged_file_path = os.path.join(SME_dir, f"{paper.filename}_SME.txt")
    paper.SME = merged_file_path

    try:
        title = paper.title if paper.title is not None else ""
        with open(merged_file_path, 'w', encoding='utf-8') as merged_file:
            if paper.short_SME_flag is False: # regular SME, with sequence breaking between start / mid / end, and therefore adding a separator.
                    # Write the contents to the merged file with separators in between
                    merged_file.write(title+":\n")
                    merged_file.write(read_partial_file(paper.start))
                    merged_file.write(separator)
                    merged_file.write(read_partial_file(paper.mid))
                    merged_file.write(separator)
                    merged_file.write(read_partial_file(paper.end))
                    merged_file.write("\n"+title)

            else: # short SME, with NO sequence breaking between start / mid / end. Therefore, do not add a separator AND remove ignore_factor from start's beggining and end's ending.
                total_expected_len = sum(count_words_in_file(path, SME_log_path) for path in [paper.start, paper.mid, paper.end])
                # Determine the portions to be excluded
                if total_expected_len >= 2000:
                    start_exclude = 500
                    end_exclude = 500
                else:
                    start_exclude = int(count_words_in_file(paper.start, SME_log_path) * ignore_factor)
                    end_exclude = int(count_words_in_file(paper.end, SME_log_path) * ignore_factor)

                # Write the merged file while removing portions of 'start' and 'end'
                merged_file.write(title+":\n")
                merged_file.write(read_partial_file(paper.start, exclude_start=start_exclude)) # begining of 'start' is being removed
                merged_file.write(read_partial_file(paper.mid))  # 'mid' is included in full
                merged_file.write(read_partial_file(paper.end, exclude_end=end_exclude)) # ending of 'end' is being removed
                merged_file.write("\n"+title)

    except Exception as e:
        message = f"An error occurred while trying to merge start/mid/end of {paper.filename}: {e}\n"
        print(message)
        log_error(message+"\n", SME_log_path)


#Function - Remove Extra Lines for **main_text**
def is_title_or_uppercase(line):
    """Check if the given line is in title case or uppercase."""
    return line == line.title() or line == line.upper()

def is_mostly_uppercase(line):
    """Check if at least 75% of the line's characters are uppercase."""
    uppercase_chars = sum(1 for char in line if char.isupper())
    percentage_uppercase = (uppercase_chars / len(line)) * 100 if line else 0
    return percentage_uppercase >= 75

def ends_with_punctuation(line):
    """Check if the given line ends with a punctuation character, excluding the dash and comma."""
    if line:
        last_char = line[-1]
        return last_char in string.punctuation and last_char not in ('-', ',')
    return False

def can_join(next_line):
    """Check if the next line can be joined with the previous line."""
    stripped_next_line = next_line.strip()
    if not stripped_next_line:  # if next line is empty, we can join
        return True

    # Check if the next line is in title case, uppercase, or mostly uppercase
    if (is_title_or_uppercase(stripped_next_line) or
        is_mostly_uppercase(stripped_next_line)):
        return False  # cannot join

    return True  # can join

def remove_extra_lines_main(paper, orig_length, log_path):
    try:
        with open(paper.main_text, 'r') as file:
            lines = file.readlines()

        # shold be in the main code ---> text_after_removing_lines = ''.join(processed_lines)
        processed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped_line = line.rstrip()

            # If the line is empty or meets certain conditions, we don't join it with the next line.
            if (not stripped_line or
                is_title_or_uppercase(stripped_line) or
                is_mostly_uppercase(stripped_line) or
                ends_with_punctuation(stripped_line)):
                processed_lines.append(line)
                i += 1
                continue

            # If this is the last line, no joining is needed.
            if i == len(lines) - 1:
                processed_lines.append(line)
                break  # Exit the loop as this is the last line

            # Check the next line
            next_line = lines[i + 1]
            if can_join(next_line):
                # Determine if we need to remove a character (for the dash) and join the lines
                if stripped_line.endswith('-'):
                    # For a dash, we join the lines directly
                    new_line = stripped_line[:-1] + next_line.lstrip()
                elif stripped_line.endswith(','):
                    # For a comma, we need to ensure a space is maintained after it
                    new_line = stripped_line + ' ' + next_line.lstrip() if not next_line.startswith(' ') else stripped_line + next_line.lstrip()
                else:
                    # For normal cases, ensure a space separates the joined lines
                    new_line = stripped_line + ' ' + next_line.lstrip()

                # Add the newly formed line to the processed list
                processed_lines.append(new_line)
                i += 2  # Move the index by 2 as we've processed an extra line
            else:
                processed_lines.append(line)
                i += 1  # Move to the next line

        text_after_removing_lines = ''.join(processed_lines)
        current_length = count_words_in_string(text_after_removing_lines)
        if (orig_length > current_length*1.05) or (orig_length < current_length*0.95):
            print(f"ERROR: The lines removal caused a major words loss / addition (more than 5%) for {paper.full_text}:\n\n")
            print(f"Original length: {orig_length}")
            print(f"Updated length: {current_length}\n\n")
            with open(log_path, 'a', encoding='utf-8') as log_file:
                now = datetime.datetime.now()
                log_file.write(str(now))
                log_file.write(f"ERROR: The lines removal caused a major words loss / addition (more than 5%) for {paper.full_text}")
                log_file.write(f"Original length: {orig_length}")
                log_file.write(f"Updated length: {current_length}\n\n")
            return
            #print(f"The lines removal caused a major words loss / addition (more than 5%) for {paper.FullText}:")
            #print(f"Original length: {orig_length}")
            #print(f"Updated length: {current_length}")

        else:
            with open(paper.main_text, 'w', encoding='utf-8') as file:
                file.write(text_after_removing_lines)

    except Exception as e:
        print(f"ERROR while removing extra lines for {paper.full_text}\n\n")
        with open(log_path, 'a', encoding='utf-8') as log_file:
            now = datetime.datetime.now()
            log_file.write(str(now))
            log_file.write(f" ERROR while trying to remove extra lines for {paper.full_text}\n\n")


#Function - Add Missing Lines for **main_text**
def add_missing_lines_main(paper, orig_length, abbrevs, log_path):

    try:
        with open(paper.main_text, 'r') as file:
            lines = file.readlines()
        new_text = ""

        for line in lines:
            # If the line is empty or contains only whitespace, we skip it
            if line.strip() == "":
                new_text += line  # We're preserving the blank line here
                continue

            temp_period_index = 0
            while temp_period_index < len(line):
                # Find the next period in the line
                next_period_index = line.find('.', temp_period_index)

                if next_period_index == -1:  # No more periods in the line
                    break

                # Check if this period is part of an abbreviation
                is_abbreviation = any(line[next_period_index - len(abbrev):next_period_index + 1] == abbrev for abbrev in abbrevs)

                # Check for ' v' or ' V' before the period
                is_special_v_case = line[next_period_index - 2:next_period_index] == " v" or line[next_period_index - 2:next_period_index] == " V"

                # If it's an abbreviation or special 'v' case, we skip to the next period
                if is_abbreviation or is_special_v_case:
                    temp_period_index = next_period_index + 1
                    continue

                # Check if the period is followed by a number, and if so, treat the number as the period
                match = re.match(r"\.\s*\d+", line[next_period_index:])
                if match:
                    # The period is followed by a number, so we consider the number as the period
                    temp_period_index = next_period_index + match.end()
                else:
                    temp_period_index = next_period_index + 1

                # Check the characters after the period to see if we need to insert a newline
                if temp_period_index < len(line) and line[temp_period_index].isspace():
                    # Look ahead to find the next non-space character
                    next_char_index = temp_period_index
                    while next_char_index < len(line) and line[next_char_index].isspace():
                        next_char_index += 1

                    if next_char_index < len(line) and line[next_char_index].isupper():
                        # This looks like the start of a new sentence, so we insert a newline
                        line = line[:temp_period_index] + '\n' + line[temp_period_index:]
                        temp_period_index = next_char_index  # Updating the index to reflect the new line character
                    else:
                        # Not the start of a new sentence, so we just move on
                        continue
                else:
                    # Not the pattern we're looking for, so we just move on
                    continue

            # Append the processed line to the new text
            new_text += line


        current_length = count_words_in_string(new_text)
        if (orig_length > current_length*1.05) or (orig_length < current_length*0.95):
            print(f"ERROR: The lines addition caused a major words loss / addition (more than 5%) for {paper.full_text}")
            print(f"Original length: {orig_length}")
            print(f"Updated length: {current_length}\n\n")
            with open(log_path, 'a', encoding='utf-8') as log_file:
                now = datetime.datetime.now()
                log_file.write(str(now))
                log_file.write(f"ERROR: The lines addition caused a major words loss / addition (more than 5%) for {paper.full_text}\n\n")
                log_file.write(f"Original length: {orig_length}")
                log_file.write(f"Updated length: {current_length}\n\n")
            return

        else:
            with open(paper.main_text, 'w', encoding='utf-8') as file:
                file.write(new_text)

    except Exception as e:
        print(f"ERROR {str(e)} while trying to add missing lines for {paper.full_text}\n\n")
        with open(log_path, 'a', encoding='utf-8') as log_file:
            now = datetime.datetime.now()
            log_file.write(str(now))
            log_file.write(f" ERROR {str(e)} while trying to add missing lines for {paper.full_text}\n\n")

#Function - Reorganize ACK Text
def reorganize_acknowledgment(paper, ACK_log_path):
    try:
        ack_text = paper.acknowledgment
        lines = ack_text.splitlines()
        processed_text = ""

        for line in lines:
            # Check if the line starts with a space followed by a number, 't', '*', or '†'
            if line.startswith(' ') and (line.lstrip()[0].isdigit() or line.lstrip()[0] in ['t', '*', '†']):
                processed_text += "\n" + line
            # Check if the line starts directly with a number, 't', '*', or '†'
            elif line[0].isdigit() or line[0] in ['t', '*', '†']:
                processed_text += "\n" + line
            else:
                processed_text += ' ' + line

        # Join the processed lines
        lines = processed_text.split('\n')
        # Remove '- ' from each line and filter out blank lines
        cleaned_lines = [line.replace("- ", "").strip() for line in lines if line.strip()]
        # Join the cleaned lines back into a single string
        cleaned_text = '\n'.join(cleaned_lines)

        paper.reorg_acknowledgment = cleaned_text
        paper.reorg_acknowledgment_length = count_words_in_string(paper.reorg_acknowledgment)

    except Exception as e:
        paper.reorg_acknowledgment = None
        paper.reorg_acknowledgment_length = None
        print(f"ERROR IN REORGINZING ACK: {e} for the file {paper.fulltext}")
        log_error(f"ERROR IN REORGINZING ACK: {e} for the file {paper.fulltext}.\n\n", ACK_log_path)


###GEN Functions

#GEN Function - Generate Text Files (PDF Extraction)
def gen_extract_text_from_pdf_with_timeout(pdf_dir=pdf_dir, pdf_to_txt_log_path=pdf_to_txt_log_path):
    # PDF Text Extraction
    for filename in tqdm(os.listdir(pdf_dir), desc="Extracting Text from PDFs"):
        log_error(f"Opening file: {filename}\n", pdf_to_txt_log_path)
        print(f"Detected a file: {filename}")
        if filename.endswith(".pdf"):
            log_error(f"Trying to extract text INCLUDING TITLE PAGE from: {filename}\n", pdf_to_txt_log_path)
            pdf_path = os.path.join(pdf_dir, filename)
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(fulltext_dir, txt_filename)
            extract_text_from_pdf_with_timeout(pdf_path, txt_path, pdf_to_txt_log_path, timeout=60)

        else:  # i.e., file does not end with ".pdf"
            print(f"Skip Message: {filename} was skippied as it is not a PDF file.\n\n")
            log_error(f"Skip Message: {filename} was skippied as it is not a PDF file.\n\n", pdf_to_txt_log_path)
    # Intentional delay
    time.sleep(delay)
    # Safety Check = no. of PDFs vs. no. of TXT"""
    num_of_PDFs = count_specific_files(pdf_dir, '.pdf')
    print("Number of PDFs in the PDF folder: " + str(num_of_PDFs))
    num_of_TXTs = count_specific_files(fulltext_dir, '.txt')
    print("Number of TXTs in the Fulltext folder: " + str(num_of_TXTs))
    print("\n")
    # Get the base names (without extension) of all PDF and TXT files
    pdf_filenames = {os.path.splitext(filename)[0] for filename in os.listdir(pdf_dir) if filename.endswith('.pdf')}
    txt_filenames = {os.path.splitext(filename)[0] for filename in os.listdir(fulltext_dir) if filename.endswith('.txt')}
    # Find PDFs that don't have a corresponding TXT file
    mismatched_files = pdf_filenames - txt_filenames
    # Print the names of mismatched files
    if mismatched_files:
        print("Mismatches (PDFs without corresponding TXTs):")
        for file in mismatched_files:
            print(file)
    else:
        print("No mismatches found. All PDFs have corresponding TXTs.")


#GEN Function - Create LRPaper Objects and Extract Core Attributes
def gen_create_objs_refPDF_refulltext_extjournal(papers, pdf_dir=pdf_dir, fulltext_dir=fulltext_dir,
                                                 LR_Name=LR_Name, txt_length_log_path=txt_length_log_path,
                                                 valid_pdf_path_log_path=valid_pdf_path_log_path,
                                                 critical_errors_log_path=critical_errors_log_path):
    # Loop through every file in the directory
    for filename in tqdm(os.listdir(fulltext_dir), desc="Processing Files", unit="file"):
        try:
            if filename.endswith(".txt"):
                file_path = os.path.join(fulltext_dir, filename)
                # Create a new LRPaper object, and assign the file path to the full_text attribute
                new_paper = LRPaper()
                new_paper.full_text = file_path
                new_paper.filename = os.path.splitext(filename)[0]
                pdf_filename = os.path.splitext(filename)[0] + ".pdf"
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                if os.path.exists(pdf_path):
                    new_paper.PDF = pdf_path
                    new_paper.number_of_pages = get_num_of_pages(pdf_path)
                else:
                    print(f"ERROR: No file found at the PDF path:\n{pdf_path}")
                    log_error(f"ERROR: No file found at the PDF path:{filename}\n\
                    No PDF path was addedd; check manually if the path/file is valid.\n\n", valid_pdf_path_log_path)

                new_paper.journal = LR_Name

                # counting general number of words (including title page)
                new_paper.length_original = count_words_in_file(new_paper.full_text, txt_length_log_path)
                # subtracting the number of words from the title page from the
                if (new_paper.number_of_pages is not None) and (new_paper.number_of_pages > 1):
                    words_on_title_page = count_words_in_title_page(new_paper.PDF)
                    new_paper.length_original = new_paper.length_original - words_on_title_page
                    if (new_paper.length_original > 1):
                        new_paper.general_length_problem_flag = False  # flagging there is NO problem with the length
                    else:
                        new_paper.general_length_problem_flag = True  # flagging there is a problem with the length

                papers.append(new_paper)

        except Exception as e:
            print(f"CRITICAL ERROR: Could not create LRPaper object for {filename}.\n")
            log_error(f"CRITICAL ERROR: Could not create LRPaper object for {filename}.\n\n", critical_errors_log_path)
    # print_LRPapers_list(papers)
    # Intentional delay
    time.sleep(delay)

    #Safety Check: No. of LRPapers in the papers list vs. No. of TXT files"""
    num_of_TXTs = count_specific_files(fulltext_dir, '.txt')
    print("Number of TXTs in the Fulltext folder: " + str(num_of_TXTs))
    print("Number of LRPaper objects in current papers list: " + str(len(papers)))


#GEN Function - Extract the citation line
def gen_extract_citation_line(papers, cite_log_path=cite_log_path, fulltext_dir=fulltext_dir):
    for paper in tqdm(papers, desc="Processing papers of the papers list",
                      unit="paper"):  # Iterating over LRPaper objects
        log_error(f"Trying to extract citation from object: {paper.full_text}\n", cite_log_path)
        extract_citation_line(paper, cite_log_path)

    # print_LRPapers_list(papers)
    # Safety Check = no. of TXTs vs. no. of paper objects with legit cite_line
    num_of_TXTs = count_specific_files(fulltext_dir, '.txt')
    print("Number of TXTs in the Fulltext folder: " + str(num_of_TXTs))
    num_of_valid_cite_line = 0
    for paper in papers:
        if paper.cite_line != "***NO CITATION PATTERN WAS FOUND***":
            num_of_valid_cite_line += 1
    print("Number of objects with a valid citation line: " + str(num_of_valid_cite_line))


#GEN Function - Extract DocID and YVP; Create author & title line
def gen_extract_doc_id_YVP_and_create_author_title_line(papers, position_checker=1, UID_counter=10000,
                                                        yearvolpage_log_path=yearvolpage_log_path,
                                                        auth_title_text_log_path=auth_title_text_log_path):
    # Process each LRPaper object
    for paper in tqdm(papers, desc="Processing papers of the papers list", unit="paper"):
        try:
            # Extract information and update object attributes
            extract_doc_id_YVP_from_cite_line(paper, LR_ID, UID_counter,
                                              yearvolpage_log_path)  # assigns values to year, first_page, vol, vol_start_index, and doc_id

            if paper.vol_start_index is None:
                log_error(f"Skip Message: {paper.full_text} (doc_id: {paper.doc_id}) has no vol_start_index.\n\n",
                          auth_title_text_log_path)
                # print(f"Data extraction failed for paper {paper.full_text}, with doc_id: {paper.doc_id}\n")
            else:  # i.e., vol_start_index is not None
                create_author_title_line(paper, paper.vol_start_index, auth_title_text_log_path)

            # Progress tracking
            if position_checker % 100 == 0:
                print(f"Processed {position_checker} papers so far.")

            position_checker += 1
            UID_counter += 1

        except Exception as e:
            # Handle exceptions for each paper processing - only in case the very calling of function raised an issue
            print(
                f"ERROR: {str(e)}\nAn error occurred while processing paper {paper.full_text} (doc_id: {paper.doc_id})")
            print(
                "Could not run the function 'extract_doc_id_YVP_from_cite_line' or the function 'create_author_title_line'\n\n")
            log_error(
                f"ERROR: {str(e)}\nAn error occurred while processing paper {paper.full_text} (doc_id: {paper.doc_id})\n\
            Could not run the function 'extract_doc_id_YVP_from_cite_line' or the function 'create_author_title_line'\n\n",
                auth_title_text_log_path)

    # Intentional delay
    time.sleep(delay)
    # print_LRPapers_list(papers)
    print(len(papers))


#GEN Function - Extract Authors / Titles
def gen_extract_authors_and_title(papers, position_checker=1, extract_authors_and_title_log_path=extract_authors_and_title_log_path):
    # Process each LRPaper object
    for paper in tqdm(papers, desc="Processing papers of the papers list", unit="paper"):
        try:
            # Extract information and update object attributes
            extract_authors_and_title(paper, extract_authors_and_title_log_path)
            # Progress tracking
            if position_checker % 100 == 0:
                print(f"Processed {position_checker} papers so far.")
            position_checker += 1

        except Exception as e:
            # Handle exceptions for each paper processing - only in case the very calling of function raised an issue
            print(
                f"ERROR: - {str(e)}\nA major error occurred while processing paper {paper.full_text} (doc_id: {paper.doc_id})")
            print("Could not run the function 'extract_authors_and_title'\n\n")
            log_error(
                f"ERROR: {str(e)}\nA major error occurred while processing paper {paper.full_text} (doc_id: {paper.doc_id})\n\
            Could not run the function 'extract_authors_and_title'\n\n", extract_authors_and_title_log_path)
    # print_LRPapers_list(papers)


#GEN Function - Partition and Generate Main/FNs Files
def gen_fns_and_main_processing_with_timeout(papers, blindspot_area=0.33, zoom_factor=2, line_grayscale_threshold=128,
                                             line_thickness_tolerance=20, minimal_length=150, timeout=90,
                                             main_fns_texts_dir=main_fns_texts_dir,
                                             main_fns_text_division_log_path=main_fns_text_division_log_path,
                                             first_last_fns_log_path=first_last_fns_log_path):
    for paper in tqdm(papers, desc="Processing papers of the papers list", unit="paper"):
        try:
            paper.main_text, paper.fns_text = fns_and_main_processing_with_timeout(paper, main_fns_texts_dir,
                                                                                   main_fns_text_division_log_path,
                                                                                   first_last_fns_log_path,
                                                                                   blindspot_area, zoom_factor,
                                                                                   line_grayscale_threshold,
                                                                                   line_thickness_tolerance,
                                                                                   minimal_length, timeout)
            paper.main_text_length = count_words_in_file(paper.main_text, main_fns_text_division_log_path)
            paper.fns_text_length = count_words_in_file(paper.fns_text, main_fns_text_division_log_path)
        except Exception as e:
            print(f" ERROR {str(e)}: Could not call the 'fns_and_main_processing' function for: {paper.full_text}\n\n")
            log_error(
                f" ERROR {str(e)}: Could not call the 'fns_and_main_processing' function for: {paper.full_text}\n\n",
                main_fns_text_division_log_path)

        # remove the LR name appearnces from the main_text file
        try:
            clear_journal_name(paper, main_fns_text_division_log_path)
        except Exception as e:
            print(f" ERROR {str(e)}: Could not call the function clear_journal_name for: {paper.full_text}\n\n")
            log_error(f" ERROR {str(e)}: Could not call the function clear_journal_name for: {paper.full_text}\n\n",
                      main_fns_text_division_log_path)
    # print_LRPapers_list(papers)
    # Intentional delay
    time.sleep(delay)



#GEN Function - Remove Redundant Lines in Main Text
def gen_remove_extra_lines_main(papers, main_reorg_log_path):
    for paper in tqdm(papers, desc="Processing papers of the papers list - Removing Redundant Lines", unit = "paper"):
        if paper.main_text is not None:
            #print(f"Removing lines from item: {paper.doc_id}, path: {paper.full_text}")
            original_length = paper.main_text_length
            #print(f"Original length pre lines removal: {original_length}")

            # removing redundant lines
            for cycle in range(6):
                remove_extra_lines_main(paper, original_length, main_reorg_log_path)
                #print(f"Update length after REMOVING, version {cycle+1}: {count_words_in_file(paper.main_text, main_fns_text_division_log_path)}")
                time.sleep(1)
            paper.main_text_length = count_words_in_file(paper.main_text, main_reorg_log_path)
            #print("Fiished with this paper.\n\n\n")


#GEN Function - Add Missing Linebreaks in Main Text
def gen_add_missing_lines_main(papers, main_reorg_log_path):
    abbrevs = {
                "Mr.", "Mrs.", "Ms.", "Dr.", "Jr.", "Sr.", "Inc.", "St.", "Co.", "Ltd.", "Etc.", "etc.",
                "Mt.", "Ft.", "vs.", "et al.", "i.e.", "Et al.", "E.g.", "E.G.", "e.g.", "U.S.",
                "U.S.C.", "C.F.R.", "a.m.", "p.m.","A.M.","P.M."
              }
    for paper in tqdm(papers, desc="Processing papers of the papers list - Adding Missing Lines", unit = "paper"):
        if paper.main_text is not None:
            #print(f"Adding lines to item: {paper.doc_id}, path: {paper.full_text}")
            original_length = paper.main_text_length
            #print(f"Original length pre lines addition: {original_length}")

            for cycle in range(3):
                add_missing_lines_main(paper, original_length, abbrevs, main_reorg_log_path)
                #print(f"Update length after ADDING, version {cycle+1}: {count_words_in_file(paper.main_text, main_fns_text_division_log_path)}")
                time.sleep(1)
            paper.main_text_length = count_words_in_file(paper.main_text, main_reorg_log_path)



#GEN Function - First, Last, and Total FNs
def gen_extract_first_last_total_fns(papers, first_last_fns_log_path):
    for paper in tqdm(papers, desc="Processing papers of the papers list", unit="paper"):
        try:
            extract_first_last_total_fns(paper, first_last_fns_log_path)

        except Exception as e:
            log_error(f"ERROR with calling the function for {paper.full_text}.\n\n", first_last_fns_log_path)
