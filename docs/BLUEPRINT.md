# Official scope review

Reviewed on 14 October 2026 against AWS's current SAA-C03 documentation before implementation.

- [Exam guide, response types, scored/unscored structure and results](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html)
- [Domain 1: tasks 1.1–1.3, knowledge and skills](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain1.html)
- [Domain 2: tasks 2.1–2.2, knowledge and skills](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html)
- [Domain 3: tasks 3.1–3.5, knowledge and skills](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html)
- [Domain 4: tasks 4.1–4.4, knowledge and skills](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain4.html)
- [Technologies and concepts](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/saa-technologies-concepts.html)
- [Service short-name conventions](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/saa-service-mentions.html)
- [In-scope services](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/saa-03-in-scope-services.html)
- [Out-of-scope services](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/saa-03-out-of-scope-services.html)

| Official domain | Weight | Bank | All-scored mock | Scored portion in simulation |
|---|---:|---:|---:|---:|
| Design Secure Architectures | 30% | 120 | 20 | 15 |
| Design Resilient Architectures | 26% | 104 | 17 | 13 |
| Design High-Performing Architectures | 24% | 96 | 15 | 12 |
| Design Cost-Optimized Architectures | 20% | 80 | 13 | 10 |

Simulation adds 15 random unscored items and hides their status during the attempt. A plain percentage does not reproduce AWS's scaled scoring system. The app deliberately avoids converting practice percentages to official scaled scores.

`backend/app/blueprint.py` holds the full official task names. The source validator checks every mapping and confirms coverage of all 14 tasks. Service/concept coverage is a study selection, not a claim that every possible guide knowledge point or every in-scope service has a question. Scope lists are nonexhaustive and can change.
