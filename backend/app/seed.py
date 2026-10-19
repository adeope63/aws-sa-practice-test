"""Original related case questions; no copied exam items or generated filler."""
import hashlib
from pathlib import Path
from collections import Counter
from .models import Question
from .blueprint import TASKS, DOMAINS, GUIDE
DOCS = {
'RDS Multi-AZ DB instance':'AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html',
'RDS Read Replicas':'AmazonRDS/latest/UserGuide/USER_ReadRepl.html',
'Reserved Instances':'AWSEC2/latest/UserGuide/ec2-reserved-instances.html',
'Spot Instances':'AWSEC2/latest/UserGuide/using-spot-instances.html',
'Cognito':'cognito/latest/developerguide/what-is-amazon-cognito.html',
'IAM':'IAM/latest/UserGuide/access_policies.html','STS':'IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html','Organizations':'organizations/latest/userguide/orgs_manage_policies_scps.html','IAM Identity Center':'singlesignon/latest/userguide/what-is.html','S3':'AmazonS3/latest/userguide/Welcome.html','EC2':'AWSEC2/latest/UserGuide/concepts.html','Secrets Manager':'secretsmanager/latest/userguide/rotating-secrets.html','VPC':'vpc/latest/userguide/what-is-amazon-vpc.html','PrivateLink':'vpc/latest/privatelink/what-is-privatelink.html','WAF':'waf/latest/developerguide/waf-chapter.html','GuardDuty':'guardduty/latest/ug/what-is-guardduty.html','Systems Manager':'systems-manager/latest/userguide/session-manager.html','ACM':'acm/latest/userguide/acm-overview.html','Site-to-Site VPN':'vpn/latest/s2svpn/VPC_VPN.html','Firewall Manager':'waf/latest/developerguide/fms-chapter.html','CloudTrail':'awscloudtrail/latest/userguide/cloudtrail-user-guide.html','CloudFront':'AmazonCloudFront/latest/DeveloperGuide/Introduction.html','Macie':'macie/latest/user/what-is-macie.html','EBS':'ebs/latest/userguide/what-is-ebs.html','KMS':'kms/latest/developerguide/overview.html','Backup':'aws-backup/latest/devguide/whatisbackup.html','SQS':'AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html','SNS':'sns/latest/dg/welcome.html','Step Functions':'step-functions/latest/dg/welcome.html','DynamoDB':'amazondynamodb/latest/developerguide/Introduction.html','EventBridge':'eventbridge/latest/userguide/eb-what-is.html','ECS':'AmazonECS/latest/developerguide/Welcome.html','Amazon MQ':'amazon-mq/latest/developer-guide/welcome.html','API Gateway':'apigateway/latest/developerguide/welcome.html','RDS':'AmazonRDS/latest/UserGuide/Welcome.html','ALB':'elasticloadbalancing/latest/application/introduction.html','Route 53':'Route53/latest/DeveloperGuide/Welcome.html','EFS':'efs/latest/ug/whatisefs.html','RDS Proxy':'AmazonRDS/latest/UserGuide/rds-proxy.html','X-Ray':'xray/latest/devguide/aws-xray.html','CloudFormation':'AWSCloudFormation/latest/UserGuide/Welcome.html','FSx':'fsx/latest/WindowsGuide/what-is.html','Storage Gateway':'filegateway/latest/files3/WhatIsFileGateway.html','Lambda':'lambda/latest/dg/welcome.html','Batch':'batch/latest/userguide/what-is-batch.html','EC2 Auto Scaling':'autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html','ElastiCache':'AmazonElastiCache/latest/dg/WhatIs.html','Neptune':'neptune/latest/userguide/intro.html','Redshift':'redshift/latest/mgmt/welcome.html','Global Accelerator':'global-accelerator/latest/dg/what-is-global-accelerator.html','Gateway Load Balancer':'elasticloadbalancing/latest/gateway/introduction.html','Transit Gateway':'vpc/latest/tgw/what-is-transit-gateway.html','Data Firehose':'firehose/latest/dev/what-is-this-service.html','Kinesis':'streams/latest/dev/introduction.html','Glue':'glue/latest/dg/what-is-glue.html','DataSync':'datasync/latest/userguide/what-is-datasync.html','Savings Plans':'savingsplans/latest/userguide/what-is-savings-plans.html','Compute Optimizer':'compute-optimizer/latest/ug/what-is-compute-optimizer.html','Athena':'athena/latest/ug/what-is.html'}

