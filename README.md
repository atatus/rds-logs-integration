# Export-RDS-Logs-S3-to-Atatus

1. Create an S3 Bucket (To Store CloudWatch Logs)

    * Navigate to the Amazon S3 Dashboard.
    * Click on "Create bucket."
    * Once the bucket is created, open it and go to the `Permissions` tab.
    * Grant CloudWatch write access to the bucket by setting up a `bucket policy`.
    * Click on the `Edit` button for `Bucket Policy` and paste the following JSON policy

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
    * Finally, Choose `Save Changes`.

2. Create IAM Role (To be used for Lambda automation)

    * Navigate to your AWS IAM Dashboard.
    * Switch to the `Roles` tab and click on the `Create role` button.
    * Under Select type of trusted entity, choose `AWS service` and under `Use case`, select `Lambda` and click on Next.
    * Search for `AmazonS3FullAccess`, `CloudWatchLogsFullAccess`, and `CloudWatchEventsFullAccess` policies, and select each of them.
    * Set the Role Name to `Export-RDS-CloudWatch-To-S3-Lambda-Role` and click on `Create role`.


3. Lambda (Function to automate CloudWatch Logs export to S3)

    * Navigate to the AWS Lambda Dashboard.
    * Click on the `Functions` tab and then click `Create function`.
    * Choose `Author from Scratch`.
    * Set the Function name to `Export-RDS-CloudWatch-Logs-To-S3`.
    * Under `Runtime,` select `Python 3.x.`
    * Under `Permissions,` choose `Use an existing role` and select the IAM role created in the previous step(Export-RDS-CloudWatch-To-S3-Lambda-Role).
    * Click on `Create Function` and go to the Code view. Paste the contents of the script file `cw-logs-to-s3.py` into the code editor.
    * Set the `scrap_interval` time in minutes within the script.
    * Then `Deploy` the function.
    * In the `Configuration` tab, select `General Configuration` and click the `Edit` button to change the timeout to `10 minutes`.
    * Save the configuration.


4. Set automation to run this lambda function

    * Go to your `CloudWatch dashboard`.
    * Go to the `Events ⇒ Rules`.
    * Click on `Create Rule`: set rule name `lambda-exec-rule`.
    * Under Rule type, select `Schedule`. Then click `continue to create rule`.
    * Under Schedule pattern, select `A schedule that runs at a regular rate, such as every 10 minutes.` Set the rate expression previously you mention in above script. Then click Next.
    * Choose target type as `AWS service`. Under Target, select Lambda Function.
    * Under Function, select the function we have created in the previous step `Export-RDS-CloudWatch-Logs-To-S3`
    * Finally, Choose Review and create.

5. Adding dependency module in Layers

    To utilize Python's requests module in a Lambda function, you must add it as a layer. Follow these steps:

    * follow below steps to create dependencies zip file in your local machine:

    ```bash
      mkdir python
      cd python
      pip install --target . requests
      zip -r dependencies.zip ../python
    ```

    * Upload your zip file:

      - Navigate to `AWS Lambda > Additional Resources > Layers`.
      - Click on `Create Layer`.
      - Under `Name` section enter your layer name.
      - Choose `Upload a .zip file` and upload your `dependencies.zip` file.
      - Select compatible architecture and runtimes.
      - Click the `Create` button.

6. Lambda (Function to automate export S3 Logs to Atatus)

    * Switch to AWS Lambda Dashboard.
    * Click on the Functions and then click on the Create function button.
    * Keep `Author for Scratch` selected.
    * Set Function name: `Export-S3-Logs-To-Atatus`
    * Under `Runtime`, select Python 3.x.
    * Click on `Create Function` and navigate to the Code view. Next, copy the script file `s3-logs-to-atatus.py` and paste it into the code base.
    * Then `Deploy` the function.

7. Add permissions for Lambda function(Export-S3-Logs-To-Atatus) role

    * Go to function `Configurations` and select `Permissions` from the left sidebar.
    * Click on the `Role name link`,  it will take us to AWS IAM page.
    * click on the `Add permissions` button and select `Attach policies` from the drop down list.
    * Search for `AmazonS3FullAccess`, `AmazonS3ObjectLambdaExecutionRolePolicy`, `AmazonS3OutpostsFullAccess`, and `AmazonS3ReadOnlyAccess` policies, and select each of them.
    * Click the `Add Permission` button.

8. Adding triggers(S3 Bucket) in Lambda function

    * Navigate to `AWS Lambda` function (Export-S3-Logs-To-Atatus)
    * Click on the `+ Add trigger` button from the Lambda console.
    * Select `s3` source under `Trigger configuration`.
    * Select your `Bucket Name`.
    * Under `Event Type`. Choose `All object create events`.
    * Check acknowledge and click on `Add` button.

9. Add dependency module to your Lambda function

    * Navigate to your Lambda function(Export-S3-Logs-To-Atatus).
    * Locate the `Layers` section under `Code` tab.
    * Click the `Add a layer` button.
    * Select `Custom layers`, choose your custom layer and version from the drop-down menu.
    * Click the `Add` button.

10. Now you will get logs into Atatus Dashboard
