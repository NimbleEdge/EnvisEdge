package org.nimbleedge.envisedge

import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.services.s3.AmazonS3Client
import com.amazonaws.services.s3.model.{ObjectMetadata, PutObjectRequest, GetObjectRequest}
import java.io.File
import com.amazonaws.services.s3.model.PresignedUrlDownloadRequest
import com.amazonaws.services.s3.model.ListObjectsRequest
import collection.JavaConverters._

object AmazonS3Communicator {
    val s3Config = ConfigManager.staticConfig.getConfig("s3")
    val credentials = new BasicAWSCredentials(s3Config.getString("aws_access_key"), s3Config.getString("aws_secret_access_key"))
    val amazonS3Client = new AmazonS3Client(credentials)
    println("S3 Client Init...")

    def upload(bucket: String, filePath: String, filename: String): Boolean = {
        
        /*
        filePath : local path of file to upload
        filename : path of uploaded in S3
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

            val filePath = s3Config.getString("save_location") + "d-" + splitPath.last
            
            amazonS3Client.getObject(new GetObjectRequest(bucket, fileKeyName), new File(filePath))
            
            return filePath
            
        } catch {
            case ex: Exception => println(ex.getMessage()); "Failed"
        }
    }

    def createEmptyDir(bucket: String, dirName: String) : Boolean = {
        /*
            dirName should end in '/'
        */

        try {
            amazonS3Client.putObject(bucket, dirName, ""); true

        } catch {
            case ex: Exception => println(ex.printStackTrace()); false
        }

    }


    def listAllFiles(bucket: String, dir:String): Array[String] = {

        try {
            var objSummary = amazonS3Client.listObjects(bucket, dir).getObjectSummaries().asScala
            var keys  = new Array[String](objSummary.length-1)
            var i = 0
            for (obj <- objSummary) {
                var filename = obj.getKey().replace(dir, "")
                if (filename != "") {
                    keys(i) = filename
                    i = i+1
                }

            }
            return keys
        } catch {
            case ex: Exception => println(ex.printStackTrace()); null
        }
        
    }

    def emptyDir(bucket:String, dirName: String) : Boolean = {
        try {
            var files: Array[String] = listAllFiles(bucket, dirName)
            for (file <- files) {
                delete(bucket, dirName + file)
            }
            return true  
        } catch {
            case ex:Exception => println(ex.printStackTrace()); false
        }
    }

    def checkFileExists(bucket: String, fileKey: String): Boolean = {

        try {
            amazonS3Client.getObject(bucket, fileKey); true
        } catch {
            case ex: Exception => println(ex.printStackTrace()); false
        }
    }

}