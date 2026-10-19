"""Pair only the supplied PDF's assessment/review items with its own answer keys."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
pages=json.loads((root/'tmp/pdfs/sybex-pages.json').read_text())
chapter_names={c['id']:c['title'] for c in json.loads((root/'backend/app/study_cards.json').read_text())['chapters']}
# Verified review-section boundaries, including reviews spilling onto a following chapter's nominal starting page.
ranges={1:(64,66),2:(102,108),3:(128,132),4:(180,184),5:(212,216),6:(231,234),7:(260,264),8:(281,284),9:(292,296),10:(324,330),11:(360,364),12:(393,398),13:(412,416)}

def clean_page(p):
 lines=p['text'].splitlines()
 if lines and (re.match(r'^\d+\s+(Chapter\s+\d+|Appendix\s+A)',lines[0]) or re.match(r'^Review Questions\s+\d+$',lines[0]) or re.match(r'^Chapter\s+\d+:.*\s+\d+$',lines[0]) or re.match(r'^(?:[ivxlcdm]+\s+)?(?:Answers to )?Assessment Test(?:\s+[ivxlcdm]+)?$',lines[0])):
  lines=lines[1:]
 return '\n'.join(lines)
def page_range(a,b):return '\n'.join(clean_page(p) for p in pages[a-1:b])
def tidy(s):return re.sub(r'\s+',' ',s).strip()

def parse_questions(text):
 candidates=list(re.finditer(r'(?m)^\s*(\d+)\.\s+',text))
 matches=[];expected=1
 for candidate in candidates:
  if int(candidate.group(1))==expected:
   matches.append(candidate);expected+=1
 result={}
 for i,m in enumerate(matches):
  n=int(m.group(1));body=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)].strip()
  options=list(re.finditer(r'(?m)^\s*([A-H])\.\s+',body))
  assert len(options)>=2,(n,body[:200])
  stem=tidy(body[:options[0].start()])
  choices=[{'label':o.group(1),'text':tidy(body[o.end():options[j+1].start() if j+1<len(options) else len(body)])} for j,o in enumerate(options)]
  assert n not in result and stem and all(o['text'] for o in choices)
  assert [o['label'] for o in choices]==list('ABCDEFGH'[:len(choices)]),(n,choices)
  result[n]={'number':n,'question':stem,'choices':choices}
 assert sorted(result)==list(range(1,len(result)+1)),sorted(result)
 return result

def parse_answers(text):
 matches=list(re.finditer(r'(?m)^\s*(\d+)\.\s+([A-H](?:\s*,\s*[A-H])*)\.\s+',text))
 result={}
 for i,m in enumerate(matches):
  n=int(m.group(1));result[n]={'key':re.findall(r'[A-H]',m.group(2)),'explanation':tidy(text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)])}
 assert len(result)==len(matches), 'Duplicate answer numbers'
 return result

assessment_q=parse_questions(page_range(33,38))
assessment_a=parse_answers(page_range(39,41))
answer_text=page_range(418,445)
headings=list(re.finditer(r'(?m)^Chapter\s+(\d+)\s*:',answer_text))
assert [int(h.group(1)) for h in headings]==list(range(1,14)),[(h.group(1),answer_text[h.start():h.start()+70]) for h in headings]
answer_sections={int(h.group(1)):parse_answers(answer_text[h.end():headings[i+1].start() if i+1<len(headings) else len(answer_text)]) for i,h in enumerate(headings)}
sections=[('ASSESSMENT TEST',None,assessment_q,assessment_a)]
for chapter,(start,end) in ranges.items():sections.append((f'CHAPTER {chapter}: {chapter_names[chapter]}',chapter,parse_questions(page_range(start,end)),answer_sections[chapter]))
lines=[];records=[]
for title,chapter,questions,answers in sections:
 assert set(questions)==set(answers),(title,'Question/answer number mismatch',set(questions)^set(answers))
 lines.extend([title,''])
 for n,q in questions.items():
  key=answers[n]['key']
  assert set(key)<=set(o['label'] for o in q['choices']),(title,n,key)
  lines.append(f'{n}. {q["question"]}')
  lines.extend(f'{o["label"]}. {o["text"]}' for o in q['choices'])
  lines.extend(['Answer: '+', '.join(key),''])
  records.append({'section':title,'chapter':chapter,**q,'answer':key,'book_explanation':answers[n]['explanation']})
 print(title,':',len(questions),'questions and matched keys')
out=root/'output/text/AWS SAA-C03 Study Guide - Questions Choices and Answers Only.txt'
out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
(root/'tmp/pdfs/sybex-questions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Output:',out)
print('Total:',len(records),'Questions;',sum(len(q['choices']) for q in records),'Choices;',len(records),'Answer keys')
