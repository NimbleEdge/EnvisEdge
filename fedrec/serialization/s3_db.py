from abc import ABC, abstractmethod
import os
import yaml
import boto3
import pandas as pd

class AbstractDatabaseManager(ABC):
    

    def __init__(self):

        pass

    
    @abstractmethod
    def download(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractmethod
    def upload(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractmethod
    def update(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractmethod
    def delete(self):
        raise NotImplementedError("Database interface not defined.")





"""
    TODO: Make the whole FL service independent of local system. All the io operations should be done via S3 only.
"""

class S3Interface(AbstractDatabaseManager):

  
    def __init__(self,
                region=None,
                aws_access_key=None,
                aws_secret_access_key=None,
                storage=None
                ):
        
        self.region = region
        self.storage = storage
        self.s3 = boto3.resource(
                service_name='s3',
                region_name=region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_access_key
        )

        self.current_buckets = None
        try:

            self.current_buckets = [bucket.name for bucket in self.s3.buckets.all()]
        
        except Exception as e:
            print(e)
        
        print("Current Buckets: ", self.current_buckets)
        pass



    
    def listAllBuckets(self):
        if self.current_buckets == None:
            raise Exception("Info not available.")

        for b in self.current_buckets:
            print(b)
  


    def download(self, bucket_name: str, file_key: str):
        """

        """
        #condition to check if s3 is connected
        if self.current_buckets == None : 
            raise Exception("Error connecting to database.")
        
        #Extract Group of device and model we need to fetch
        if not bucket_name in self.current_buckets:
            raise Exception("Requested bucket does not exist.")
        
        filePath = self.storage + file_key
        
        self.s3.Bucket(bucket_name).download_file(
            Key=file_key, Filename=filePath
        )

        return filePath



    def upload(self, bucket_name: str, file_path: str, file_key: str):
        if self.current_buckets == None:
            raise Exception("Error connecting to database.")
        

        if not bucket_name in self.current_buckets:
            raise Exception("Requested bucket does not exist.")

        self.s3.Bucket(bucket_name).upload_file(Filename=file_path, Key=file_key)
        #os.remove(file_path) 


  
    def update(self, bucket_name:str, file_path:str, file_key:str):
        if self.current_buckets == None:
            raise Exception("Error connecting to database.")

        self.upload(bucket_name, file_path, file_key)


    def delete(self, bucket_name: str, file_key: str):
        if self.current_buckets == None:
            raise Exception("Error connecting to database.")
        
        if not bucket_name in self.current_buckets:
            raise Exception("Requested bucket does not exist.")

        self.s3.Object(bucket_name, file_key).delete()