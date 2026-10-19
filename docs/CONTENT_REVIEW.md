# Content validation and review status

All 400 original case items are flagged **Technical review pending**. This means no independent item-by-item certification subject-matter review is claimed. Passing structural checks does not establish psychometric quality or certification readiness.

The 100 original case specifications each produce four educational perspectives. They are deliberately related. The bank prioritizes stable architectural principles rather than prices, quotas, or guarantees that depend on a specific Region/configuration. The source specifications include a correct architecture, a complementary control, and three less suitable choices with explicit reasons.

Automated checks cover unique IDs and exact stems, 120/104/96/80 distribution, all 14 task mappings, single/multiple response option counts, correct-key membership, unique options per item, explanation presence, and official-documentation URL domains. These do not independently detect every semantic duplicate or resolve all context-sensitive technical claims.

Selected technical anchors checked while implementing:

- [SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html): timeout behavior, deletion after success, duplicate-delivery caveats.
- [RDS Multi-AZ DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html): synchronous standby, failover, no reads from the single standby. Multi-AZ DB clusters differ.
- [S3 storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html): access latency, multi-AZ/single-AZ choices, retrieval/minimum-duration trade-offs.
- [Gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html): S3/DynamoDB support, routing, NAT avoidance.
- [Third-party role access](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html): customer-specific vendor external IDs and trust/permissions separation.
- [DR strategies](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html): backup/restore, pilot light, warm standby and active/active trade-offs; actual RTO/RPO require testing.
- [CloudFront private S3 origins](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html): OAC and REST origins versus unsupported S3 website origins.
- [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html): version protection and compliance/governance differences.

Remaining review work includes independent scrutiny of every question/answer explanation, harder distractors for some introductory cases, better separation of related perspectives, verification of all reference deep links, and broader coverage of the guide's less represented services. Difficulty labels are editorial, not calibrated using learner data. The original questions are learning material, not official or endorsed AWS exam content.


## User-provided book import

The separate Howlett collection has 400 retained source items and 1,600 option explanations. It underwent editorial review against AWS service documentation and the official scope. 247 items retain their key/wording, 45 have recorded key or wording corrections, and 108 are available for study without a unique scored answer or are unsuitable for current scored SAA practice. All source stems, options and keys remain in provenance. The report is `BOOK_IMPORT_REVIEW.json` and the readable export is in `output/text/`.

The rules separate factual distractors from plausible alternatives: ambiguous questions do not invent a unique correct option or label all other applicable services wrong. Current-service names and scope matter, including Shield Standard versus Advanced, IAM temporary credentials, Global Accelerator routing versus deployment, Aurora's primary write Region, and the Flink rename/Kinesis SQL discontinuation. The import is an editorial review, not independent subject-matter certification or an AWS endorsement.

No exact duplicate stem-and-option-set fingerprints were detected in the 400 imports. There are many related and near-repeated definitions; the shared concept-family IDs let mock generation prefer different concepts. Exact duplicate checking does not establish semantic independence.
