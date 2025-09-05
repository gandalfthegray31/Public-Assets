# personal_copilot_architecture_full.py
"""
Generates a labeled AWS architecture diagram for the "Personal Co-Pilot" platform.
Output: personal_copilot_aws_architecture_labeled.png

Prereqs:
  - Graphviz installed (brew install graphviz OR sudo apt-get install graphviz -y)
  - pip install diagrams
Run:
  python personal_copilot_architecture_full.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import Postgresql

# --- AWS icon imports with version-safe fallbacks -----------------------------
from diagrams.aws.network import Route53, CloudFront, APIGateway
from diagrams.aws.iot import IotCore
from diagrams.aws.iot import IotGreengrass as Greengrass
from diagrams.aws.integration import Eventbridge, SQS, SNS, StepFunctions
from diagrams.aws.storage import S3
from diagrams.aws.compute import Lambda

# DynamoDB is stable
from diagrams.aws.database import Dynamodb

# Neptune can be NeptuneDatabase OR Neptune, depending on diagrams version
try:
    from diagrams.aws.database import NeptuneDatabase as NeptuneIcon
except Exception:
    try:
        from diagrams.aws.database import Neptune as NeptuneIcon
    except Exception:
        NeptuneIcon = None  # will fallback to generic Server later

# OpenSearch sometimes lives in analytics (newer); fallback to elasticsearch icon if needed
try:
    from diagrams.aws.analytics import OpenSearchService as OpenSearchIcon
except Exception:
    try:
        from diagrams.aws.analytics import ElasticsearchService as OpenSearchIcon
    except Exception:
        OpenSearchIcon = None  # fallback later

# Lake Formation may be missing in older releases
try:
    from diagrams.aws.analytics import LakeFormation as LakeFormationIcon
except Exception:
    LakeFormationIcon = None

# Kinesis modules
from diagrams.aws.analytics import (
    KinesisDataStreams, KinesisDataFirehose, Glue, Athena, Quicksight
)

# ML layer: Bedrock icon may not exist; SageMaker & Personalize are stable
from diagrams.aws.ml import Sagemaker, Personalize
try:
    from diagrams.aws.ml import Bedrock as BedrockIcon
except Exception:
    BedrockIcon = None

from diagrams.aws.management import Cloudwatch, Cloudtrail
try:
    from diagrams.aws.management import XRay
except ImportError:
    from diagrams.onprem.monitoring import Prometheus as XRay  # fallback


# Security
from diagrams.aws.security import Cognito, IAM, KMS, WAF, ShieldAdvanced, Macie

# Engagement
try:
    from diagrams.aws.mobile import Pinpoint
except Exception:
    Pinpoint = None

# --- Helpers to instantiate icons or fallback to a labeled Server -------------
def node_or_fallback(IconClass, label):
    if IconClass is None:
        return Server(f"{label}\n(fallback)")
    return IconClass(label)

with Diagram(
    "Personal Co-Pilot on AWS — Numbered Reference Architecture",
    show=False,
    filename="personal_copilot_aws_architecture_labeled",
    direction="LR",
):
    # =============================
    # (1) EDGE / CLIENTS
    # =============================
    with Cluster("1. Edge (Vehicle \n & Mobile)"):
        driver = Users("Driver")
        vehicle_hmi = Server("1a. Vehicle HMI \n (AAOS/IVI)")
        greengrass = Greengrass("1b. AWS IoT Greengrass v2\n(edge runtime)")
        local_models = Server("1c. Neo-compiled models\n(ONNX/TensorRT)")
        local_cache = Postgresql("1d. Local cache (SQLite/FS)")
        mobile_app = Users("1e. Mobile App \n (Android/iOS)")

        driver >> vehicle_hmi
        vehicle_hmi >> greengrass
        greengrass >> local_models
        greengrass >> local_cache
        driver >> mobile_app

    # =============================
    # (2) INGRESS & API
    # =============================
    with Cluster("2. Ingress & API Layer"):
        dns = Route53("2a. Route 53 (DNS)")
        cdn = CloudFront("2b. CloudFront (CDN)")
        apigw = APIGateway("2c. API Gateway (REST/GraphQL)")
        iot = IotCore("2d. IoT Core (MQTT + Shadows)")
        eb = Eventbridge("2e. EventBridge (routing)")

        dns >> cdn >> apigw
        vehicle_hmi >> iot
        mobile_app >> Edge(label="HTTPS") >> cdn
        apigw >> eb
        iot >> eb

    # =============================
    # (3) ORCHESTRATION & ASYNC
    # =============================
    with Cluster("3. Orchestration & Async"):
        lamb = Lambda("3a. Lambda (microservices)")
        sfn = StepFunctions("3b. Step Functions (workflows)")
        sqs = SQS("3c. SQS (buffering)")
        sns = SNS("3d. SNS (fan-out)")

        eb >> lamb
        lamb >> sfn
        eb >> sqs
        lamb >> sns

    # =============================
    # (4) DATA PLANE
    # =============================
    with Cluster("4. Data Plane"):
        # --- Streaming & Lake ---
        with Cluster("4a. Streaming & Lake"):
            kds = KinesisDataStreams("4a1. Kinesis Data Streams")
            kdf = KinesisDataFirehose("4a2. Kinesis Firehose")
            s3 = S3("4a3. S3 Data Lake")
            glue = Glue("4a4. Glue (ETL, Catalog)")
            lf = node_or_fallback(LakeFormationIcon, "4a5. Lake Formation (governance)")
            athena = Athena("4a6. Athena (SQL on S3)")

            eb >> kds
            kds >> kdf >> s3
            glue >> lf
            s3 >> glue >> athena

        # --- Operational / Realtime Stores ---
        with Cluster("4b. Operational Stores"):
            ddb = Dynamodb("4b1. DynamoDB (Profiles)")
            os = node_or_fallback(OpenSearchIcon, "4b2. OpenSearch (Vectors/RAG)")
            neptune = node_or_fallback(NeptuneIcon, "4b3. Neptune (Graph)")

            lamb >> ddb
            lamb >> os
            lamb >> neptune

    # =============================
    # (5) AI / ML LAYER
    # =============================
    with Cluster("5. AI / ML"):
        bedrock = node_or_fallback(BedrockIcon, "5a. Amazon Bedrock\n(LLMs, Agents, KB)")
        sm = Sagemaker("5b. SageMaker\n(Training/Inference/Feature Store)")
        personalize = Personalize("5c. Amazon Personalize\n(Recs)")

        # Data into ML
        ddb >> personalize
        os >> bedrock
        neptune >> sm
        s3 >> sm

        # Inference paths
        lamb >> bedrock
        lamb >> personalize
        lamb >> sm

    # =============================
    # (6) IDENTITY & SECURITY
    # =============================
    with Cluster("6. Identity & Security"):
        cognito = Cognito("6a. Cognito (AuthN)")
        iam = IAM("6b. Verified Permissions (Cedar)")
        kms = KMS("6c. KMS (Encryption)")
        macie = Macie("6d. Macie (PII Discovery)")
        waf = WAF("6e. WAF (L7 protection)")
        shield = ShieldAdvanced("6f. Shield Advanced (DDoS)")
        trail = Cloudtrail("6g. CloudTrail (Audit)")

        cdn >> waf >> shield
        apigw >> cognito
        [apigw, lamb, s3, ddb, os, neptune] >> kms
        s3 >> macie
        [apigw, lamb, eb, sfn, sqs, sns] >> trail
        [apigw, lamb] >> iam

    # =============================
    # (7) OBSERVABILITY & BI
    # =============================
    with Cluster("7. Observability & Analytics"):
        cw = Cloudwatch("7a. CloudWatch (metrics/logs)")
        xray = XRay("7b. X-Ray (traces)")
        qs = Quicksight("7c. Quicksight (dashboards)")

        [apigw, lamb, sfn, eb, iot] >> cw
        [apigw, lamb] >> xray
        [athena, ddb, os] >> qs

    # =============================
    # (8) ENGAGEMENT
    # =============================
    if Pinpoint is not None:
        pinpoint = Pinpoint("8. Pinpoint (notifications/A-B)")
    else:
        pinpoint = Server("8. Pinpoint (notifications/A-B)\n(fallback)")

    lamb >> pinpoint
    pinpoint >> mobile_app

    # =============================
    # (9) LEGEND / ANNOTATIONS
    # =============================
    with Cluster("Legend — One-line Role per Number"):
        l1 = Server("1. Edge: Real-time personalization at \n vehicle/mobile with \n Greengrass + on-device models.")
        l2 = Server("2. Ingress & API: Secure entry via \n API Gateway/IoT Core; \n traffic terminates at CloudFront.")
        l3 = Server("3. Orchestration: Event-driven flows \n & async reliability with Lambda, \n SQS, SNS, Step Functions.")
        l4 = Server("4. Data Plane: Lake on S3 + \n governed access; \n DynamoDB/Neptune/OpenSearch for fast reads & RAG.")
        l5 = Server("5. AI/ML: Bedrock agents + \n SageMaker + Personalize \n to rank, reason, and recommend.")
        l6 = Server("6. Security: Cognito auth, \n Cedar-based consent, KMS encryption, \n WAF/Shield, Macie, audit trails.")
        l7 = Server("7. Observability: CloudWatch/X-Ray \n for SLOs; Quicksight for product \n & business insights.")
        l8 = Server("8. Engagement: Pinpoint for \n messaging, journeys, and \n A/B testing.")
