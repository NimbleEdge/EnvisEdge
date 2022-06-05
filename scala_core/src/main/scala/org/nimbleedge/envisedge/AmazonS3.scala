package org.nimbledge.recoedge


import com.typesafe.config.{Config, ConfigFactory}

import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.services.s3.AmazonS3Client
import com.amazonaws.services.s3.model.{ObjectMetadata, PutObjectRequest, GetObjectRequest}
import java.io.File

object AmazonS3Communicator {
    val applicationConf: Config = ConfigFactory.load()

    val credentials = new BasicAWSCredentials(applicationConf.getString("s3.aws_access_key"), applicationConf.getString("s3.aws_secret_access_key"))
    val amazonS3Client = new AmazonS3Client(credentials)
    
    def upload(bucket: String, filePath: String, filename: String): Boolean = {

        /*
            bucket: Name of S3 bucket in which to upload the file
            filePath: Local Path to file to be uploaded
            filename: path in S3 bucket to the uploaded file
        */


        try {
            val fileToUpload = new File(filePath)
            amazonS3Client.putObject(bucket, filename, fileToUpload); true
        } catch {
            case ex: Exception => println(ex.getMessage()); false
        }
    }

    def delete(bucket: String, fileKeyName: String): Boolean = {

        try {
            amazonS3Client.deleteObject(bucket, fileKeyName); true
        } catch {
            case ex: Exception => println(ex.getMessage()); false
        }
    }

    def download(bucket: String, fileKeyName: String): String = {
        
        try {
            //val data = amazonS3Client.getObjectMetadata(bucket, fileKeyName)
            val splitPath = fileKeyName.split("/")

            val filePath = applicationConf.getString("s3.save_location") + "d-" + splitPath.last
            
            amazonS3Client.getObject(new GetObjectRequest(bucket, fileKeyName), new File(filePath))
            
            return filePath
        } catch {
            case ex: Exception => println(ex.getMessage()); "Failed"
        }
    }
}