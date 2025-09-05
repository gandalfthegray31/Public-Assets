# personal_copilot_arch_labeled.py
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import Postgresql
from diagrams.aws.network import Route53, CloudFront, APIGateway
from diagrams.aws.iot import IotCore, IotGreengrass
from diagrams.aws.integration import Eventbridge, SQS, SNS, StepFunctions
from diagrams.aws.analytics import KinesisDataStreams, KinesisDataFirehose, Glue, Athena, Quicksight, LakeFormation
from diagrams.aws.storage import S3
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, NeptuneDatabase as Neptune
from diagrams.aws.analytics import OpenSearchService
from diagrams.aws.ml import Sagemaker, Personalize
from diagrams.aws.management import Cloudwatch, Cloudtrail, XRay
from diagrams.aws.security import Cognito, IAM, KMS, WAF, ShieldAdvanced, Macie
from diagrams.aws.mobile import Pinpoint

# fallback if Bedrock icon missing
try:
    from diagrams.aws.ml import Bedrock
    BedrockNode = Bedrock
except Exception:
    BedrockNode = Sagemaker

with Diagram(
    "Personal Co-Pilot on AWS — Numbered Reference Architecture",
    show=False,
    filename="personal_copilot_aws_architecture_labeled",
    direction="LR",
):
    # === (1) Edge / Clients ===
    with Cluster("1. Edge (Vehicle & Mobile)"):
        driver = Users("Driver")
        vehicle_hmi = Server("1a. Vehicle HMI")
        greengrass = Greengrass("1b. IoT Greengrass")
        local_models = Server("1c. Neo Models")
        local_cache = Postgresql("1d. Local Cache")
        mobile_app = Users("1e. Mobile App")

        driver >> vehicle_hmi
        vehicle_hmi >> greengrass
        greengrass >> local_models
        greengrass >> local_cache
        driver >> mobile_app

    # === (2) Ingress & API ===
    with Cluster("2. Ingress & API Layer"):
        dns = Route53("2a. Route53")
        cdn = CloudFront("2b. CloudFront")
        apigw = APIGateway("2c. API Gateway")
        iot = IotCore("2d. IoT Core")
        eb = Eventbridge("2e. EventBridge")

        dns >> cdn >> apigw
        vehicle_hmi >> iot
        mobile_app >> Edge(label="HTTPS") >> cdn
        apigw >> eb
        iot >> eb

    # === (3) Orchestration ===
    with Cluster("3. Orchestration & Async"):
        lamb = Lambda("3a. Lambda")
        sfn = StepFunctions("3b. Step Functions")
        sqs = SQS("3c. SQS")
        sns = SNS("3d. SNS")

        eb >> lamb
        lamb >> sfn
        eb >> sqs
        lamb >> sns

    # === (4) Data Plane ===
    with Cluster("4. Data Plane"):
        with Cluster("4a. Streaming & Lake"):
            kds = KinesisDataStreams("4a1. Kinesis")
            kdf = KinesisDataFirehose("4a2. Firehose")
            s3 = S3("4a3. S3 Lake")
            glue = Glue("4a4. Glue")
            lf = LakeFormation("4a5. Lake Formation")
            athena = Athena("4a6. Athena")

            eb >> kds
            kds >> kdf >> s3
            glue >> lf
            s3 >> glue >> athena

        with Cluster("4b. Operational Stores"):
            ddb = Dynamodb("4b1. DynamoDB")
            os = OpenSearchService("4b2. OpenSearch")
            neptune = Neptune("4b3. Neptune")

            lamb >> ddb
            lamb >> os
            lamb >> neptune

    # === (5) AI/ML ===
    with Cluster("5. AI / ML"):
        bedrock = BedrockNode("5a. Bedrock")
        sm = Sagemaker("5b. SageMaker")
        personalize = Personalize("5c. Personalize")

        ddb >> personalize
        os >> bedrock
        neptune >> sm
        s3 >> sm
        lamb >> [bedrock, personalize, sm]

    # === (6) Security & Compliance ===
    with Cluster("6. Identity & Security"):
        cognito = Cognito("6a. Cognito")
        iam = IAM("6b. Verified Permissions")
        kms = KMS("6c. KMS")
        macie = Macie("6d. Macie")
        waf = WAF("6e. WAF")
        shield = ShieldAdvanced("6f. Shield")
        trail = Cloudtrail("6g. CloudTrail")

        cdn >> waf >> shield
        apigw >> cognito
        [apigw, lamb, s3, ddb, os, neptune] >> kms
        s3 >> macie
        [apigw, lamb, eb, sfn, sqs, sns] >> trail
        [apigw, lamb] >> iam

    # === (7) Observability ===
    with Cluster("7. Observability & Analytics"):
        cw = Cloudwatch("7a. CloudWatch")
        xray = XRay("7b. X-Ray")
        qs = QuickSight("7c. QuickSight")

        [apigw, lamb, sfn, eb, iot] >> cw
        [apigw, lamb] >> xray
        [athena, ddb, os] >> qs

    # === (8) Engagement ===
    pinpoint = Pinpoint("8. Pinpoint")
    lamb >> pinpoint
    pinpoint >> mobile_app
