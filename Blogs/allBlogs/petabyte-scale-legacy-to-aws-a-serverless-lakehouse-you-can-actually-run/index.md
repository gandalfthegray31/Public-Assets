Here’s your piece converted into a **Medium-ready article**. It keeps a clean structure, skimmable sections, copy-pasteable code, and **preserves external links** to official docs so readers can dive deeper.

---

# Petabyte-Scale Legacy-to-AWS: Serverless Lakehouse, Tag-Driven FinOps, and ML on Autopilot

**TL;DR** — A pragmatic blueprint to move *petabytes* of historical + CDC data from legacy databases (Oracle, SQL Server, Teradata, Db2, MongoDB, etc.) into an **S3-based lakehouse** using **AWS DMS → Parquet**, govern with **Lake Formation LF-tags**, query with **Athena (Iceberg)**, index with **OpenSearch Serverless**, and orchestrate **serverless ML** via **EventBridge Scheduler + Step Functions + SageMaker**. Cost is controlled by **S3 object tags** + **Intelligent-Tiering** + lifecycle.

---

## Why this stack?

* **Zero/low ops:** S3, Athena, OpenSearch Serverless, Step Functions, EventBridge Scheduler, Glue, SageMaker jobs — all managed and elastic.
* **Governed access:** **Lake Formation LF-tag** policy grants by *attributes*, not raw ARNs.
* **Cost optimized:** Lifecycle by **object tags**, **Intelligent-Tiering**, compression + columnar everywhere.
* **Future-proof:** **Iceberg** ACID/time travel; open file formats (Parquet).

---

## Reference Architecture

**Ingest**

