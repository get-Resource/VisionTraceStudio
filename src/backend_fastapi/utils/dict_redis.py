import redis
import json
import time

class RedisDict:
    def __init__(self, host='localhost', port=6379, db=0,password="/6tnxR98p4Xzmd/t5dhwIS8a1q1H8I+js2278cZta01SZRcyPGB4WVmy6oo7+66ubovdo9hS6WBpHR1Y", max_retries=3, retry_delay=1):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._connect()

    def _connect(self):
        self.conn = redis.StrictRedis(host=self.host, port=self.port,password=self.password, db=self.db)

    def _reconnect(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self._connect()
                return
            except redis.ConnectionError:
                retries += 1
                time.sleep(self.retry_delay)
        raise redis.ConnectionError("Failed to reconnect to Redis server")

    def _execute_command(self, command, *args, **kwargs):
        try:
            return command(*args, **kwargs)
        except redis.ConnectionError:
            self._reconnect()
            return command(*args, **kwargs)

    def __getitem__(self, key):
        value = self._execute_command(self.conn.get, key)
        if value:
            return json.loads(value)
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        print(key, value)
        existing_value = self._execute_command(self.conn.get, key)
        if existing_value:
            existing_dict = json.loads(existing_value)
            nested_keys = key.split('.')
            last_key = nested_keys[-1]
            nested_dict = existing_dict
            for nested_key in nested_keys[:-1]:
                nested_dict = nested_dict.setdefault(nested_key, {})
            nested_dict[last_key] = value
            value = existing_dict
        self._execute_command(self.conn.set, key, json.dumps(value))

    def __delitem__(self, key):
        self._execute_command(self.conn.delete, key)

    def keys(self):
        return [key.decode() for key in self._execute_command(self.conn.keys)]

    def values(self):
        return [json.loads(value) for value in self._execute_command(self.conn.mget, self.keys())]

    def items(self):
        return [(key, json.loads(self._execute_command(self.conn.get, key))) for key in self.keys()]

    def clear(self):
        self._execute_command(self.conn.flushdb)

    def __repr__(self):
        return str(self.items())
    
    import json
import redis
from observables import ObservableDict

class RedisDict(ObservableDict):
    def __init__(self, host='localhost', port=6379, db=0):
        super().__init__()
        self.redis_conn = None
        self.host = host
        self.port = port
        self.db = db
        self.connect()

    def connect(self):
        self.redis_conn = redis.Redis(host=self.host, port=self.port, db=self.db)
        self.redis_conn.ping()  # Test connection
        self.load_data()  # Load initial data from Redis

    def load_data(self):
        keys = self.redis_conn.keys()
        for key in keys:
            value = self.redis_conn.get(key)
            self[key] = json.loads(value)

    def save_data(self):
        for key, value in self.items():
            self.redis_conn.set(key, json.dumps(value))

    def reconnect(self):
        self.redis_conn = None
        self.connect()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save_data()

    def __delitem__(self, key):
        super().__delitem__(key)
        self.redis_conn.delete(key)

    def observe(self, observer):
        super().observe(observer)
        observer.set_parent(self)

    def on_disconnect(self):
        # Your custom logic for handling disconnection
        pass

    def on_reconnect(self):
        # Your custom logic for handling reconnection
        pass

    def ping(self):
        try:
            self.redis_conn.ping()
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            self.on_disconnect()
            self.reconnect()
            self.on_reconnect()

# Example usage:
redis_dict = RedisDict()

class MyObserver:
    def update(self, changes):
        print("Changes:", changes)

observer = MyObserver()
redis_dict.observe(observer)

# Modify the dictionary
redis_dict['key'] = 'value'



# 示例用法
if __name__ == "__main__":
    redis_dict = RedisDict()
    redis_dict['nested_dict'] = {'key': 'value'}
    print(redis_dict['nested_dict'])

    # 修改嵌套字典中的值
    redis_dict['nested_dict']['key'] = 'new_value'

    print(redis_dict['nested_dict'])
