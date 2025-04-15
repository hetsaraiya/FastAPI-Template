"""
Redis connection manager for AgrEazy.

This module provides a Redis connection manager for handling Redis client operations
and connection lifecycle.
"""

import json
import typing
import redis
from functools import wraps
from src.config.manager import settings
from src.utilities.logging.logger import logger

class RedisManager:
    """
    Redis connection manager for handling Redis client operations.
    
    This class manages Redis connections and provides utility methods for
    working with Redis, including connection creation, key management,
    and serialization helpers.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Redis connection manager exists."""
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance
    
    def __init__(self):
        """Initialize the Redis connection manager."""
        # Only set up the client if it doesn't exist yet
        if self._client is None:
            self._setup_redis_client()
    
    def _setup_redis_client(self):
        """Set up the Redis client with configuration from settings."""
        try:
            logger.info(f"Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                decode_responses=settings.REDIS_DECODE_RESPONSES
            )
            # Test the connection
            self._client.ping()
            logger.info(f"Connected to Redis successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self._client = None
    
    @property
    def client(self) -> redis.Redis:
        """
        Get the Redis client instance.
        
        Returns:
            redis.Redis: The Redis client instance.
            
        Raises:
            ConnectionError: If the Redis client is not connected.
        """
        if self._client is None:
            self._setup_redis_client()
            if self._client is None:
                raise ConnectionError("Redis client is not connected")
        return self._client
    
    async def close(self):
        """Close the Redis connection."""
        if self._client:
            logger.info("Closing Redis connection")
            self._client.close()
            self._client = None
    
    def set(self, key: str, value: typing.Any, expiration: int = None) -> bool:
        """
        Set a key-value pair in Redis with optional expiration.
        
        Args:
            key: The key to set.
            value: The value to set.
            expiration: Optional expiration time in seconds.
            
        Returns:
            bool: True if the key was set, False otherwise.
        """
        try:
            # Serialize non-string values to JSON
            if not isinstance(value, (str, bytes)):
                value = json.dumps(value)
                
            # Use default expiration from settings if not specified
            if expiration is None:
                expiration = settings.REDIS_CACHE_EXPIRATION
                
            return self.client.set(key, value, ex=expiration)
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis set error for key '{key}': {str(e)}")
            return False
    
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """
        Get a value from Redis by key.
        
        Args:
            key: The key to get.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The value from Redis, or the default value if the key doesn't exist.
        """
        try:
            value = self.client.get(key)
            if value is None:
                return default
                
            # Try to deserialize from JSON if it looks like JSON
            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
                    
            return value
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis get error for key '{key}': {str(e)}")
            return default
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key: The key to delete.
            
        Returns:
            bool: True if the key was deleted, False otherwise.
        """
        try:
            return bool(self.client.delete(key))
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis delete error for key '{key}': {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key: The key to check.
            
        Returns:
            bool: True if the key exists, False otherwise.
        """
        try:
            return bool(self.client.exists(key))
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis exists error for key '{key}': {str(e)}")
            return False
    
    def flush_all(self) -> bool:
        """
        Flush all keys in the current Redis database.
        WARNING: This will delete all data in the Redis database.
        
        Returns:
            bool: True if the database was flushed, False otherwise.
        """
        try:
            self.client.flushdb()
            return True
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis flushdb error: {str(e)}")
            return False
    
    def set_many(self, mapping: dict, expiration: int = None) -> bool:
        """
        Set multiple key-value pairs in Redis with the same expiration.
        
        Args:
            mapping: A dictionary of key-value pairs to set.
            expiration: Optional expiration time in seconds.
            
        Returns:
            bool: True if all keys were set, False otherwise.
        """
        try:
            # Serialize non-string values to JSON
            serialized_mapping = {}
            for k, v in mapping.items():
                if not isinstance(v, (str, bytes)):
                    serialized_mapping[k] = json.dumps(v)
                else:
                    serialized_mapping[k] = v
                    
            # Set all keys
            pipeline = self.client.pipeline()
            for k, v in serialized_mapping.items():
                if expiration is None:
                    pipeline.set(k, v, ex=settings.REDIS_CACHE_EXPIRATION)
                else:
                    pipeline.set(k, v, ex=expiration)
            pipeline.execute()
            return True
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis set_many error: {str(e)}")
            return False
    
    def get_many(self, keys: list) -> dict:
        """
        Get multiple values from Redis by keys.
        
        Args:
            keys: A list of keys to get.
            
        Returns:
            dict: A dictionary of key-value pairs for keys that exist.
        """
        try:
            pipeline = self.client.pipeline()
            for key in keys:
                pipeline.get(key)
            values = pipeline.execute()
            
            result = {}
            for i, key in enumerate(keys):
                if values[i] is not None:
                    value = values[i]
                    # Try to deserialize from JSON if it looks like JSON
                    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                        try:
                            result[key] = json.loads(value)
                            continue
                        except json.JSONDecodeError:
                            pass
                    result[key] = value
            return result
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis get_many error: {str(e)}")
            return {}
    
    def build_key(self, *parts) -> str:
        """
        Build a Redis key from parts.
        
        Args:
            *parts: Parts to join into a key.
            
        Returns:
            str: The built key.
        """
        return ':'.join(str(p) for p in parts if p)


# Create a singleton instance
redis_manager = RedisManager()