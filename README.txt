--------------------------------------README-------------------------------------------Introduction
This is a financial statements download program used for EDGARProcedure
1: Create a new directory in any place you want
2: Keep the Python file (edgar_download.py) and one index file in this directory(You can download index file from ftp://ftp.sec.gov/edgar/full-index/)
3: Open the terminal and use the command (cd your_directory_path) to navigate to the directory that you just created
4: Input command like:

   Download everything: $ python edgar_download.py --target 10-K 10-Q 8-K Others   Download 10-K and Others :$ python edgar_download.py --target 10-K Others   Download 8-K including press release:$ python edgar_download.py --target 8-K   ... ...