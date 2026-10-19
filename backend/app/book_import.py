"""Reviewed local import of the PDF supplied by the user, with full provenance."""
import hashlib, json, re
from collections import Counter
from pathlib import Path
from .book_review import REVIEW
from .book_facts import option_fact
from .book_option_notes import NOTES
from .seed import DOCS
from .blueprint import TASKS

REF_PATHS={
'VPN':DOCS['Site-to-Site VPN'],'NACL':'vpc/latest/userguide/vpc-network-acls.html','IAM':'IAM/latest/UserGuide/id_roles.html','S3Encryption':'AmazonS3/latest/userguide/default-bucket-encryption.html','Shield':'waf/latest/developerguide/shield-chapter.html','S3Policy':'AmazonS3/latest/userguide/bucket-policies.html','Endpoint':'vpc/latest/privatelink/privatelink-access-aws-services.html','KMSRotation':'kms/latest/developerguide/rotate-keys.html','CloudTrail':DOCS['CloudTrail'],'TLS':'AmazonS3/latest/userguide/security-best-practices.html','KMS':DOCS['KMS'],'MFA':'IAM/latest/UserGuide/id_credentials_mfa.html','Config':'config/latest/developerguide/evaluate-config.html','SecurityHub':'securityhub/latest/userguide/what-is-securityhub.html','SG':'vpc/latest/userguide/vpc-security-groups.html','ACM':DOCS['ACM'],'Secrets':DOCS['Secrets Manager'],'GuardDuty':DOCS['GuardDuty'],'WAF':DOCS['WAF'],'Organizations':DOCS['Organizations'],'VPC':DOCS['VPC'],'EBS':DOCS['EBS'],'Backup':DOCS['Backup'],'CloudHSM':'cloudhsm/latest/userguide/introduction.html','ParameterStore':'systems-manager/latest/userguide/systems-manager-parameter-store.html','DirectConnect':DOCS.get('Direct Connect','directconnect/latest/UserGuide/Welcome.html'),'STS':DOCS['STS'],'RDS':DOCS['RDS'],'EFS':DOCS['EFS'],'FlowLogs':'vpc/latest/userguide/flow-logs.html','Inspector':'inspector/latest/user/what-is-inspector.html','APIGateway':DOCS['API Gateway'],'CloudWatch':'AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html','ELB':'elasticloadbalancing/latest/userguide/what-is-load-balancing.html','Route53':'Route53/latest/DeveloperGuide/routing-policy.html','MultiAZ':DOCS['RDS Multi-AZ DB instance'],'DynamoDB':DOCS['DynamoDB'],'CloudFront':DOCS['CloudFront'],'AutoScaling':DOCS['EC2 Auto Scaling'],'S3Versioning':'AmazonS3/latest/userguide/Versioning.html','EC2':DOCS['EC2'],'S3Replication':'AmazonS3/latest/userguide/replication.html','DMS':'dms/latest/userguide/Welcome.html','GlobalTables':'amazondynamodb/latest/developerguide/GlobalTables.html','Spot':DOCS['Spot Instances'],'CloudFormation':DOCS['CloudFormation'],'GlobalAccelerator':DOCS['Global Accelerator'],'Redshift':DOCS['Redshift'],'ReadReplicas':DOCS['RDS Read Replicas'],'Beanstalk':'elasticbeanstalk/latest/dg/Welcome.html','ElastiCache':DOCS['ElastiCache'],'AuroraGlobal':'AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html','S3Classes':'AmazonS3/latest/userguide/storage-class-intro.html','IdentityCenter':DOCS['IAM Identity Center'],'Lambda':DOCS['Lambda'],'Aurora':'AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.html','ECS':DOCS['ECS'],'SQS':DOCS['SQS'],'EKS':'eks/latest/userguide/what-is-eks.html','LakeFormation':'lake-formation/latest/dg/what-is-lake-formation.html','S3':DOCS['S3'],'S3Acceleration':'AmazonS3/latest/userguide/transfer-acceleration.html','Kinesis':DOCS['Kinesis'],'Athena':DOCS['Athena'],'Lustre':'fsx/latest/LustreGuide/what-is.html','CloudWatchLogs':'AmazonCloudWatch/latest/logs/AnalyzingLogData.html','SageMaker':'sagemaker/latest/dg/whatis.html','Flink':'managed-flink/latest/java/what-is.html','CodeDeploy':'codedeploy/latest/userguide/welcome.html','Fargate':'AmazonECS/latest/developerguide/AWS_Fargate.html','FSxWindows':DOCS['FSx'],'Snowball':'snowball/latest/developer-guide/doc-history.html','SavingsPlans':DOCS['Savings Plans'],'CostExplorer':'cost-management/latest/userguide/ce-what-is.html','PricingCalculator':'pricing-calculator/latest/userguide/what-is-pricing-calculator.html','TrustedAdvisor':'awssupport/latest/user/trusted-advisor.html','Budgets':'cost-management/latest/userguide/budgets-managing-costs.html','DLM':'ebs/latest/userguide/snapshot-lifecycle.html','CUR':'cur/latest/userguide/what-is-cur.html','RI':DOCS['Reserved Instances'],'TagEditor':'tag-editor/latest/userguide/tagging.html','CostTags':'awsaccountbilling/latest/aboutv2/cost-alloc-tags.html'}

