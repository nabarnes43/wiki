# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib

class Backend:

    def __init__(self):
        self.storage_client = storage.Client()
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        pass

    def upload(self, data, destination_blob_name):
        # does this create a new blob if the requested blob does not exist?
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

        blob = bucket.blob(name) # im assuming that this creates a blob with the new name

        with blob.open("w") as user:
            password = password.encode()
            secure_password = hashlib.sha3_256(password).hexdigest()
            user.write(secure_password)

        return f"user {name} successfully created."

    def sign_in(self):
        pass

    def get_image(self):
        pass
