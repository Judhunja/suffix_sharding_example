import boto3
import random
import time
from datetime import datetime

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = 'UniversityRegistrations'


def setup_demo_table():
    """Creates the DynamoDB table if it doesn't already exist."""
    existing_tables = [t.name for t in dynamodb.tables.all()]

    if table_name not in existing_tables:
        print(f"Creating table '{table_name}'...")
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},  # Partition Key
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}  # Sort Key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'  # Serverless, pay-as-you-go billing
        )
        # Wait until the table exists before trying to write to it
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print("Table created successfully!\n")
    else:
        print(
            f"Table '{table_name}' already exists. Proceeding to write data...\n"
        )

    return dynamodb.Table(table_name)


def register_for_class(table, course_code, student_id, status):
    TOTAL_SHARDS = 10
    shard_id = random.randint(1, TOTAL_SHARDS)

    # Example PK: "COURSE#CS301_4"
    partition_key = f"COURSE#{course_code}_{shard_id}"

    # Example SK: "ENROLLED#STUDENT-8842#2026-02-27T08:00:01"
    current_time = datetime.utcnow().isoformat()
    sort_key = f"{status}#{student_id}#{current_time}"

    response = table.put_item(
        Item={
            'PK': partition_key,
            'SK': sort_key,
            'Timestamp': current_time
        }
    )

    print(f"Success -> Node: {partition_key:<18} | Index: {sort_key}")
    return response


if __name__ == "__main__":
    table = setup_demo_table()

    print("8:00 AM Registration Rush...\n")
    for _ in range(15):  # Running 15 registrations
        register_for_class(
            table=table,
            course_code="CS301",
            student_id=f"STUDENT-{random.randint(1000, 9999)}",
            status="ENROLLED"
        )
        time.sleep(0.2)  # To visualize timestamps
