from pymongo import MongoClient


class Mongo:
    def __init__(self, index="content", host="localhost", port=27017):
        self.index = index
        self.client = MongoClient(host, port)
        self.db = self.client['university_db']
        self.collection = self.db['university']

    def create(self, university_data):
        self.collection.insert_one(university_data)

    def read(self, tag_department):
        dep = [_ for _ in
               self.collection.find(
                   {f'mirea.departaments.{tag_department}': {'$exists': True}})]
        return dep[0]

    def update(self, tag_department, value_department):
        query = {f'mirea.departaments.{tag_department}': {'$exists': True}}
        update_data = {'$set': {tag_department: value_department}}

        self.collection.update_one(query, update_data)

    def delete(self, tag_department):
        query = {f'mirea.departaments.{tag_department}': {'$exists': True}}

        self.collection.delete_one(query)


if __name__ == "__main__":
    mongo = Mongo()
    mongo.create(university_data={
        'mirea': {
            'departaments': {
                'КБ-1': {
                    '1': 'Институт кибербезопасности и цифровых технологий',
                    '2': 'Институт информационных технологий',
                }
            }
        }
    })
    mongo.read('КБ-1')
    mongo.update('КБ-1', '123123')
    mongo.delete('КБ-1')