* Historical bulk: **[AWS Snowball/Snowmobile](https://aws.amazon.com/snow/)** to S3.
* Ongoing: **[AWS Database Migration Service (DMS) → S3 Parquet](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html)** (+ CDC).

**Storage & Catalog**

* **[Amazon S3](https://aws.amazon.com/s3/)** (versioned, encrypted).
* **Object tags** + lifecycle → **[Intelligent-Tiering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html)** / Glacier.
* **[AWS Glue Data Catalog](https://aws.amazon.com/glue/)** + **[Lake Formation LF-tags](https://docs.aws.amazon.com/lake-formation/latest/dg/tag-based-access-control.html)**.
* **[Athena + Apache Iceberg](https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg.html)** for ACID/time travel.

**Query, Search & Features**

* **[Athena partition projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html)** to avoid metastore bloat.
* **[Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)** for free-text/metadata search.

**ML/AI (serverless orchestration)**

* **[EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html)** → **[Step Functions service integrations](https://docs.aws.amazon.com/step-functions/latest/dg/integrate-services.html)** (Athena/Glue/SageMaker) → **[SageMaker training jobs](https://docs.aws.amazon.com/step-functions/latest/dg/connect-sagemaker.html)**.

**FinOps**

* **[S3 Storage Lens](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage_lens.html)** for org-wide usage/optimization insights.

---

## Legacy DBs you’ll most often migrate

Based on industry usage (see **[DB-Engines ranking](https://db-engines.com/en/ranking)**): **Oracle, MySQL, SQL Server, PostgreSQL, MongoDB**, plus MPPs like **Teradata/Netezza** and enterprise **Db2**.

**Patterns that work well:**

* Oracle/SQL Server/Db2 → **DMS full+CDC → S3 (Parquet)** → **Iceberg tables in Athena**; optionally federate to Redshift Serverless later.
* Teradata/Netezza → bulk export + **Snowball → S3** → register via Glue → Iceberg.
* MongoDB → **DMS to S3 (JSON/Parquet)**; text indexing to OpenSearch Serverless.

---

## S3 bucket with tag-driven lifecycle (CDK, TypeScript)

```ts
// cdk/lib/data-lake-stack.ts
import { Stack, StackProps, Duration, RemovalPolicy, Tags } from 'aws-cdk-lib';
import { Bucket, BlockPublicAccess, BucketEncryption, LifecycleRule, StorageClass } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class DataLakeStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const raw = new Bucket(this, 'RawBucket', {
      bucketName: `org-raw-${this.account}-${this.region}`,
      encryption: BucketEncryption.S3_MANAGED,
      versioned: true,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      lifecycleRules: [
        <LifecycleRule>{
          enabled: true,
          tagFilters: { 'data.tier': 'archive' },
          transitions: [{ storageClass: StorageClass.DEEP_ARCHIVE, transitionAfter: Duration.days(30) }]
        },
        <LifecycleRule>{
          enabled: true,
          transitions: [{ storageClass: StorageClass.INTELLIGENT_TIERING, transitionAfter: Duration.days(0) }]
        },
        <LifecycleRule>{
          enabled: true,
          tagFilters: { 'retention.days': '7' },
          expiration: Duration.days(7)
        }
      ],
      removalPolicy: RemovalPolicy.RETAIN
    });

    Tags.of(raw).add('env', 'prod');
    Tags.of(raw).add('pii', 'no');
  }
}
```

* **Object tags** drive fine-grained lifecycle (filter by tag). See **[S3 object tagging](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-tagging.html)** and **[lifecycle filters](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-filters.html)**.
* Put unknown-access data straight into **[S3 Intelligent-Tiering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering.html)**.

---

## DMS → S3 (Parquet) for full load + CDC

**Target endpoint (S3 Parquet):**

```json
{
  "EndpointIdentifier": "s3-target",
  "EndpointType": "target",
  "EngineName": "s3",
  "S3Settings": {
    "BucketName": "org-raw-123456789012-us-east-1",
    "ServiceAccessRoleArn": "arn:aws:iam::123456789012:role/dms-s3-role",
    "DataFormat": "parquet",
    "CompressionType": "gzip",
    "DatePartitionEnabled": true,
    "DatePartitionSequence": "YYYY/MM/DD",
    "ParquetVersion": "parquet-2-0",
    "cdcPath": "cdc/",
    "EnableStatistics": true
  }
}
```

**Task settings (include ops in full load; then CDC):**

```json
{
  "FullLoadSettings": {
    "TargetTablePrepMode": "DO_NOTHING",
    "StopTaskCachedChangesApplied": true
  },
  "TargetMetadata": { "ParallelApplyThreads": 8 },
  "Logging": { "EnableLogging": true },
  "ControlTablesSettings": { "ControlSchema": "dms_control" },
  "ChangeProcessingDdlHandlingPolicy": { "HandleSourceTableDropped": true },
  "ChangeProcessingTuning": { "BatchApplyEnabled": true },
  "FullLoadToCdcSettings": { "IncludeOpForFullLoad": true }
}
```

Docs: **[DMS → S3 Parquet](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html)** • **[How-to (KB)](https://repost.aws/knowledge-center/dms-s3-parquet-format)** • **[DMS endpoints](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Endpoints.html)**

---

## Curate to Parquet + tag new objects (Glue, PySpark)

```python
# glue_jobs/curate_to_parquet.py
import boto3, os
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, current_date

spark = SparkSession.builder.appName("curate").getOrCreate()
src  = os.environ["SRC"]
dest = os.environ["DEST"]

df = spark.read.parquet(src).withColumn("ingest_date", current_date())

(df.repartition(1)                     # adjust for your file sizing goals
   .write.mode("append")
   .partitionBy("ingest_date")
   .parquet(dest))

# Tag new objects for lifecycle ("archive after 30d" rule)
s3 = boto3.client('s3')
bucket = dest.replace("s3://", "").split("/")[0]
prefix = "/".join(dest.replace("s3://", "").split("/")[1:])
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    for obj in page.get("Contents", []):
        s3.put_object_tagging(
          Bucket=bucket, Key=obj["Key"],
          Tagging={"TagSet":[{"Key":"data.tier","Value":"archive"}]}
        )
```

* Tag API: **[`PutObjectTagging`](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-tagging.html)**.

---

## Lake Formation governance with LF-tags

Grant access by attributes instead of listing every table/column.

```bash
# Define LF-tags
aws lakeformation create-lf-tag --tag-key pii --tag-values yes no
aws lakeformation create-lf-tag --tag-key domain --tag-values finance ops hr

# Attach tags to a table
aws lakeformation add-lf-tags-to-resource --resource '{
  "Table": {"DatabaseName":"curated","Name":"orders"}
}' --lf-tags '[{"TagKey":"pii","TagValues":["yes"]},{"TagKey":"domain","TagValues":["finance"]}]'

# Grant permissions by tag expression
aws lakeformation grant-permissions \
  --principal '{"DataLakePrincipalIdentifier":"arn:aws:iam::123:role/analyst"}' \
  --permissions SELECT \
  --resource '{"LFTagPolicy":{"ResourceType":"TABLE","Expression":[{"TagKey":"pii","TagValues":["no"]}]}}'
```

Docs: **[LF-tags (TBAC)](https://docs.aws.amazon.com/lake-formation/latest/dg/tag-based-access-control.html)** • **[Create/manage LF-tags](https://docs.aws.amazon.com/lake-formation/latest/dg/TBAC-creating-tags.html)**

---

## Iceberg tables in Athena (ACID + time travel)

```sql
-- Create a database rooted in S3
CREATE DATABASE IF NOT EXISTS curated
LOCATION 's3://org-curated-123456789012-us-east-1/';

-- CTAS into Iceberg, partitioning for performance
CREATE TABLE curated.orders_iceberg
WITH (
  table_type='ICEBERG',
  location='s3://org-curated-123456789012-us-east-1/orders_iceberg/',
  format='PARQUET',
  partitioning=ARRAY['bucket(order_id, 16)','ingest_date']
) AS
SELECT * FROM raw_db.orders_parquet;

-- Time-travel read
SELECT * FROM curated.orders_iceberg FOR VERSION AS OF TIMESTAMP '2025-08-01 00:00:00';
```

Docs: **[Athena + Iceberg](https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg.html)** • **[Prescriptive guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/getting-started.html)**

### Huge partition spaces? Use partition projection

```sql
CREATE EXTERNAL TABLE raw_db.clicks (
  user_id string, ts timestamp, ...
)
PARTITIONED BY (dt string)
LOCATION 's3://org-raw-.../clicks/'
TBLPROPERTIES (
  'projection.enabled'='true',
  'projection.dt.type'='date',
  'projection.dt.range'='2020/01/01,NOW',
  'projection.dt.format'='yyyy/MM/dd',
  'storage.location.template'='s3://org-raw-.../clicks/dt=${dt}/'
);
```

Docs: **[Partition projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html)** • **[Supported types](https://docs.aws.amazon.com/athena/latest/ug/partition-projection-supported-types.html)**

---

## Make the lake **searchable** (OpenSearch Serverless)

Index JSON/text columns or document blobs for discovery.

**S3 → Lambda (indexer) → OpenSearch Serverless**:

```js
// lambda/index-to-opensearch.js
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import fetch from "node-fetch";

const S3 = new S3Client({});
const OPENSEARCH_URL = process.env.OPENSEARCH_URL;  // serverless collection endpoint
const INDEX = process.env.INDEX || "docs";

export const handler = async (event) => {
  for (const r of event.Records) {
    const { name: bucket } = r.s3.bucket;
    const { key } = r.s3.object;

    const resp = await S3.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
    const body = await resp.Body.transformToString(); // JSON or text
    const doc = JSON.parse(body);

    const res = await fetch(`${OPENSEARCH_URL}/${INDEX}/_doc/${encodeURIComponent(key)}`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ s3key: key, ...doc })
    });
    if (!res.ok) throw new Error(await res.text());
  }
};
```

Docs: **[OpenSearch Serverless overview](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)** • **[Serverless API ref](https://docs.aws.amazon.com/opensearch-service/latest/ServerlessAPIReference/Welcome.html)**

---

## Serverless ML pipeline (Scheduler → Step Functions → Athena/Glue/SageMaker)

**1) Schedule retrains nightly** with **EventBridge Scheduler**.
**2) Step Functions** runs: **Athena extract → Glue feature job → SageMaker training**.
**3) Model artifacts land in S3; optionally deploy serverless inference later.**

### EventBridge Scheduler → Step Functions (CDK snippet)

```ts
// cdk: schedule daily 02:00 UTC
import * as scheduler from 'aws-cdk-lib/aws-scheduler';

new scheduler.CfnSchedule(this, 'DailyRetrain', {
  flexibleTimeWindow: { mode: 'OFF' },
  scheduleExpression: 'cron(0 2 * * ? *)',
  target: {
    arn: stateMachine.stateMachineArn,
    roleArn: scheduleRole.roleArn,
    input: JSON.stringify({ trainingDate: new Date().toISOString().slice(0,10) })
  }
});
```

* Docs: **[EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html)** • **[CDK construct](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_scheduler/README.html)**

### Step Functions (ASL excerpt)

```json
{
  "StartAt": "AthenaExtract",
  "States": {
    "AthenaExtract": {
      "Type": "Task",
      "Resource": "arn:aws:states:::athena:startQueryExecution.sync",
      "Parameters": {
        "QueryString.$": "States.Format('SELECT * FROM curated.orders_iceberg WHERE dt = {}', $.trainingDate)",
        "QueryExecutionContext": { "Database": "curated" },
        "ResultConfiguration": { "OutputLocation": "s3://org-features/out/" }
      },
      "Next": "GlueFeatureJob"
    },
    "GlueFeatureJob": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": { "JobName": "build_features", "Arguments": {"--date.$":"$.trainingDate"} },
      "Next": "SageMakerTrain"
    },
    "SageMakerTrain": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
      "Parameters": {
        "TrainingJobName.$": "States.Format('xgb-{}', $.trainingDate)",
        "AlgorithmSpecification": {
          "TrainingImage": "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.7-1",
          "TrainingInputMode": "File"
        },
        "InputDataConfig": [{
          "ChannelName": "train",
          "DataSource": { "S3DataSource": {
            "S3DataType": "S3Prefix", "S3Uri": "s3://org-features/out/",
            "S3DataDistributionType": "FullyReplicated" }}}
        ],
        "OutputDataConfig": { "S3OutputPath": "s3://org-models/xgb/" },
        "ResourceConfig": { "InstanceType": "ml.m7i.2xlarge", "InstanceCount": 1, "VolumeSizeInGB": 50 },
        "RoleArn": "arn:aws:iam::123:role/sm-exec"
      },
      "End": true
    }
  }
}
```

Docs: **[Step Functions + Athena](https://docs.aws.amazon.com/step-functions/latest/dg/connect-athena.html)** • **[Glue](https://docs.aws.amazon.com/step-functions/latest/dg/integrate-services.html)** • **[SageMaker](https://docs.aws.amazon.com/step-functions/latest/dg/connect-sagemaker.html)**

### (Alt) Train using SageMaker SDK (Python)

```python
from sagemaker import Session
from sagemaker.inputs import TrainingInput
from sagemaker.estimator import Estimator

sess = Session()
est = Estimator(
  image_uri="683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.7-1",
  role="arn:aws:iam::123:role/sm-exec",
  instance_count=1, instance_type="ml.m7i.2xlarge",
  output_path="s3://org-models/xgb/"
)
est.fit({"train": TrainingInput("s3://org-features/out/")})
```

---

## Cost controls to wire in on day 1

1. **Columnar + compression** (Parquet + gzip) via DMS and CTAS.
2. **Lifecycle by tag**: `data.tier=archive` → transition to Glacier Deep Archive; `retention.days=7` → expire staging.
3. **Intelligent-Tiering** default class for unpredictable access patterns.
4. **Partition projection** + periodic **Iceberg compaction** for big data sets.
5. Org-wide visibility with **S3 Storage Lens** to right-size rules/prefixes.

Docs:

* [Object tagging + lifecycle filter](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-tagging.html) • [Lifecycle filters](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-filters.html)
* [Intelligent-Tiering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering.html) • [How it works](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html)
* [Storage Lens](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage_lens.html)

---

## Producer uploads with tags (no extra job needed)

You can set tags **on PUT**:

```
PUT /bucket/key HTTP/1.1
x-amz-tagging: data.tier=archive&retention.days=30
x-amz-storage-class: INTELLIGENT_TIERING
```

Docs: **[`PutObject` + `x-amz-tagging`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html)** • **[Tagging guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-tagging.html)**

---

## Quick mapping: legacy → AWS pattern

| Legacy                    | Landing & CDC                       | Lakehouse & Query                                          | Notes                                         |
| ------------------------- | ----------------------------------- | ---------------------------------------------------------- | --------------------------------------------- |
| Oracle / SQL Server / Db2 | **DMS** full + CDC → **S3 Parquet** | **Athena (Iceberg)** + LF-tags                             | Use SCT later if moving to Aurora PG.         |
| Teradata / Netezza        | Bulk export + **Snowball → S3**     | Register in Glue → **Iceberg**                             | Start with historical bulk, then incremental. |
| MongoDB                   | **DMS → S3** (JSON/Parquet)         | Athena on JSON/Parquet; **OpenSearch Serverless** for text | Great for doc search + analytics.             |

---

## Monorepo layout you can adopt

```
repo/
├─ cdk/                    # buckets, lifecycle, LF-tags, Scheduler, StepFn, Lambda, OpenSearch
├─ glue_jobs/              # curation + feature engineering
├─ lambdas/                # s3->opensearch indexer
├─ sql/                    # Athena DDL/CTAS, Iceberg, projection
└─ notebooks/              # SageMaker SDK jobs and experiments
```

---

## Ops runbook (checklist)

* **Buckets**: versioning on, block public, SSE (S3 or KMS).
* **Ingest**: Snowball for multi-PB historicals → DMS for CDC.
* **Curation**: Glue/EMR Serverless to standardize + compact + tag.
* **Catalog/Govern**: Glue Data Catalog; LF-tags for PII and domains.
* **Query**: Athena (Iceberg), partition projection for wide partitions.
* **Search**: OpenSearch Serverless collection for discovery.
* **ML**: EventBridge Scheduler → Step Functions → Athena/Glue/SageMaker.
* **FinOps**: Storage Lens dashboards; tag-driven lifecycle; Intelligent-Tiering.

---

## References (handy links)

* DMS to S3 (Parquet): [docs](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html) · [how-to](https://repost.aws/knowledge-center/dms-s3-parquet-format)
* S3 object tagging & lifecycle filters: [tagging](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-tagging.html) · [filters](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-filters.html)
* S3 Intelligent-Tiering: [overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html) · [using](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering.html)
* Lake Formation LF-tags: [TBAC](https://docs.aws.amazon.com/lake-formation/latest/dg/tag-based-access-control.html) · [create tags](https://docs.aws.amazon.com/lake-formation/latest/dg/TBAC-creating-tags.html)
* Athena + Iceberg: [Iceberg in Athena](https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg.html) · [Prescriptive guide](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/getting-started.html)
* Partition projection: [guide](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html) · [types](https://docs.aws.amazon.com/athena/latest/ug/partition-projection-supported-types.html)
* OpenSearch Serverless: [overview](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html) · [API](https://docs.aws.amazon.com/opensearch-service/latest/ServerlessAPIReference/Welcome.html)
* EventBridge Scheduler: [what is](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html) · [CDK](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_scheduler/README.html)
* Step Functions integrations: [catalog](https://docs.aws.amazon.com/step-functions/latest/dg/integrate-services.html) · [Athena](https://docs.aws.amazon.com/step-functions/latest/dg/connect-athena.html) · [SageMaker](https://docs.aws.amazon.com/step-functions/latest/dg/connect-sagemaker.html)
* S3 Storage Lens: [user guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage_lens.html)
* DB-Engines: [ranking](https://db-engines.com/en/ranking)

---

### Copy/paste guidance for Medium

* Paste as-is into the Medium editor.
* Medium honors fenced code blocks (`ts, `json, `python, `sql, \`\`\`js).
* Links are already embedded and will be preserved.
* Add a cover image (optional) and tags like **AWS**, **Data Engineering**, **Serverless**, **S3**, **Athena**, **Lake Formation**, **SageMaker**, **OpenSearch**.

If you want, I can also package this as a **CDK starter repo** (buckets + lifecycle + LF-tags + DMS helpers + Step Functions + Scheduler + Lambda indexer) so readers can deploy and follow along.