SERVICE_NAMES={
'VPN':'Site-to-Site VPN','NACL':'VPC','SG':'VPC','S3Encryption':'S3','S3Policy':'S3','Endpoint':'VPC Endpoints','KMSRotation':'KMS','MFA':'IAM','Config':'AWS Config','SecurityHub':'Security Hub','Secrets':'Secrets Manager','Organizations':'AWS Organizations','ParameterStore':'Systems Manager Parameter Store','DirectConnect':'Direct Connect','FlowLogs':'VPC Flow Logs','APIGateway':'API Gateway','CloudWatch':'CloudWatch','Route53':'Route 53','MultiAZ':'RDS','AutoScaling':'EC2 Auto Scaling','S3Versioning':'S3','S3Replication':'S3','GlobalTables':'DynamoDB','GlobalAccelerator':'Global Accelerator','ReadReplicas':'RDS','Beanstalk':'Elastic Beanstalk','AuroraGlobal':'Aurora','S3Classes':'S3','IdentityCenter':'IAM Identity Center','S3Acceleration':'S3','Lustre':'FSx for Lustre','CloudWatchLogs':'CloudWatch Logs','Flink':'Managed Service for Apache Flink','FSxWindows':'FSx for Windows File Server','SavingsPlans':'Savings Plans','CostExplorer':'Cost Explorer','PricingCalculator':'Pricing Calculator','TrustedAdvisor':'Trusted Advisor','DLM':'EBS Data Lifecycle Manager','CUR':'Cost and Usage Report','RI':'EC2 Reserved Instances','TagEditor':'Tag Editor','CostTags':'Cost Allocation Tags'}

