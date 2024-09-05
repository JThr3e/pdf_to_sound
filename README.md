This tool takes in a pdf file and page range and will try to create an mp3 version that can be listened to.
The tool will attempt to clean up the pdf file by removing labels and making sure columns don't get jumbled.

setup:
```
pip3 install -r requirments.txt
```

usage:

```
python pdf_to_text.py /path/to/file.pdf start_page stop_page --prefix <file/folder prefix>
```
