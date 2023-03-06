# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib


BUCKET_NAME = "sdswiki_contents"

class Backend:

    def __init__(self):
        self.storage_client = storage.Client()
        
    def get_wiki_page(self, name):

        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(name)
        
        with blob.open() as f:
            return f.read()

    #Gets the names of all pages from the content bucket.
    def get_all_page_names(self):
        pages_names_list = []

        storage_client = storage.Client()
        
        blobs = storage_client.list_blobs(BUCKET_NAME)

        # Note: The call returns a response only when the iterator is consumed.
        for blob in blobs:
            pages_names_list.append(blob.name)
        #return the list

    def upload(self, data, destination_blob_name):
        bucket = self.storage_client.bucket('sdswiki_contents')
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(data)
        
        return f"{destination_blob_name} with contents {data} uploaded to sdswiki_contents."

    def sign_up(self, name, password):
        #this assumes that we've saved the different usernames as blobs with the hashed password inside.
        bucket = self.storage_client.bucket('sdsusers_passwords')
        blobs = self.storage_client.list_blobs('sdsusers_passwords')

        for blob in blobs:
            if blob.name == name:
                return f"user {name} already exists in the database. Please sign in." 
                # or I could have it call the sign in method at once?

        blob = bucket.blob(name) 

        with blob.open("w") as user:
            password = password.encode()
            secure_password = hashlib.sha3_256(password).hexdigest()
            user.write(secure_password)

        return f"user {name} successfully created."

    def sign_in(self, username, password):
        bucket = self.storage_client.bucket('sdsusers_passwords')
        blob = bucket.blob(username)
        password = password.encode()
        salty_password = f"{username}{password}"
        hashed = hashlib.sha3_256(salty_password).hexdigest()

        with blob.open("r") as username:
            if hashed == username.read():
                return f"{username} logged in successfully."
            return "Incorrect password entered for {username}"

    def get_image(self, name):
        bucket = self.storage_client.bucket('sdswiki_contents')
        blob = bucket.blob(name)

        with blob.open("rb") as f:
            return f.read()

backend = Backend()

print(backend.get_wiki_page("page_one.txt"))
print(backend.get_all_page_names())