# Minimal repairs preserve the original separately. No repair is silently applied.
STEMS={
20:'Which AWS service evaluates supported resource configurations against security rules and can trigger configured remediation?',
24:'Which AWS service stores application database passwords securely and supports configured managed rotation workflows?',
38:'In which AWS networking service do you configure subnet network ACLs?',
43:'Which AWS service records supported resource configurations, evaluates compliance rules, and supports configured remediation?',
55:'Which mechanism should a Lambda function use for authorized AWS API calls without embedding long-term access keys?',
57:'Which AWS service evaluates supported resource configurations against compliance rules rather than acting as a preventive permission firewall?',
78:'Which AWS service provides a dedicated private physical network connection between an on-premises data center and AWS?',
89:'How can you filter requests to an AWS WAF-supported web endpoint by the request source country?',
103:'Which RDS deployment option provides synchronous standby replication and managed failover after a database instance or Availability Zone disruption?',
115:'Which Elastic Load Balancing feature allows a load balancer node to distribute eligible traffic to targets in other Availability Zones?',
127:'Which AWS analytical data warehouse offers a Serverless deployment mode that automatically adjusts compute capacity within configured settings?',
130:'Which service can shift DNS answers to a healthy predeployed recovery endpoint using configured failover records and health checks?',
175:'Which EC2 Auto Scaling feature adjusts group capacity in response to configured demand-related metrics?',
195:'Which service adjusts EC2 instance-group capacity based on configured workload signals and can integrate with an Elastic Load Balancer?',
222:'Which AWS service provides scalable object APIs for large collections of frequently accessed unstructured data?',
231:'Which service provides managed serverless SQL queries directly over supported S3 datasets without provisioning a query cluster?',
246:'Which architecture feature underpins Aurora cluster storage redundancy and configured failover within one AWS Region?',
262:'Which managed AWS service runs Apache Flink applications to process and analyze streaming data?',
295:'Which design distributes requests across healthy EC2 targets and replaces or adjusts instance capacity in a configured redundant web tier?',
310:'Which feature can reduce unused EC2 fleet capacity when appropriate group scaling policies and minimum-capacity settings are configured?',
341:'Which architecture can maintain a redundant EC2 application tier across AZs while adjusting capacity to demand?',
348:'For a key-value/document database application with variable traffic and no requirement for relational joins, which listed option avoids a fixed reserved-instance commitment?',
349:'Which feature changes the number of EC2 instances in a configured group to match workload demand?',
357:'Which feature maintains and adjusts the number of EC2 instances in a configured group according to scaling policies?',
361:'Which feature can reduce unneeded EC2 group capacity using configured demand or scheduled scaling policies?',
366:'Which tool can apply resource tags in bulk across supported AWS resources before those tags are separately activated for cost allocation?',
368:'Which EC2 purchase model avoids a long-term commitment and Spot reclamation for unpredictable workloads that cannot tolerate Spot interruptions?',
379:'Which tool applies supported resource tags in bulk, with separate billing activation still required for cost allocation?',
384:'Which feature adjusts the EC2 group instance count to demand rather than resizing a running instance vertically?',
395:'Which EC2 purchase model suits variable demand when there is no steady commitment baseline and the workload cannot tolerate Spot interruptions?',
}
OPTION_REPAIRS={
3:{'b':'To provide assumable permissions and temporary security credentials instead of embedded long-term credentials'},
9:{'b':'AWS Shield Standard'},
128:{'b':'By routing supported traffic to healthy configured endpoints through the AWS global network'},
157:{'c':'Cross-Region replication, local secondary reads, and recovery from primary-Region disruption'},
262:{'a':'Amazon Managed Service for Apache Flink'},
341:{'b':'Use a load balancer and an Auto Scaling group across multiple AZs with sufficient redundant capacity'},
}
# Restore uniqueness where broad source wording offers other valid mechanisms.
for n in [114,153,179,209]:
    REVIEW[n]['status']='Corrected'
    STEMS[n]='Which AWS service maintains and adjusts an EC2 Auto Scaling group instance count using configured capacity and scaling policies?'
REVIEW[118]['status']='Review only'
REVIEW[118]['reason']='DynamoDB global tables replicate the database across Regions, but they do not automatically fail over every application component. Aurora can also replicate across Regions in supported configurations. The source lacks a DynamoDB data-model requirement and a complete application routing/failover design.'

