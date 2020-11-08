# AWS Cloud Backup Program
## Design
Program3Backup is a backup client built in Python using the AWS boto3 SDK. It uses the existing programmatic access settings found in the AWS CLI configuration to update or create a bucket with a provided directory’s structure and contents. The default bucket name is formatted as ```p3backup-month-day-year-HHMMSS```. For example, ```p3backup-11-01-19-173930```. This means each generated bucket will almost always be unique and carries at-a-glance information about when it took place.

In order to save bandwidth while updating an existing bucket, I needed a way to upload only files that have been modified. Objects in an S3 bucket contain a ```last modified``` parameter. Initially, I thought comparing that with the actual file’s date modified would be a good approach. After testing, I decided to switch my criteria of modification to ```file size```. Adding a tag to each object would have been another possible option. File size is recorded as an integer in bytes and is the same between files if they have not been modified. 

## Execution
The program is run through the included Program3Backup.py script or with the Program3Backup.pyc bytecode. It takes two parameters: 
```
bucket name, root directory
```
Both parameters can be left blank to back up the current working directory using a generated bucket name. The bucket name parameter can be set to backup to specified bucket. If the bucket already exists, then only new or changed files will be uploaded.

```NOTE: If you want to use a generated bucket name AND a specified root directory, set the bucket name parameter to “default” so the argument parser can handle directory paths with spaces.```

## Testing
The program was tested using my AWS educate S3 account. I’m allowed 100 buckets with an adequate number of uploads for small files. I used the following directory structure to test my program. Directory 2 is an empty directory with spaces in the name. aaFile.txt was a text file with separate copies modified at different timestamps. It was at this stage where I noticed something about the last modified parameter for the uploaded object. I expected it to keep the Date modified metadata, but instead, AWS’s Last modified only reflected changes in the cloud. This meant that matching the two dates was not a good approach. I pivoted my criteria to use file size in bytes since it was a metadata that would be retained when uploaded. One point that I didn’t test is compatibility with non-Windows machines. I’m confident it will work on Linux and Mac systems because the Python path object is based on the current OS.
