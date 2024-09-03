import sys
import time
import argparse
import datetime
from pathlib import Path


import pymupdf
from gtts import gTTS, gTTSError
from multi_column import column_boxes
from samba import samba_process_data
from pydub import AudioSegment 


# This function can be re-written to use whatever api, the higher the quality llm the better 
def clean_data(text):
    system = """
    Your are not a chatbot.
    You are a tool that cleans up text extracted from PDFs. 
    Remove any words or symbols that are out of place such as words not part of a complete sentence,
    however, keep words occuring at page boundaries, keep words that are part of headers that make sense, and remove headers that resemble page headers.
    Remove any text that seems to be tabulated data.
    Remove any new lines that are not part of paragraph or header breaks.
    Replace words broken by hyphens with their full word equivalents.
    Do not add any words or punctuation.
    Do not delete entire paragraphs.
    Do not reword any of the content and do not remove content, aside from the modifications listed, text should be unchanged.
    Do not under any circumstances insert any commentary about what is being done, only include the result in your response. 
    What follows is one page of the PDF to process:
    """
    model = "llama3-405b"
    return samba_process_data(model, system, text)

def extract_text(fname, start, end):
    doc = pymupdf.open(fname)
    text = ""
    for i,page in enumerate(doc[start:end]):
        print("Processing page " + str(i) +" of " + str(end-start))
        page_text = ""
        bboxes = column_boxes(page, footer_margin=50, no_image_text=True)
        for rect in bboxes:
            page_text += page.get_text(clip=rect, sort=True) + "\n"
        cleaned = clean_data(page_text)
        text += cleaned + "\n\n"
    return text

# This function can be re-written to use whatever api 
# fname is the file to write mp3 to
# text should be delivered in resonable sized chunks that the api chosen can handle
def tts_api_request(fname, text):
    for attempt in range(5):
        try:
            tts = gTTS(text, lang='en', slow=False)
            tts.save(fname)
            return
        except gTTSError as e:
            if "429 (Too Many Requests)" in str(e):
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
        except Exception as e:
            raise  # Re-raise any other exceptions

def chunk_and_reconstruct(text, prefix, chunk_size=100):
    audio_chunk_dir = "outputs/"+datetime.datetime.now().strftime(prefix+"_mp3_chunking_%I_%M%p_%B%d_%Y")
    Path(audio_chunk_dir).mkdir(parents=True, exist_ok=True)
    print("saving chunk mp3s to " + audio_chunk_dir + "/ ...")
    fragments = text.split(" ")
    mp3_fragments = []
    for i in range(0, len(fragments), chunk_size):
        chunk_text = " ".join(fragments[i:i+chunk_size])
        fname = audio_chunk_dir + "/" + "mp3_index_"+str(i)+".mp3"
        print("Processing file " + fname + " ... (" + str(i) +","+str(len(fragments))+")")
        tts_api_request(fname, chunk_text)
        mp3_fragments.append(fname)

    print("Combining audio segments...")
    combined = AudioSegment.empty()
    for mp3 in mp3_fragments:
        sound = AudioSegment.from_mp3(mp3)
        combined += sound
    combined.export(audio_chunk_dir+"/"+prefix+"_FINAL_OUTPUT.mp3", format="mp3")
    print("Saved to: " + str(audio_chunk_dir+"/"+prefix+"FINAL_OUTPUT.mp3"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_file")
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("--prefix", default="out", required=False)
    args = parser.parse_args()
    
    text_dir = "outputs/"+datetime.datetime.now().strftime(args.prefix+"_extract_text_%I_%M%p_%B%d_%Y")
    Path(text_dir).mkdir(parents=True, exist_ok=True)
    text = extract_text(args.pdf_file, args.start, args.end)
    with open(text_dir+"/"+args.prefix+"_output.txt", "w") as f:
        f.write(text)
    chunk_and_reconstruct(text, args.prefix)

if __name__ == "__main__":
    main()   



        
