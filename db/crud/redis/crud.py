import redis


class Redis:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    def create(self, key, value):
        self.redis_client.set(key, value)
        print(f"Запись создана: {key} - {value}")

    def read(self, key):
        value = self.redis_client.get(key)
        if value is not None:
            print(f"Значение {key}: {value}")
        else:
            print(f"Запись {key} не найдена")

    def update(self, key, new_value):
        if self.redis_client.exists(key):
            self.redis_client.set(key, new_value)
            print(f"Запись обновлена: {key} - {new_value}")
        else:
            print(f"Запись {key} не найдена")

    def delete(self, key):
        if self.redis_client.exists(key):
            self.redis_client.delete(key)
            print(f"Запись удалена: {key}")
        else:
            print(f"Запись {key} не найдена")


if __name__ == "__main__":
    redis_crud = Redis()
    redis_crud.create("student:1", "Романов Дмитрий")
    redis_crud.read("student:1")
    redis_crud.update("student:1", "Дмитрий Романов")
    redis_crud.read("student:1")
    redis_crud.delete("student:1")
    redis_crud.read("student:1")
