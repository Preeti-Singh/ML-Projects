# install pyttsx3
# install PyPDF2
import pyttsx3
import PyPDF2
pdf_book=open('python.pdf','rb')
reading_book=PyPDF2.PdfFileReader(pdf_book)
page_number=reading_book.numPages

pdf_speaker=pyttsx3.init()
choose_page=reading_book.getPage(0)
pdf_text=choose_page.extractText()
pdf_speaker.say(pdf_text)
pdf_speaker.runAndWait()

