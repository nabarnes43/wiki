# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
from google.cloud import exceptions
import hashlib
import io
from flask import Flask


class Backend:

    def __init__(self, storage_client=storage.Client()):
        self.storage_client = storage_client

    def get_wiki_page(self, name):
        """Gets the contents of the specified wiki page.

        Args:
            name: The name of the wiki page.

        Returns:
            The contents of the wiki page.

        Raises:
            exceptions.NotFound: If the specified wiki page is not found.
            Exception: If there is a network error.
        """
        try:
            bucket = self.storage_client.bucket("sdswiki_contents")
            blob = bucket.blob(name)
            with blob.open() as f:
                content = f.read()
            return content

        except exceptions.NotFound:
            return f"Error: Wiki page {name} not found."

        except Exception as e:
            return f"Network error: {e}"

    def get_all_page_names(self):
        """Gets the names of all wiki pages.

        Returns:
            A list of the names of all wiki pages.

        Raises:
            Exception: If there is a network error.
        """
        try:
            pages_names_list = []
            blobs = self.storage_client.list_blobs("sdswiki_contents")

            if not blobs:
                return "Error: No pages found in bucket."

            for blob in blobs:
                pages_names_list.append(blob.name)

            return pages_names_list

        except Exception as e:
            return f"Network error: {e}"

    def upload(self, data, destination_blob_name):
        '''
        Uploads page to Wiki server

        Args:
            destination_blob_name = name of page to be uploaded
            data = the information to be displayed on the page

        returns:
            A response message stating if your upload was successful or not.
            If the upload was unsuccessulf, the reason why would be displayed.
        '''
        if data == b'':
            return 'Please upload a file.'
        if destination_blob_name == '':
            return 'Please provide the name of the page.'

        blobs = self.storage_client.list_blobs('sdswiki_contents')
        bucket = self.storage_client.bucket('sdswiki_contents')

        for blob in blobs:
            if destination_blob_name == blob.name:
                return 'Upload failed. You cannot overrite an existing page'

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data)

        return f"{destination_blob_name} uploaded to Wiki."

    def sign_up(self, name, password):
        '''
        Allows a person to create an account on the wiki if they are using it for th efirst time.

        Args:
            name = This acts as the username of the person
            password = The password associated with the account for the wiki

        Returns:
            A message letting you know if your account was successfully created,
            or if it was unsuccessful because the user already exists.
        '''
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

    #Checks the buckets to ensure correct info is being used for logins
    def sign_in(self, username, password):
        '''
        Allows a person to sign into their wiki account.

        Args:
            username = This acts as the username of the person
            password = The password associated with the account for the wiki

        Returns:
            A message letting you know if login was successful or not.
        '''
        salty_password = f"{username}{password}".encode()
        hashed = hashlib.sha3_256(salty_password).hexdigest()
        blobs = self.storage_client.list_blobs('sdsusers_passwords')
        stored = False

        for blob in blobs:
            if username == blob.name:
                with blob.open("r") as username:
                    secure_password = username.read()
                stored = True
        if not stored:
            return "Username not found"

        if hashed == secure_password:
            return 'Sign In Successful'
        return 'Incorrect Password'

    def get_image(self, name):
        '''
        Allows images to be pulled from the bucket and sent to the html pages. 

        Args:
            name = The name of the picture

        Returns:
            Binary form of the image reqested.
        '''
        bucket = self.storage_client.bucket('sdsimages')
        blob = bucket.blob(name)

        with blob.open("rb") as f:
            img = f.read()

        return img

    def delete_page(self, name):
        blobs = self.storage_client.list_blobs('sdswiki_contents')
        for blob in blobs:
            if blob.name == name:
                blob.delete()
                return True
        return False

    def bookmark(self, page_title, name):
        '''
        Stores a user's bookmark in a GCP blob

        Args:
            page_title = page to bookmark
            name = The name of the user's account

        Returns:
            True for successful bookmarks, False otherwise
        '''
        bucket = self.storage_client.bucket('sds_bookmarks')
        blob = bucket.get_blob(name)

        #For first time bookmarks
        if blob == None:
            blob = bucket.blob(name)
            blob.upload_from_string(page_title + '\n')
            return True

        #Adding bookmarks to existing blobs instead of overwritting data
        with blob.open('r') as f:
            bookmark_data = f.read()
        if page_title not in bookmark_data:
            bookmark_data += page_title + '\n'
            blob.upload_from_string(bookmark_data)
            return True
        #Return false if bookmark already exists
        return False

    def get_bookmarks(self, name, existing_pages):
        '''
        Pulls a user's bookmarks from GCP Bucket and ensures all bookmarks are still valid

        Args:
            name = The name of the user's account
            existing_pages = pages currently in the wiki

        Returns:
            list of bookmarks
        '''
        new_data = ""
        deleted_pages = False
        bookmarks_list = []
        bucket = self.storage_client.bucket('sds_bookmarks')
        blob = bucket.get_blob(name)

        if blob == None:
            return bookmarks_list

        #Reading in bookmark data
        with blob.open('r') as f:
            bookmark_data = f.readlines()

        #Ensuring all bookmarked pages are still active (in the wiki)
        for line in bookmark_data:
            if line[:-1] not in existing_pages:
                deleted_pages = True
                continue
            new_data += line
            bookmarks_list.append(line[:-1])

        if deleted_pages:
            blob.upload_from_string(new_data)
        return bookmarks_list

    def remove_bookmark(self, title, name):
        '''
        Rewrites a blob's data and skips over the line to remove 

        Args:
            title = bookmark to remove
            name = The name of the user's account

        Returns:
            Success message or error message
        '''
        new_data = ""
        deleted = False
        bucket = self.storage_client.bucket('sds_bookmarks')
        blob = bucket.get_blob(name)
        title += '\n'
        #Read in bookmark data
        with blob.open('r') as f:
            bookmark_data = f.readlines()
        #Rewriting data but skipping over the line we're removing
        for line in bookmark_data:
            if line == title:
                deleted = True
                continue
            new_data += line
        #Upload new data
        blob.upload_from_string(new_data)
        #Return success or error message
        if deleted:
            return 'Bookmark successfully deleted'
        return 'Error'
