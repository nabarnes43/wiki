# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
import io
from flask import Flask
import base64


class Backend:

    def __init__(self, storage_client = storage.Client()):
        self.storage_client = storage_client
        
    def get_wiki_page(self, name):

        bucket = self.storage_client.bucket("sdswiki_contents")
        blob = bucket.blob(name)
        
        with blob.open() as f:
            return f.read()

        #add error handling


    #Gets the names of all pages from the content bucket.
    def get_all_page_names(self): #does this need to return a value? or pages names list saved as a class variable so i can access it later?
        pages_names_list = []
        
        blobs = self.storage_client.list_blobs("sdswiki_contents")

        # Note: The call returns a response only when the iterator is consumed.
        for blob in blobs:
            pages_names_list.append(blob.name)
        
        return pages_names_list

    def upload(self, data, destination_blob_name):
        blobs = self.storage_client.list_blobs('sdswiki_contents')

        for blob in blobs:
            if destination_blob_name == blob.name:
                return 'Upload failed. You cannot overrite an existing page'

        blob = self.storage_client.blob(destination_blob_name)
        blob.upload_from_string(data)
        
        return f"{destination_blob_name} with contents {data} uploaded to sdswiki_contents."

    def sign_up(self, name, password):
        #this saves the username as a blob with the hashed password inside.
        bucket = self.storage_client.bucket('sdsusers_passwords')
        blobs = self.storage_client.list_blobs('sdsusers_passwords')

        for blob in blobs:
            if blob.name == name:
                return f"user {name} already exists in the database. Please sign in." 

        blob = bucket.blob(name) 
        with blob.open("w") as user:
            salty_password = f"{name}{password}".encode()
            secure_password = hashlib.sha3_256(salty_password).hexdigest()
            user.write(secure_password)

        return f"user {name} successfully created."

    def sign_in(self, username, password):
        bucket = self.storage_client.bucket('sdsusers_passwords')
        blob = bucket.blob(username)
        password = password.encode()
        salty_password = f"{username}{password}".encode()
        hashed = hashlib.sha3_256(salty_password).hexdigest()

        try:        
            with blob.open("r") as username:
                secure_password = username.read()
        except:
            return "Username not found"
        
        if hashed == secure_password:
            return True
        return False


    def get_image(self, name):
        bucket = self.storage_client.bucket('sdsimages')
        blob = bucket.blob(name)

        with blob.open("rb") as f:
            img = f.read()

        return img

