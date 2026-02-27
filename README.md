# DynamoDB Suffix Sharding Demo

A practical demonstration of the suffix sharding pattern in DynamoDB to handle high-traffic scenarios like university course registrations.

## What is Suffix Sharding?

Suffix sharding is a technique to distribute write traffic across multiple partition keys by appending a random shard identifier to the partition key. This prevents hot partitions and allows DynamoDB to scale horizontally during high-traffic events.

## The Problem

Without sharding, all students registering for "CS301" would write to the same partition key (`COURSE#CS301`), creating a hot partition that limits throughput to ~1000 writes/second per partition.

## The Solution

This demo distributes writes across 10 shards by appending a random suffix (1-10) to the partition key:
- `COURSE#CS301_1`
- `COURSE#CS301_2`
- `COURSE#CS301_3`
- ... and so on

This allows the system to handle 10x the write throughput during registration rushes.

## Key Schema

- **Partition Key (PK)**: `COURSE#{course_code}_{shard_id}`
- **Sort Key (SK)**: `{status}#{student_id}#{timestamp}`

## Prerequisites

- Python 3.x
- AWS account with DynamoDB access
- Boto3 library
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)

## Installation

```bash
pip install boto3
```

## Configuration

Ensure your AWS credentials are configured:

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## Usage

Run the demo:

```bash
python suffix_sharding_demo.py
```

The script will:
1. Create the `UniversityRegistrations` table (if it doesn't exist)
2. Simulate 15 student registrations for CS301
3. Display how writes are distributed across different shards

## Example Output

```
8:00 AM Registration Rush...

Success -> Node: COURSE#CS301_7    | Index: ENROLLED#STUDENT-8842#2026-02-27T08:00:01
Success -> Node: COURSE#CS301_3    | Index: ENROLLED#STUDENT-5621#2026-02-27T08:00:02
Success -> Node: COURSE#CS301_9    | Index: ENROLLED#STUDENT-7234#2026-02-27T08:00:03
...
```

## Querying Sharded Data

To retrieve all registrations for a course, you'll need to query all shards:

```python
TOTAL_SHARDS = 10
all_registrations = []

for shard_id in range(1, TOTAL_SHARDS + 1):
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': f'COURSE#CS301_{shard_id}'
        }
    )
    all_registrations.extend(response['Items'])
```

## Trade-offs

**Pros:**
- Handles high write throughput
- Prevents hot partitions
- Simple to implement

**Cons:**
- Queries require scanning all shards
- Slightly more complex read logic
- Need to choose appropriate shard count

## Cleanup

To delete the demo table:

```bash
aws dynamodb delete-table --table-name UniversityRegistrations
```