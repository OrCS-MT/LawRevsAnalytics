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
