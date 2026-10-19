"""Source-linked Sybex question import with option explanations and explicit repairs."""
import hashlib,json,re
from pathlib import Path
from collections import Counter
from .blueprint import TASKS
from .seed import DOCS
from .sybex_review import REVIEW
ROOT=Path(__file__).parent
BASE_TASK={0:'2.1',1:'2.1',2:'3.2',3:'3.1',4:'3.4',5:'3.3',6:'1.1',7:'2.2',8:'3.4',9:'3.5',10:'2.2',11:'3.2',12:'1.2',13:'4.2'}
BASE_SERVICES={0:['AWS'],1:['AWS'],2:['EC2'],3:['S3'],4:['VPC'],5:['RDS','DynamoDB'],6:['IAM'],7:['CloudWatch','CloudTrail','AWS Config'],8:['Route 53','CloudFront'],9:['Glue','Kinesis'],10:['EC2 Auto Scaling'],11:['EC2'],12:['IAM','KMS'],13:['EC2']}
EXTRA_DOCS={'AWS Config':'config/latest/developerguide/WhatIsConfig.html','CloudHSM':'cloudhsm/latest/userguide/introduction.html','Budgets':'cost-management/latest/userguide/budgets-managing-costs.html','Cost Explorer':'cost-management/latest/userguide/ce-what-is.html','Trusted Advisor':'awssupport/latest/user/trusted-advisor.html','Security Hub':'securityhub/latest/userguide/what-is-securityhub.html','Inspector':'inspector/latest/user/what-is-inspector.html','Directory Service':'directoryservice/latest/admin-guide/what_is.html','Firehose':'firehose/latest/dev/what-is-this-service.html'}
SPECIAL_REFS={
'gp3':'https://docs.aws.amazon.com/ebs/latest/userguide/general-purpose.html',
'vm':'https://docs.aws.amazon.com/vm-import/latest/userguide/import-vm-image.html',
'roles':'https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2.html',
'cert':'https://docs.aws.amazon.com/acm/latest/userguide/acm-exportable-certificates.html',
'fifo':'https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/avoid-backlog-with-the-same-message-group-id.html',
'glue':'https://docs.aws.amazon.com/glue/latest/dg/add-job-streaming.html',
'origins':'https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistS3AndCustomOrigins.html',
'x509':'https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html',
'free':'https://aws.amazon.com/free/free-tier-faqs/',
'support':'https://docs.aws.amazon.com/awssupport/latest/user/support-plans-eos.html',
'nat':'https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateways-regional.html',
'pitr':'https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html',
'redshift':'https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-clusters.html',
'consistency':'https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel',
'kms':'https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html',
'cloudtrail':'https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html',
'cli':'https://docs.aws.amazon.com/cli/latest/reference/iam/get-access-key-last-used.html',
'spotcli':'https://docs.aws.amazon.com/cli/latest/reference/ec2/request-spot-fleet.html',
'presign':'https://docs.aws.amazon.com/cli/latest/reference/s3/presign.html'}
REF_ITEMS={'2.9':'gp3','2.2':'vm','2.14':'roles','12.20':'cert','10.25':'fifo','9.10':'glue','8.17':'origins','6.7':'x509','13.1':'free','1.11':'support','0.1':'support','4.14':'nat','4.15':'nat','0.15':'pitr','10.12':'pitr','5.17':'redshift','5.21':'redshift','3.10':'consistency','12.17':'kms','12.16':'kms','7.1':'cloudtrail','6.5':'cli','13.19':'spotcli','3.16':'presign'}
def source_rationale(raw):
    return re.sub(r'\s*See Chapter \d+ for more information\.?','',raw['book_explanation']).strip()
def classify(raw,stem):
    c=raw['chapter'] or 0;t=BASE_TASK[c];s=BASE_SERVICES[c]
    text=stem+' '+' '.join(o['text'] for o in raw['choices'])
    # Prefer services explicitly present in the stem; options include intentional distractors.
    found=[name for name in {**DOCS,**EXTRA_DOCS} if re.search(r'\b'+re.escape(name)+r'\b',stem,re.I)]
    if found:s=sorted(found,key=lambda name:(-len(name),name))[:4]
    low=stem.lower()
    if c in [0,1,2,3,4,5,8,10,11]:
        if any(w in low for w in ['encrypt','kms','decrypt']):t='1.3'
        elif any(w in low for w in ['iam','authenticate','access key','root user','role','permissions']):t='1.1'
        elif any(w in low for w in ['security group','nacl','ddos','sql injection','malware']):t='1.2'
        elif c in [0,1] and any(w in low for w in ['dynamodb','database','rds','elasticache']):t='3.3'
        elif c in [0,1] and any(w in low for w in ['vpc','subnet','route 53','cloudfront','domain']):t='3.4'
        elif c in [0,1] and any(w in low for w in ['ec2','ami','container','lambda']):t='3.2'
        elif c in [0,1] and any(w in low for w in ['s3','storage','snapshot']):t='3.1'
        elif 'sqs' in low or 'queue' in low or 'microservice' in low:t='2.1'
    if c==13:
        if any(w in low for w in ['storage class','snapshot','ebs','cost allocation']):t='4.1'
        elif 'rds' in low or 'database' in low:t='4.3'
        elif 'organization' in low:t='1.1'
    if c==12 and any(w in low for w in ['kms','encrypt','efs','ebs','s3 objects']):t='1.3'
    if c==11 and any(w in low for w in ['cache','database','rds','redis','replica']):t='3.3'
    return t,s

