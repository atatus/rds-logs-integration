# Export-RDS-Logs-S3-to-Atatus

1. Create an S3 Bucket (To Store CloudWatch Audit Logs)

  * Go to Amazon S3 Dashboard.
  * Create a new Bucket.
  * Once you have created a bucket, open it and navigate to the Permissions tab.
  * We will need to allow CloudWatch to put objects to the bucket (Write Access)
  * Click on Edit button for Bucket policy then paste the below policy json.

  ```json
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Principal": {
                  "Service": "logs.<YOUR_REGION>.amazonaws.com"
              },
              "Action": "s3:GetBucketAcl",
              "Resource": "arn:aws:s3:::<YOUR_BUCKET_NAME>"
          },
          {
              "Effect": "Allow",
              "Principal": {
                  "Service": "logs.<YOUR_REGION>.amazonaws.com"
              },
              "Action": "s3:PutObject",
              "Resource": "arn:aws:s3:::<YOUR_BUCKET_NAME>/*",
              "Condition": {
                  "StringEquals": {
                      "s3:x-amz-acl": "bucket-owner-full-control"
                  }
              }
          }
      ]
  }
  ```

2. Create IAM Role (We will use this for Lambda automation)

  * Open your AWS IAM Dashboard.
  * Switch to the Roles and click on the `Create Role` button.
  * Under `Use case`, select Lambda and click on Next.
  * Search for `AmazonS3FullAccess` and select it.
  * Search for `CloudWatchLogsFullAccess` and select it.
  * Search for `CloudWatchEventsFullAccess` and select it.
  * Set Role Name: `Export-RDS-CloudWatch-To-S3-Lambda` and click on Create role.


3. Lambda (Function to automate CloudWatch Logs export to S3)

  * Switch to AWS Lambda Dashboard.
  * Click on the Functions and then click on the Create function button.
  * Keep `Author for Scratch` selected.
  * Set `Function name`: `Export-RDS-CloudWatch-Logs-To-S3`
  * Under `Runtime`, select Python 3.x.
  * Under `Permissions`, select `Use an existing role` and select the IAM role that we created in the previous step.
  * Click on `Create Function` and navigate to the Code view. Next, copy the script file `cw-logs-to-s3.py` and paste it into the code base.
  * You need to set `scrap_interval` time in minutes in that script
  * Save the function.


4. set automation to run this lambda function

  * Go to your `CloudWatch dashboard`.
  * Go to the `Events ⇒ Rules`.
  * Click on `Create Rule`.
  * Under Rule type, select `Schedule`. Then click `continue to create rule`.
  * Under Schedule pattern, select `A schedule that runs at a regular rate, such as every 10 minutes.` Set the rate expression previously you mention in above steps. Then click Next.
  * Choose target type as `AWS service`. Under Target, select Lambda Function.
  * Under Function, select the function we have created in the previous step `Export-RDS-CloudWatch-Logs-To-S3`
  * Finally, Choose Review and create.

5. Lambda (Function to automate S3 Logs export Atatus)

  * Switch to AWS Lambda Dashboard.
  * Click on the Functions and then click on the Create function button.
  * Keep `Author for Scratch` selected.
  * Set Function name: `Export-S3-Logs-To-Atatus`
  * Under `Runtime`, select Python 3.x.
  * Click on `Create Function` and navigate to the Code view. Next, copy the script file `s3-logs-to-atatus.py` and paste it into the code base.
  * Then you should modify already you choose rate expression
  * Save the function.


6. Configuring Policies for Lambda function

  * Go to `Configurations` and select `Permissions` from the left sidebar.
  * Click on the Execution Role name link just under Role name,  it will take us to AWS IAM page.
  * click on the `Add permissions` button and select `Attach policies` from the drop down list.
  * Search for `AmazonS3FullAccess` and select it.
  * Search for `AmazonS3ObjectLambdaExecutionRolePolicy` and select it.
  * Search for `AmazonS3OutpostsFullAccess` and select it.
  * Search for `AmazonS3ReadOnlyAccess` and select it.

7. Adding triggers(S3 Bucket) in lambda function (Export-S3-Logs-To-Atatus)

  * Click on the `+ Add trigger` button from the Lambda console.
  * Under `Bucket` select `Bucket Name`.
  * Under `Event Type`. Choose `All object create events`.
  * Click on `Add` button.

8. Adding Layers in lambda function (Export-S3-Logs-To-Atatus)

  To utilize Python's requests module in a Lambda function, you must add it as a layer. Follow these steps:

  * Create a directory for your dependencies:

  ```bash
    mkdir python
    cd python
    pip install --target . requests
    zip -r dependencies.zip ../python
  ```

  * Upload your zip file:

    - Navigate to `AWS Lambda > Additional Resources > Layers`.
    - Click on `Create Layer`.
    - Under `Name, enter your layer name.
    - Choose `Upload a .zip file` and upload your `dependencies.zip` file.
    - Select compatible architecture and runtimes.
    - Click the `Create` button.

  * Add the layer to your Lambda function:

    - Navigate to your Lambda function.
    - Locate the `Layers` section.
    - Click the `Add a layer` button.
    - Select `Custom layers` from the checkbox.
    - Choose your custom layer and version from the drop-down menu.
    - Click the `Add` button.

9. Now you will get logs into Atatus Dashboard
