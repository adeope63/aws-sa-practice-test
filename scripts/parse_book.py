"""Parse the user-supplied extraction without changing its answer keys."""
import json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'output/text/AWS SAA-C03 - Questions Choices and Answers Only.txt'
s=source.read_text(); records=[]
for chunk in s.strip().split('\n\n'):
 lines=chunk.splitlines()
 n,stem=lines[0].split('. ',1)
 opts=[{'id':line[0].lower(),'text':line[3:]} for line in lines[1:5]]
 records.append({'number':int(n),'source_domain':(int(n)-1)//100+1,'scenario':stem,'options':opts,'source_key':lines[5].split(': ')[1].lower()})
assert len(records)==400
(root/'backend/app/book_source.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 import sys
 start=int(sys.argv[1]) if len(sys.argv)>1 else 1
 end=int(sys.argv[2]) if len(sys.argv)>2 else 400
 for q in records[start-1:end]:
  print(f"{q['number']} [{q['source_key'].upper()}] {q['scenario']} | "+' / '.join(o['id'].upper()+':'+o['text'] for o in q['options']))
