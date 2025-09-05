# filename: aaos_aws_location_arch.py
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Client
from diagrams.onprem.iac import Ansible as MapLibre   # placeholder icon for MapLibre
from diagrams.onprem.compute import Server as GPS

# AWS icons
from diagrams.aws.general import General as Generic
from diagrams.aws.security import Cognito, IAM
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge, SNS, SQS
from diagrams.aws.management import Cloudwatch, Cloudtrail
from diagrams.aws.analytics import KinesisDataStreams as Kinesis

with Diagram(
    "Smart Navigation on AAOS with Amazon Location (High-Level)",
    filename="aaos_aws_location",
    direction="LR",
    show=False,
    outformat="png",
    graph_attr={"splines": "spline", "pad": "0.3", "fontsize": "11", "labelloc": "t"},
):
    # -------- Vehicle (AAOS) --------
    with Cluster("Vehicle • Android Automotive OS (AAOS)"):
        driver_ui = Client("Driver UI\n(Car App Library\nNavigationTemplate)")
        nav_orch  = Client("Nav Orchestrator\n(CarAppService)")
        maplibre  = MapLibre("Map Renderer\n(MapLibre Native)")
        auth_cli  = Client("Auth Client\n(Cognito Identity)")
        gps       = GPS("GPS / Sensors")

        gps >> Edge(label="location updates") >> nav_orch
        driver_ui << Edge(label="guidance / maneuvers") << nav_orch
        maplibre << Edge(label="route geometry") << nav_orch

    # -------- AWS Cloud --------
    with Cluster("AWS Cloud"):
        # Amazon Location Service (use Generic icon placeholders)
        with Cluster("Amazon Location Service"):
            maps   = Generic("Maps\n(GetMap*)")
            places = Generic("Place Index\n(SearchPlaceIndex*)")
            routes = Generic("Route Calculator\n(CalculateRoute*)")
            fences = Generic("Geofences\n(Events)")

        # Identity & Access
        with Cluster("Identity & Access"):
            cognito = Cognito("Amazon Cognito\n(Identity Pool)")
            iam     = IAM("IAM Roles & Policies")

        # Optional serverless backend
        with Cluster("Serverless Backend (Optional)"):
            api  = APIGateway("Amazon API Gateway")
            fn   = Lambda("AWS Lambda")
            db   = Dynamodb("DynamoDB\n(Favorites / Recents)")
            edge = CloudFront("CloudFront\n(Content / OTA)")
            api >> fn
            fn >> db

        # Events & Notifications
        with Cluster("Events & Notifications"):
            evb = Eventbridge("Amazon EventBridge")
            sns = SNS("Amazon SNS")
            sqs = SQS("Amazon SQS (optional)")
            evb >> sns
            evb >> sqs

        # Observability & Telemetry
        with Cluster("Observability"):
            cwatch = Cloudwatch("Amazon CloudWatch")
            ctrail = Cloudtrail("AWS CloudTrail")
            kds    = Kinesis("Kinesis Data Streams\n(optional)")

        # Auth path
        auth_cli >> Edge(label="get temp creds") >> cognito >> Edge(label="assume role") >> iam

        # Tiles, search, routes, geofences
        maplibre >> Edge(label="signed tiles / style (SigV4)") >> maps
        nav_orch >> Edge(label="search / reverse geocode") >> places
        nav_orch >> Edge(label="calculate route / ETA") >> routes
        fences >> Edge(label="enter/exit events") >> evb

        # Backend optional lookups
        fn >> Edge(label="server-side places/routes") >> places
        fn >> routes

        # Push notifications back to app
        sns >> Edge(label="notify device / topic") >> driver_ui

        # Observability wiring
        for svc in [maps, places, routes, fences, api, fn, db, evb, sns]:
            svc >> cwatch
        fn >> ctrail
        kds >> cwatch

    # Proactive tips/reroute to app
    api >> Edge(label="tips / reroute / content") >> nav_orch
