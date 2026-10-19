"""Faithfully extract the user-supplied study guide; document prose is data."""
from pathlib import Path
import json, pdfplumber
root=Path(__file__).resolve().parents[1]
source=Path('/Users/mustapha/Downloads/AWS Certified Solutions Architect Study Guide with 900 -- Ben Piper, David Clinton -- Sybex Study Guide, 4, 2022 -- Wiley & Sons, Incorporated, John -- isbn13 9781119982623 -- a5de08a7019e6956aa67fcff2d5ca701 -- Anna’s Archive.pdf')
pages=[]
with pdfplumber.open(source) as pdf:
 for i,page in enumerate(pdf.pages,1):
  pages.append({'page':i,'text':(page.extract_text(x_tolerance=2,y_tolerance=3) or '').strip()})
  if i%100==0:print(f'Extracted {i}/{len(pdf.pages)} pages',flush=True)
out=root/'output/text/AWS SAA-C03 Study Guide - Ben Piper and David Clinton.txt'
out.write_text('\n\n'.join(f'--- PDF page {p["page"]} ---\n\n{p["text"] if p["text"] else "[No extractable text on this page; image or blank page.]"}' for p in pages)+'\n',encoding='utf-8')
(root/'tmp/pdfs/sybex-pages.json').write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
print('Output:',out)
print('Pages:',len(pages),'Empty/image-only:',[p['page'] for p in pages if not p['text']])
print('Words:',sum(len(p['text'].split()) for p in pages))