def fingerprint(stem,choices):
    norm=lambda s:re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
    return hashlib.sha256((norm(stem)+'|'+'|'.join(sorted(norm(o['text']) for o in choices))).encode()).hexdigest()
def build_sybex_import():
    source=json.loads((ROOT/'sybex_source.json').read_text())
    notes={}
    for line in (ROOT/'sybex_option_notes.txt').read_text().splitlines():
        if line.strip():
            k,*values=line.split('|');assert k not in notes;notes[k]=values
    seen={};bank=[]
    for seq,raw in enumerate(source,1):
        chapter=raw['chapter'] or 0;number=raw['number'];item=f'{chapter}.{number}';qid=f'Y{chapter:02d}-{number:03d}'
        review=REVIEW.get(item,{});status=review.get('status','Reviewed')
        stem=review.get('stem') or raw['question'];key=review.get('key',[v.lower() for v in raw['answer']]);eligible=status!='Review only'
        rationale=review.get('reason',source_rationale(raw));changes=[]
        if stem!=raw['question']:changes.append('Practice stem clarified; original retained below.')
        if key!=[v.lower() for v in raw['answer']]:changes.append('Practice answer key corrected from '+', '.join(raw['answer'])+' to '+', '.join(v.upper() for v in key)+'.')
        repairs=review.get('options',{})
        if repairs:changes.append('Practice option wording repaired; source options retained below.')
        tf=[o['text'] for o in raw['choices']]==['True','False']
        values=notes.get(item);assert tf or (values and len(values)==len(raw['choices'])),item
        opts=[]
        for i,o in enumerate(raw['choices']):
            letter=o['label'].lower();note=values[i].strip() if values else '_'
            if note=='_':note=rationale
            if not eligible:
                if values and values[i].strip()=='_':note=rationale
                why='Study note. '+note
            elif letter in key:
                why='Correct. '+note
                if note!=rationale:why+=' '+rationale
            else:why='Incorrect for this question. '+note
            opts.append({'id':letter,'text':repairs.get(letter,o['text']),'explanation':why})
        fp=fingerprint(stem,opts);duplicate=seen.get(fp)
        if duplicate:eligible=False;changes.append('Exact duplicate of '+duplicate+'; retained for study, excluded from scored selection.')
        else:seen[fp]=qid
        task,services=classify(raw,stem)
        refs=[{'title':'AWS documentation: '+s,'url':'https://docs.aws.amazon.com/'+(DOCS|EXTRA_DOCS)[s]} for s in services if s in (DOCS|EXTRA_DOCS)]
        if not refs:refs=[{'title':'Official SAA-C03 exam guide','url':'https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html'}]
        if item in REF_ITEMS:refs.insert(0,{'title':'AWS reference for this review','url':SPECIAL_REFS[REF_ITEMS[item]]})
        provenance={'collection':'Sybex study guide (user-provided)','source_title':'AWS Certified Solutions Architect Study Guide, 4th Edition','author':'Ben Piper and David Clinton','source_number':seq,'source_section':raw['section'],'source_chapter':chapter,'source_question_number':number,'original_scenario':raw['question'],'original_options':[{'id':o['label'].lower(),'text':o['text']} for o in raw['choices']],'source_key':', '.join(v.lower() for v in raw['answer']),'source_explanation':raw['book_explanation'],'review_status':status,'reviewed_on':'2026-10-14','changes':changes,'scope_note':'Editorial source-based explanations with targeted AWS documentation checks; not an AWS endorsement.'}
        bank.append(dict(id=qid,family='sybex-'+fp[:16],domain=int(task[0]),task=task,title=f'Sybex {"Assessment" if chapter==0 else "Chapter "+str(chapter)} #{number}',scenario=stem,services=services,concepts=[raw['section']],options=opts,correct=key if status!='Review only' else [],explanation=rationale+(' '+' '.join(changes) if changes else ''),difficulty='Foundational',references=refs,verification='Editorial source review' if status=='Reviewed' else status,eligible=eligible,duplicate_of=duplicate,provenance=provenance))
    validate_sybex(bank);return bank

def validate_sybex(bank):
    assert len(bank)==317 and len({q['id'] for q in bank})==317
    assert sum(len(q['options']) for q in bank)==1279
    assert {q['provenance']['source_number'] for q in bank}==set(range(1,318))
    for q in bank:
        assert q['task'] in TASKS and q['domain']==int(q['task'][0])
        assert len(q['options'])>=2 and all(len(o['explanation'])>35 for o in q['options'])
        assert set(q['correct']) <= {o['id'] for o in q['options']}
        assert not q['eligible'] or q['correct']
        assert not q['duplicate_of'] or not q['eligible']
        assert q['provenance']['review_status']!='Review only' or not q['correct']
    return Counter(q['provenance']['review_status'] for q in bank)