def build_bank():
    bank=[]; seq=Counter()
    for line in Path(__file__).with_name('cases.txt').read_text().splitlines():
        task,title,scenario,solution,why,control,controlwhy,b1,b2,b3,services=line.split('|')
        domain=int(task[0]); seq[domain]+=1
        family=f'{["","S","R","P","C"][domain]}{seq[domain]:02d}'
        bad=[x.split('~') for x in [b1,b2,b3]]
        opts=[{'id':'a','text':solution,'explanation':why}]+[{'id':chr(98+i),'text':text,'explanation':reason} for i,(text,reason) in enumerate(bad)]
        refs=[{'title':f'Official {services.split(",")[0]} documentation','url':'https://docs.aws.amazon.com/'+DOCS[services.split(',')[0]]},{'title':f'Official domain {domain} requirements','url':GUIDE+f'solutions-architect-associate-03-domain{domain}.html'}]
        specific={'S05':'IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html','S21':'AmazonS3/latest/userguide/object-lock.html','S23':'AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html','S27':'vpc/latest/privatelink/gateway-endpoints.html','R13':'AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html','R14':'AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html','P04':'fsx/latest/LustreGuide/what-is.html','C01':'AmazonS3/latest/userguide/storage-class-intro.html','C02':'AmazonS3/latest/userguide/storage-class-intro.html','C03':'AmazonS3/latest/userguide/storage-class-intro.html','C16':'vpc/latest/privatelink/gateway-endpoints.html'}
        if family in specific: refs[0]['url']='https://docs.aws.amazon.com/'+specific[family]
        if family in ['R16','R17','R18']: refs.append({'title':'Official disaster recovery strategies','url':'https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html'})
        explanation=f'{why} The design must satisfy the stated workload constraints together. {controlwhy} Review this trade-off: {bad[0][1]} The selected design addresses the requirement without relying on that alternative.'
        stems=[
            (f'{scenario} Which solution BEST meets these requirements?',opts,['a'],'Architecture decision'),
            (f'{scenario} A proposed design would: {bad[0][0][0].lower()+bad[0][0][1:]}. The review identifies this problem: {bad[0][1]} Which replacement BEST addresses the problem while preserving the requirements?',opts,['a'],'Design review'),
            (f'{scenario} Select TWO complementary actions for the implementation and its operational or security control.',opts+[{'id':'e','text':control,'explanation':controlwhy}],['a','e'],'Implementation controls'),
            (f'{scenario} The team has selected this solution: {solution}. Which accompanying design consideration is MOST appropriate?', [{'id':'a','text':control,'explanation':controlwhy}]+[{'id':chr(98+i),'text':t,'explanation':r} for i,(t,r) in enumerate(bad)],['a'],'Operational trade-offs'),
        ]
        for index,(stem,options,key,kind) in enumerate(stems,1):
            bank.append(dict(id=f'{family}-{index}',family=family,domain=domain,task=task,title=f'{title} · {kind}',scenario=stem,services=services.split(','),concepts=[title,kind],options=options,correct=key,explanation=explanation,difficulty='Advanced' if index==3 else 'Intermediate',references=refs,verification='Technical review pending'))
    validate(bank)
    return bank

def validate(bank):
    assert len(bank)==400, f'Expected 400 items; got {len(bank)}'
    assert len({q['id'] for q in bank})==400
    assert len({hashlib.sha256(q['scenario'].encode()).hexdigest() for q in bank})==400
    assert Counter(q['domain'] for q in bank)=={1:120,2:104,3:96,4:80}
    assert set(q['task'] for q in bank)==set(TASKS)
    for q in bank:
        assert q['task'][0]==str(q['domain'])
        assert len(q['options'])==(5 if len(q['correct'])>1 else 4)
        assert set(q['correct'])<=set(o['id'] for o in q['options'])
        assert len({o['text'] for o in q['options']})==len(q['options'])
        assert all(o['explanation'] for o in q['options'])
        assert all(r['url'].startswith('https://docs.aws.amazon.com/') for r in q['references'])

def seed(db):
    from .book_import import build_import
    from .sybex_import import build_sybex_import
    for data in build_bank()+build_import()+build_sybex_import():
        existing=db.get(Question,data['id'])
        if existing:
            for key,value in data.items(): setattr(existing,key,value)
        else: db.add(Question(**data))
    db.commit()
if __name__=='__main__':
    bank=build_bank(); print(f'{len(bank)} structurally validated questions / {len(set(q["family"] for q in bank))} related architecture cases; technical review pending')
