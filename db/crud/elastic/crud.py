from elasticsearch import Elasticsearch


class Elastic:
    def __init__(self, index="content", host="localhost", port=9200):
        self.index = index
        self.es = Elasticsearch(
            [
                {
                    'host': host,
                    'port': port,
                    "scheme": "http"
                }
            ], verify_certs=False
        )

    def create(self, document_id, document_body):
        self.es.index(index=self.index, id=document_id, document=document_body)
        print(f"Документ с ID {document_id} создан")

    def read(self, document_id):
        result = self.es.get(index=self.index, id=document_id)
        print(f"Документ с ID {document_id}: {result['_source']}")

    def update(self, document_id, updated_body):
        self.es.update(index=self.index, id=document_id, body={"doc": updated_body})
        print(f"Документ с ID {document_id} обновлен")

    def delete(self, document_id):
        self.es.delete(index=self.index, id=document_id)
        print(f"Документ с ID {document_id} удален")


if __name__ == "__main__":
    es = Elastic()
    lecture_id = "1"
    document_body = {"title": "Лекция 1", "content": "Описание"}
    es.create(lecture_id, document_body)
    es.read(lecture_id)
    updated_body = {"title": "Лекция 1", "content": "Новое описание"}
    es.update(lecture_id, updated_body)

    es.read(lecture_id)
    es.delete(lecture_id)
