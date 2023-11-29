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

## **Class *LRPaper***"""

class LRPaper:
    """
    Represents a Law Review paper, containing various metadata and textual components.
    """

    def __init__(self, doc_id=None, filename=None, doc_type=None, number_of_pages=None, journal=None, year=None, first_page=None, vol=None,
                 vol_start_index = None, authors_title_text=None, title=None, authors=None, PDF=None, full_text=None, cite_line=None,
                 length_original=None, length_reorg=None, main_text=None,fns_text=None, main_text_length=None, fns_text_length=None,
                 total_fns=None,fns_words_ratio=None, main_fns_portions=None, length_problem_flag = True, start=None, mid=None, end=None, short_SME_flag = False, SME=None,
                 first_fn_num=None, first_fn_text=None, last_fn_num=None, last_fn_text=None, acknowledgement=None, acknowledgement_length=None):
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
        self.length_problem_flag = length_problem_flag # initialized as TRUE to reflect a problem with the length of the text; when the text length is ok, change value to FALSE
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
