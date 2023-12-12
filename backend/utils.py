import tempfile
import docx2txt

def convert_docx_to_txt(file):
    """Convert a docx file to a txt file."""
    # create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
        # convert the docx file to a txt file
        tmp.write(docx2txt.process(file))
        # read the txt file
        tmp.seek(0)
        txt = tmp.read()
    # return the txt file
    return txt
