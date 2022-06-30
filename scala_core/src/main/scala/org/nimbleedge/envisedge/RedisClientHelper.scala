package org.nimbleedge.envisedge

import com.redis._

object RedisClientHelper {

    def initConnection(host: String = DEFAULT_REDIS_HOST, port: Int = DEFAULT_REDIS_PORT) = {
        clients = new RedisClientPool(host, port)
        clients.withClient {
            client => client.flushdb
        }
        println("Connection established to " + host + ":" + port)
    }

    def set(key: String, value: String) = {
        clients.withClient {
            client => client.set(key, value)
        }
    }

    def get(key: String) : Option[String] = {
        clients.withClient {
            client => client.get(key)
        }
    }

    def lpush(key: String, value: String) = {
        clients.withClient {
            client => client.lpush(key, value)
        }
    }

    def rpush(key: String, value: String) = {
        clients.withClient {
            client => client.rpush(key, value)
        }
    }

    def getList(key: String) : Option[List[Option[String]]] = {
        clients.withClient {
            client => client.lrange(key, 0, -1)
        }
    }

    def llen(key: String) : Option[Long] = {
        clients.withClient {
            client => client.llen(key)
        }
    }

    def hmset(hash: String, map: Map[String, Any]) = {
        clients.withClient {
            client => client.hmset(hash, map)
        }
    }

    def hmget(hash: String, fields: String*) : Option[Map[String, String]] = {
        clients.withClient {
            client => client.hmget[String, String](hash, fields: _*)
        }
    }

    def hset(hash: String, field: String, value: String) = {
        clients.withClient {
            client => client.hset(hash,field,value)
        }
    }

    def hget(hash: String, field: String) : Option[String] = {
        clients.withClient {
            client => client.hget[String](hash, field)
        }
    }

    def flushdb() = {
        clients.withClient {
            client => client.flushdb
        }
    }

    def expire(hash: String, ttl: Int) : Boolean = {
        clients.withClient {
            client => client.expire(hash, ttl)
        }
    }

    var clients : RedisClientPool = _

    // TODO configure these in the FLSystemManager
    val DEFAULT_REDIS_HOST = "localhost"
    val DEFAULT_REDIS_PORT = 6379
}

