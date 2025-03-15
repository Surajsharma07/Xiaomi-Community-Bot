from pymongo import MongoClient

class Database:
    def __init__(self):
        """
        Initializes the connection to the MongoDB database.
        """
        self.client = MongoClient("mongodb+srv://surajatepichost:i7n6kUEIP3emI0KM@communitybot.adl6v.mongodb.net/?retryWrites=true&w=majority&appName=communitybot")
        self.db = self.client["communitybot"]  # Replace 'communitybot' with your database name if different

    def insert_document(self, collection_name, document):
        """
        Inserts a document into the specified collection.

        Args:
            collection_name (str): The name of the collection.
            document (dict): The document to insert.

        Returns:
            InsertOneResult: The result of the insert operation.
        """
        collection = self.db[collection_name]
        return collection.insert_one(document)

    def find_document(self, collection_name, query):
        """
        Finds a single document in the specified collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to match the document.

        Returns:
            dict: The matched document, or None if no match is found.
        """
        collection = self.db[collection_name]
        return collection.find_one(query)

    def update_document(self, collection_name, query, update_values):
        """
        Updates a document in the specified collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to match the document.
            update_values (dict): The values to update in the document.

        Returns:
            UpdateResult: The result of the update operation.
        """
        collection = self.db[collection_name]
        return collection.update_one(query, {"$set": update_values})

    def delete_document(self, collection_name, query):
        """
        Deletes a document from the specified collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to match the document.

        Returns:
            DeleteResult: The result of the delete operation.
        """
        collection = self.db[collection_name]
        return collection.delete_one(query)
