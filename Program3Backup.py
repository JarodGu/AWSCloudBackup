# Jarod Guerrero
# CSS 436 A
# 11/1/2019
# Program 3 - AWS Backup Client
#
# Creates a backup of either the current working or inputted directories
# to a user's AWS S3 bucket. Uses credentials stored in the AWS CLI configuration.
# Creates a bucket with the current timestamp if not provided or set to "default"
# If an existing bucket name is provided, it will only replace files that have been modified
# based on their size in Bytes.

from datetime import datetime
import sys # command line arguments
import os # directory and file path checking
import boto3 # AWS S3 and CLI
import posixpath
import py_compile
from pathlib import Path

rootDir = os.getcwd() # Current executing directory
default = True # Tracks status of 1st bucket name parameter
bucketName = "p3backup-" + datetime.now().strftime("%m-%d-%y-%H%M%S")

if len(sys.argv) > 1:
    # No inputted argument. Default to execution directory
    # Also update bucket name if not set to default
    if sys.argv[1] != "default":
        default = False
        bucketName = str(sys.argv[1])
    if len(sys.argv) > 2:
        rootDir = " ".join(sys.argv[2:])

# Handle invalid directories
def Invalid_Directory_Handler(exception_instance):
    print("Error: Invalid directory encountered")
    quit()

# Test for invalid starting directory
for root, dirs, files in os.walk(rootDir, onerror=Invalid_Directory_Handler):
    break

s3 = boto3.resource("s3")
bucketList = s3.buckets.all()
bucketFound = False;

if not default:
    for bucket in bucketList:
        # Check if bucket already exists. Special case where we want to
        # only update files that have changed
        if bucket.name == bucketName: # Bucket found
            bucketFound = True;
            # Create dictionary containing each S3 object path(key) and their size in Bytes
            SizeDictionary = {}
            for key in bucket.objects.all():
                # add to dictionary
                SizeDictionary[key.key] = key.size

            # Recursively iterate through the file system with os.walk()
            # Full path contains the full OS-specific path including drive letter
            # File/Directory path is the full path without drive letter
            # Temp is the POSIX path conversion that uses forward slash instead of backslash
            #       to allow the S3 cloud to simulate directories
            for root, dirs, files in os.walk(rootDir, onerror=Invalid_Directory_Handler): # Recursively navigate file path
                for name in files:
                    fullPath = os.path.join(root, name)
                    filePath = Path(os.path.splitdrive(fullPath)[1])
                    # print("Windows: ", filePath)
                    temp = filePath.as_posix()
                    # print("POSIX: ", temp)
                    if temp[0] == '/':  # Remove forward slash from start if found. Avoids trouble with cutting off first char
                        temp = temp[1:]

                    # if the file being uploaded is different in size (B),
                    #   then replace the file in the bucket 
                    if SizeDictionary[temp] != os.path.getsize(fullPath):
                        # File exists in cloud but current version is different
                        s3.Object(bucketName, temp).put(Body=open(filePath, "rb"))

                for name in dirs:
                    fullPath = os.path.join(root, name)
                    directoryPath = Path(os.path.splitdrive(fullPath)[1])
                    # print("Windows: ", directoryPath)
                    temp = directoryPath.as_posix()
                    # print("POSIX: ", temp)
                    if temp[0] == '/':
                        temp = temp[1:]
                    # print("current vals: ", SizeDictionary.get(temp[1:]), " size(B): ", os.path.getsize(fullPath))
                    if (temp + '/') not in SizeDictionary:    
                        # Upload a 0KB empty object as the directory
                        s3.Object(bucketName, temp[1:]+'/' ).put(Body = '')

if not bucketFound:
    print("Creating Bucket: ", bucketName)
    s3.create_bucket(Bucket = bucketName, CreateBucketConfiguration={"LocationConstraint":"us-west-2"})
    for root, dirs, files in os.walk(rootDir, onerror=Invalid_Directory_Handler):
        for name in files:
            fullPath = os.path.join(root, name)
            filePath = Path(os.path.splitdrive(fullPath)[1])
            # print("Windows: ", filePath)
            temp = filePath.as_posix()
            # print("POSIX: ", temp)
            if temp[0] == '/':
                temp = temp[1:]
            s3.Object(bucketName, temp).put(Body=open(filePath, "rb"))

        for name in dirs:
            fullPath = os.path.join(root, name)
            directoryPath = Path(os.path.splitdrive(fullPath)[1])
            # print("Windows: ", directoryPath)
            temp = directoryPath.as_posix()
            # print("POSIX: ", temp)
            if temp[0] == '/':
                temp = temp[1:]
            # Upload a 0KB empty object to the directory
            s3.Object(bucketName, temp + '/' ).put(Body = '')
     
print("Done uploading.")

# Brainstorming Notes:
# Buckets are a single level container and the illusion of directories
# are given by the name of each file having \dir1\dir2\cat.gif
# In order to create a backup program, I need to have a way to traverse
# all files in a directory. I wonder if it needs recursion. Yes it does.
# Should it replace files or delete ones that are moved?
# 
# The flow is like this:
# for each file in the directory and its subdirectories
#   check if one exists in the bucket
#       if it doesnt, then add it to the bucket with a recursively generated name
#           ie. \dir1\dir2\cat.gif
#       if it DOES exist, check the checksum or date modified
#           replace the file in the bucket

# How do I do recursion in python?

# The function should take two arguments:
#   An absolute root directory path
#   A bucket name

# The function goes through the existing machine's AwsCLI config
# to get the bucket and list within the bucket

# Important NOTE:
# The Amazon S3 console treats all objects that have a forward slash ("/") character as the last 
# (trailing) character in the key name as a folder, for example examplekeyname/. 
# You can't upload an object that has a key name with a trailing "/" character 
# using the Amazon S3 console. However, you can upload objects that are named with a 
# trailing "/" with the Amazon S3 API by using the AWS CLI, the AWS SDKs, or REST API.