def normalize(text): return re.sub(r'[^a-z0-9]+',' ',text.lower()).strip()
def build_import():
    source=json.loads(Path(__file__).with_name('book_source.json').read_text())
    seen={}; bank=[]
    for raw in source:
        n=raw['number']; review=REVIEW[n]; status=review['status']
        scenario=STEMS.get(n,raw['scenario'])
        opts=[]; key=review['key'] or raw['source_key']
        eligible=status!='Review only'
        repaired=OPTION_REPAIRS.get(n,{})
        explanation=review['reason']
        for original in raw['options']:
            letter=original['id']; text=repaired.get(letter,original['text'].rstrip(' -'))
            if eligible and letter==key:
                reason='Correct. '+explanation
            elif not eligible:
                reason='Review note. '+option_fact(original['text'].rstrip(' -'))+' The source wording does not make this option uniquely wrong; see the item review above.'
            else:
                contrast=NOTES.get(n,{}).get(letter) or option_fact(original['text'].rstrip(' -'))
                reason='Less suitable for this question. '+contrast+' This item tests '+review['topic']+' rather than that alternative mechanism.'
            opts.append({'id':letter,'text':text,'explanation':reason})
        fingerprint=hashlib.sha256((normalize(review['topic'])+'|'+normalize(scenario)+'|'+'|'.join(sorted(normalize(o['text']) for o in opts))).encode()).hexdigest()
        duplicate=seen.get(fingerprint)
        if duplicate: eligible=False
        else:seen[fingerprint]=f'H{n:03d}'
        refs=[{'title':'AWS documentation: '+review['topic'],'url':'https://docs.aws.amazon.com/'+REF_PATHS[review['ref']]}]
        if review['ref']=='Flink':refs.append({'title':'Kinesis SQL discontinuation and Flink migration','url':'https://docs.aws.amazon.com/kinesisanalytics/latest/dev/discontinuation.html'})
        if n in [271,289]:refs.append({'title':'Official SAA-C03 out-of-scope service list','url':'https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/saa-03-out-of-scope-services.html'})
        changes=[]
        if n in STEMS:changes.append('Practice stem clarified; original preserved below.')
        if repaired:changes.append('Practice option wording corrected; original options preserved below.')
        if key!=raw['source_key']:changes.append(f'Answer key corrected from {raw["source_key"].upper()} to {key.upper()}.')
        if duplicate:changes.append(f'Exact duplicate of {duplicate}; retained for study, excluded from scored selection.')
        provenance={'collection':'Howlett book (user-provided)','source_title':'AWS Certified Solutions Architect Associate (SAA-C03) Exam Prep: 400 Practice Questions and Answers','author':'James Howlett','source_number':n,'source_domain':raw['source_domain'],'source_question_number':(n-1)%100+1,'original_scenario':raw['scenario'],'original_options':raw['options'],'source_key':raw['source_key'],'review_status':status,'reviewed_on':'2026-10-14','changes':changes,'scope_note':'Editorial technical review; not an independent AWS certification endorsement.'}
        bank.append(dict(id=f'H{n:03d}',family='howlett-'+normalize(review['topic']).replace(' ','-'),domain=int(review['task'][0]),task=review['task'],title=f'Howlett #{n} · {review["topic"].capitalize()}',scenario=scenario,services=[SERVICE_NAMES.get(review['ref'],review['ref'])],concepts=[review['topic']],options=opts,correct=[key] if status!='Review only' else [],explanation=explanation+(' '+' '.join(changes) if changes else ''),difficulty='Foundational',references=refs,verification='Editorially reviewed' if status=='Reviewed' else status,eligible=eligible,duplicate_of=duplicate,provenance=provenance))
    validate_import(bank)
    return bank

def validate_import(bank):
    assert len(bank)==400 and len({q['id'] for q in bank})==400
    assert {q['provenance']['source_number'] for q in bank}==set(range(1,401))
    for q in bank:
        assert q['task'] in TASKS and int(q['task'][0])==q['domain']
        assert len(q['options'])==4
        assert all(len(o['explanation'])>80 for o in q['options'])
        assert not q['eligible'] or len(q['correct'])==1
        assert set(q['correct'])<=set(o['id'] for o in q['options'])
        assert not q['duplicate_of'] or not q['eligible']
        assert q['provenance']['source_key'] in ['a','b','c','d']
    return Counter(q['provenance']['review_status'] for q in bank)
