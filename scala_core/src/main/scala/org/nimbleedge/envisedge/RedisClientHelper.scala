package org.nimbleedge.envisedge

import com.redis._
import scala.collection.mutable.ListBuffer

object RedisClientHelper {

    def initConnection(host: String = ConfigManager.DEFAULT_REDIS_HOST, port: Int = ConfigManager.DEFAULT_REDIS_PORT) = {
        client = new RedisClient(host, port)
        client.flushdb
        println("Connection established to " + host + ":" + port)
    }

    def set(key: String, value: String) = {
        client.set(key, value)
    }

    def get(key: String) : Option[String] = {
        client.get(key)
    }

    def lpush(key: String, value: String) = {
        client.lpush(key, value)
    }

    def rpush(key: String, value: String) = {
        client.rpush(key, value)
    }

    def getList(key: String) : Option[List[Option[String]]] = {
        client.lrange(key, 0, -1)
    }

    def llen(key: String) : Option[Long] = {
        client.llen(key)
    }

    def hmset(hash: String, map: Map[String, Any]) = {
        client.hmset(hash, map)
    }

    def hmget(hash: String, fields: String*) : Option[Map[String, String]] = {
        client.hmget[String, String](hash, fields: _*)
    }

    def hset(hash: String, field: String, value: String) = {
        client.hset(hash,field,value)
    }

    def hget(hash: String, field: String) : Option[String] = {
        client.hget[String](hash, field)
    }

    def flushdb() = {
        client.flushdb
    }

    def expire(hash: String, ttl: Int) : Boolean = {
        client.expire(hash, ttl)
    }

    var client : RedisClient = _
}

object RedisClientPoolHelper {

    def initConnection(host: String = ConfigManager.DEFAULT_REDIS_HOST, port: Int = ConfigManager.DEFAULT_REDIS_PORT) = {
        clients = new RedisClientPool(host, port)
        println("Connection established to " + host + ":" + port)
    }

    def hmset(hashes: List[String], map: Map[String, Any]) = {
        clients.withClient {
            client => {
                hashes.foreach { hash =>
                    client.hmset(hash, map)
                }
            }
        }
    }

    def hset(hashes: List[String], field: String, value: String) = {
        clients.withClient {
            client => {
                hashes.foreach { hash =>
                    client.hset(hash,field,value)
                }
            }
        }
    }

    def hget(hashes: List[String], field: String) : List[Option[String]] = {
        var vals = new ListBuffer[Option[String]]()
        clients.withClient {
            client => {
                hashes.foreach { hash =>
                    vals += client.hget[String](hash, field)
                }
            }
        }
        return vals.toList
    }

    var clients : RedisClientPool = _
}

