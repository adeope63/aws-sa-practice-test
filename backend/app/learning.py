from .seed import DOCS
# Original summaries: the documentation links are the technical reference.
GROUPS = [
('Compute','EC2 vs Lambda vs Fargate','3.2',[
('EC2','Full OS control, custom runtimes, long-running workloads','Manage instances, patching and capacity; choose purchase options deliberately'),
('Lambda','Short stateless event handlers and bursty APIs','Per-invocation duration limit; cold starts and concurrency affect latency'),
('Fargate','Long-running containers without managing EC2 hosts','Container resource sizing and task networking remain your responsibility')]),
('Storage','S3 vs EBS vs EFS','3.1',[
('S3','Durable object storage, data lakes, static assets','Object APIs; not a native POSIX or block device'),
('EBS','Persistent block volumes for EC2 and database I/O','Volumes are AZ-scoped; ordinary attachments are not shared regional file storage'),
('EFS','Shared elastic NFS files for Linux workloads','Throughput and access patterns matter; One Zone differs from Regional resilience')]),
('Databases','RDS vs Aurora vs DynamoDB','3.3',[
('RDS','Managed relational engines and transactional SQL','Plan instance sizing, connections, backups and read scaling'),
('Aurora','MySQL/PostgreSQL-compatible relational applications','Distributed cluster storage; read replicas and global designs have distinct trade-offs'),
('DynamoDB','Key-value/document access at managed scale','Design partition keys and indexes around access patterns; not general SQL joins')]),
('Load balancing','ALB vs NLB vs Gateway Load Balancer','3.4',[
('ALB','HTTP routing by host/path and web application integration','Application layer; not a general arbitrary TCP load balancer'),
('NLB','Transport-layer TCP/UDP/TLS use cases and static IP requirements','No HTTP path-based routing'),
('Gateway Load Balancer','Transparent insertion of supported network appliances','Requires compatible GENEVE appliances and careful bidirectional routing')]),
('Edge','CloudFront vs Global Accelerator','3.4',[
('CloudFront','Cache and deliver HTTP content near users','Cache key and TTL configuration determine freshness and isolation'),
('Global Accelerator','Static anycast IPs and optimized routing to regional TCP/UDP endpoints','Does not cache content; endpoint health and routing policies matter')]),
('Messaging','SQS vs SNS vs EventBridge','2.1',[
('SQS','Durable work buffering for competing workers','Standard delivery is at least once; FIFO ordering is per message group'),
('SNS','Publish/subscribe fan-out to multiple subscriptions','Use SQS subscribers when each consumer needs a durable retry backlog'),
('EventBridge','Content-based event routing and AWS/SaaS integration','Configure target retries and dead-letter handling; not a general worker backlog')]),
('Network security','Security Groups vs Network ACLs','1.2',[
('Security Groups','Stateful resource interface filtering with allow rules','No explicit deny rules; return traffic is tracked'),
('Network ACLs','Stateless subnet-level allow/deny rules','Rule order matters; explicitly allow return traffic and ephemeral ports')]),
('Internet connectivity','NAT Gateway vs Internet Gateway','4.4',[
('NAT Gateway','Outbound IPv4 translation for private instances','Zonal dependency, hourly and processing costs; no unsolicited inbound connections'),
('Internet Gateway','VPC internet routing for appropriately addressed resources','A route alone does not grant internet access to private IPv4 instances')]),
('VPC connectivity','VPC Peering vs Transit Gateway','4.4',[
('VPC Peering','Simple direct communication between nonoverlapping VPCs','Nontransitive; larger meshes increase route management'),
('Transit Gateway','Hub connectivity and controlled transitive routing at scale','Attachment and processing costs; segment networks with route tables')]),
('Hybrid networking','VPN vs Direct Connect','3.4',[
('Site-to-Site VPN','Encrypted tunnels over existing internet connectivity','Internet path variability; configure both tunnels'),
('Direct Connect','Dedicated private connectivity for predictable large network demand','Not encrypted by default; build redundant paths and add encryption where needed')]),
('Database availability','Multi-AZ vs Read Replicas','2.2',[
('RDS Multi-AZ DB instance','Multi-AZ DB instance: synchronous standby for managed failover','Single standby does not serve reads; Multi-AZ DB clusters are a different deployment'),
('RDS Read Replicas','Read replicas for read scaling with asynchronous replication','Replication lag and promotion behavior must be understood; not a substitute for backups')]),
('Purchase models','Reserved Instances vs Savings Plans vs Spot','4.2',[
('Reserved Instances','Reserved Instances discount qualifying committed instance usage','Matching scope/configuration matters; not every reservation includes capacity reservation'),
('Savings Plans','Hourly spending commitment for eligible compute usage','Compute Savings Plans cover eligible EC2, Fargate and Lambda; unused commitment costs money'),
('Spot Instances','Spot uses spare EC2 capacity for interruptible jobs','Capacity is reclaimable; checkpoint and diversify instance choices')]),
]
COMPARISONS=[dict(id=i,title=title,category=category,task=task,services=[dict(name=name,use_case=use,tradeoff=tradeoff,url='https://docs.aws.amazon.com/'+DOCS.get(name,DOCS['VPC'])) for name,use,tradeoff in entries]) for i,(category,title,task,entries) in enumerate(GROUPS,1)]
