"""Attach verifiable chapter/PDF-page references to original quick-study cards."""
import json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from app.book_import import REF_PATHS
from app.seed import DOCS
chapters=[
(1,'Introduction to Cloud Computing and AWS',3,24),(2,'Compute Services',25,66),(3,'AWS Storage',67,88),(4,'Amazon Virtual Private Cloud (VPC)',89,142),(5,'Database Services',143,174),(6,'Authentication and Authorization — IAM',175,190),(7,'CloudTrail, CloudWatch, and AWS Config',191,222),(8,'DNS, Route 53 and CloudFront',223,242),(9,'Data Ingestion, Transformation, and Analytics',243,254),(10,'Resilient Architectures',257,286),(11,'High-Performing Architectures',287,322),(12,'Secure Architectures',323,356),(13,'Cost-Optimized Architectures',357,374)]
metadata={n:{'id':n,'title':title,'pdf_start':start+42,'pdf_end':end+42,'printed_start':start,'printed_end':end} for n,title,start,end in chapters}
pages=json.loads((root/'tmp/pdfs/sybex-pages.json').read_text())
norm=lambda s:re.sub(r'[^a-z0-9]','',s.lower())
cards=[];fallbacks=[]
for i,line in enumerate((root/'backend/app/flashcard_content.txt').read_text().splitlines(),1):
 task,ch,service,front,back,keyword=line.split('|');chapter=metadata[int(ch)]
 pool=[p for p in pages if chapter['pdf_start']<=p['page']<=chapter['pdf_end']]
 matches=[p for p in pool if norm(keyword) in norm(p['text'])]
 if matches:
  source_page=matches[0]['page'];source_kind='Topic located in the supplied chapter; answer paraphrased and clarified with AWS documentation.'
 else:
  source_page=chapter['pdf_start'];source_kind='Chapter topic cross-reference; answer includes a supplemental AWS architectural concept.';fallbacks.append((i,keyword,ch))
 ref=REF_PATHS.get(service) or {'TransferFamily':'transfer/latest/userguide/what-is-aws-transfer-family.html'}.get(service) or DOCS[service]
 if service=='IAM':ref='IAM/latest/UserGuide/access_policies_identity-vs-resource.html'
 if task=='2.2' and ('RPO' in front or 'RTO' in front):ref='whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html'
 cards.append({'id':f'FC{i:03d}','domain':int(task[0]),'task':task,'chapter':int(ch),'front':front,'back':back,'services':[{'LakeFormation':'Lake Formation','TransferFamily':'Transfer Family','AutoScaling':'EC2 Auto Scaling','Route53':'Route 53','CostExplorer':'Cost Explorer','PricingCalculator':'Pricing Calculator','TrustedAdvisor':'Trusted Advisor','SavingsPlans':'Savings Plans','DirectConnect':'Direct Connect'}.get(service,service)],'source_page':source_page,'source_printed_page':source_page-42,'source_note':source_kind,'references':[{'title':'AWS documentation','url':'https://docs.aws.amazon.com/'+ref}]})
assert len(cards)==100 and len({c['front'] for c in cards})==100
for c in cards:
 assert 1<=c['source_page']<=477
 assert len(c['back'])<600
(root/'backend/app/study_cards.json').write_text(json.dumps({'source':{'title':'AWS Certified Solutions Architect Study Guide, Fourth Edition','authors':['Ben Piper','David Clinton'],'edition':4,'year':2022,'pdf_pages':477,'note':'100 original paraphrased flashcards based on chapter topics, with current AWS clarifications. These are not the publisher online flashcard set.'},'chapters':list(metadata.values()),'cards':cards},indent=2,ensure_ascii=False)+'\n')
print('Prepared 100 flashcards. Supplemental topic references:',fallbacks)
# Cover is image-only. Transcription is explicit and keeps the rest faithful.
text_path=root/'output/text/AWS SAA-C03 Study Guide - Ben Piper and David Clinton.txt'
s=text_path.read_text()
cover='''Fourth Edition
AWS Certified Solutions Architect
STUDY GUIDE
ASSOCIATE (SAA-C03) EXAM

Includes one year of FREE access after activation to the interactive online learning environment and study tools:
900 practice questions
100 electronic flashcards
Searchable key term glossary

BEN PIPER
DAVID CLINTON
SYBEX - A Wiley Brand'''
s=s.replace('--- PDF page 1 ---\n\n[No extractable text on this page; image or blank page.]','--- PDF page 1 ---\n\n[Cover text transcribed from the image.]\n'+cover,1)
header='[Text extraction of the supplied PDF. PDF page markers preserve source-page locations. Diagrams and visual layout are not reproduced. Publisher online resources advertised on the cover are not included in this PDF extraction.]\n\n'
if not s.startswith('[Text extraction'):s=header+s
text_path.write_text(s,encoding='utf-8')
assert len(re.findall(r'^--- PDF page \d+ ---$',s,re.M))==477
print('Verified text:',text_path)
