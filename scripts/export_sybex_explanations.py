"""Export the exact explanations shown in the bank, with original wording and keys."""
import sys,json
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'backend'))
from app.sybex_import import build_sybex_import
bank=build_sybex_import();counts=Counter(q['provenance']['review_status'] for q in bank)
lines=['AWS SAA-C03 — Sybex Study Guide Questions with Explanations','Source: Ben Piper and David Clinton, 4th edition; user-provided PDF.','Editorial source-based review: 14 October 2026. Targeted current AWS documentation checks are linked per item.',f'{len(bank)} questions; {sum(len(q["options"]) for q in bank)} option explanations.',f'{counts["Reviewed"]} retained-key reviews; {counts["Corrected"]} corrected/clarified; {counts["Review only"]} study-only.',f'{sum(q["eligible"] for q in bank)} eligible for scored practice. Exact duplicates retained for reading but excluded from scored selection.','Original text and keys remain visible. For flawed items, notes explain valid uses instead of inventing a uniquely correct answer.','']
for q in bank:
 p=q['provenance'];lines += ['='*78,p['source_section'],f'Question {p["source_question_number"]} | Bank ID: {q["id"]} | Task: {q["task"]}',p['original_scenario']]
 lines += [o['id'].upper()+'. '+o['text'] for o in p['original_options']]
 lines += ['',f'Book answer: {p["source_key"].upper()}',f'Practice answer: {", ".join(v.upper() for v in q["correct"]) or "No unique defensible key assigned"}',f'Review: {p["review_status"]} | Scored practice: {"Yes" if q["eligible"] else "No"}','Rationale: '+q['explanation'],'','Option-by-option reasons:']
 lines += [o['id'].upper()+': '+o['explanation'] for o in q['options']]
 if p['changes']:
  lines += ['','Practice wording:',q['scenario']]+[o['id'].upper()+'. '+o['text'] for o in q['options']]
 lines += ['','References:']+[r['title']+' — '+r['url'] for r in q['references']]+['']
out=root/'output/text/AWS SAA-C03 Study Guide - Questions Answers and Explanations.txt';out.write_text('\n'.join(lines)+'\n')
(root/'docs/SYBEX_IMPORT_REVIEW.json').write_text(json.dumps({'total':len(bank),'option_explanations':1279,'counts':dict(counts),'eligible':sum(q['eligible'] for q in bank),'items':[{'id':q['id'],'status':q['provenance']['review_status'],'eligible':q['eligible'],'duplicate_of':q['duplicate_of'],'changes':q['provenance']['changes'],'reason':q['explanation']} for q in bank if q['provenance']['review_status']!='Reviewed' or q['duplicate_of']]},indent=2,ensure_ascii=False)+'\n')
print(out);print(counts);print('Eligible:',sum(q['eligible'] for q in bank))
