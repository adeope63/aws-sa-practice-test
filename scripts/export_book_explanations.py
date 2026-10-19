"""Export the reviewed import for reading and audit; do not modify the extraction."""
import json,sys
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from app.book_import import build_import,OPTION_REPAIRS
from app.book_facts import option_fact
bank=build_import();summary=Counter(q['provenance']['review_status'] for q in bank)
lines=['AWS SAA-C03 - Supplied Book Questions with Reviewed Explanations',
       'Source: James Howlett; PDF supplied by the user. Editorial review: 14 October 2026.',
       'The original question and key are preserved. Practice corrections are explicitly shown.',
       'Review-only items have no defensible unique scored answer as written, or are outside current practice scope.',
       'For those items, option notes explain applicability instead of falsely labeling all alternatives wrong.',
       f'400 imported items: {summary["Reviewed"]} reviewed, {summary["Corrected"]} corrected, {summary["Review only"]} review-only.',
       f'Scored-eligible imported items: {sum(q["eligible"] for q in bank)}. Related concept families remain identifiable.', '']
report=[]
for q in bank:
 p=q['provenance'];n=p['source_number'];source_key=p['source_key'];key=q['correct'][0] if q['correct'] else None
 lines.extend(['='*78,f'{n}. {p["original_scenario"]}',f'Bank ID: {q["id"]} | Official task: {q["task"]} | Review: {p["review_status"]}',f'Included in scored practice: {"Yes" if q["eligible"] else "No"}', ''])
 for original in p['original_options']:
  lines.append(f'{original["id"].upper()}. {original["text"].rstrip(" -")}')
 lines.extend(['',f'Book answer: {source_key.upper()}',f'Reviewed answer: {key.upper() if key else "No unique defensible answer as written"}',f'Review rationale: {q["explanation"]}', '', 'Reasons for each original option:'])
 for original in p['original_options']:
  letter=original['id']; current=next(o for o in q['options'] if o['id']==letter)
  if letter in OPTION_REPAIRS.get(n,{}):
   why='Source wording corrected. '+option_fact(original['text'].rstrip(' -'))+' Reviewed replacement: '+current['text']+'. '+q['explanation']
  elif key:
   why=current['explanation']
  else:
   why=current['explanation']
  lines.append(f'{letter.upper()}: {why}')
 if p['changes']:
  lines.extend(['','Practice version:',q['scenario']])
  for o in q['options']:lines.append(f'{o["id"].upper()}. {o["text"]}')
  lines.extend('Change: '+change for change in p['changes'])
 lines.extend(['','AWS references:']+[r['title']+' - '+r['url'] for r in q['references']]+[''])
 if p['review_status']!='Reviewed':report.append({'id':q['id'],'number':n,'status':p['review_status'],'book_key':source_key,'reviewed_key':key,'eligible':q['eligible'],'reason':q['explanation'],'changes':p['changes']})
out=root/'output/text/AWS SAA-C03 - Questions Answers and Explanations.txt'
out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
(root/'docs/BOOK_IMPORT_REVIEW.json').write_text(json.dumps({'counts':dict(summary),'eligible':sum(q['eligible'] for q in bank),'items':report},indent=2,ensure_ascii=False)+'\n')
print(out)
print(summary)
print('Question explanations:',len(bank),'Option explanations:',sum(len(q['options']) for q in bank))
