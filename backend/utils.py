import tempfile
import docx2txt

def convert_docx_to_txt(file):
    """Convert a docx file to a txt file."""
    return docx2txt.process(file)
