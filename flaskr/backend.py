from google.cloud import storage
from google.cloud import exceptions
from flask_login import current_user
import hashlib
import io
from flask import Flask


class Backend:

    def __init__(self, storage_client=storage.Client()):
        self.storage_client = storage_client
        self.pages_bucket = self.storage_client.bucket('sdswiki_contents')
        self.users_bucket = self.storage_client.bucket('sdsusers_passwords')
        self.images_bucket = self.storage_client.bucket('sdsimages')
        self.pages_blobs = self.storage_client.list_blobs('sdswiki_contents')
        self.users_blobs = self.storage_client.list_blobs('sdsusers_passwords')

    def get_wiki_page(self, name):
        """Gets the contents of the specified wiki page.

        Args:
            name: The name of the wiki page.

        Returns:
            The contents of the wiki page.

        Raises:
            Exception: If there is a network error.
        """
        bucket = self.storage_client.bucket("sdswiki_contents")
        blob = bucket.get_blob(name)
        if blob is None:
            return f"Error: Wiki page {name} not found."

        try:
            with blob.open() as f:
                content = f.read()
            return content
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
            blobs = self.storage_client.list_blobs('sdswiki_contents')

            if not self.pages_blobs:
                return "Error: No pages found in bucket."

            for blob in self.pages_blobs:
                pages_names_list.append(blob.name)

            return pages_names_list

        except Exception as e:
            return f"Error: {e}"

    def upload(self, data, destination_blob_name, username, override=False):
        '''
        Uploads page to Wiki server

        Args:
            destination_blob_name = name of page to be uploaded
            data = the information to be displayed on the page

        returns:
            A response message stating if your upload was successful or not.
            If the upload was unsuccessful, the reason why would be displayed.
        '''
        if len(data) <= 0:
            if override:
                return 'Page contents cannot be empty'
            return 'Please upload a file.'

        if destination_blob_name == '':
            return 'Please provide the name of the page.'

        blobs = self.storage_client.list_blobs('sdswiki_contents')
        for blob in blobs:
            if destination_blob_name == blob.name and not override:
                return 'Upload failed. You cannot overrite an existing page'

        try:
            blob = self.pages_bucket.blob(destination_blob_name)
            # Set the x-goog-meta-author metadata header
            blob.metadata = {'author': username}

            blob.upload_from_string(data)

        except Exception as e:
            return f"Network Error: {e}. Please try again later."

        if override:
            return f"The page titled {destination_blob_name} was successfully updated."
        return f"{destination_blob_name} uploaded to Wiki."

    def report(self, page, message):
        '''
        Saves the report message for a page in backend
        Args: The page being reported, and the message of the report
        Returns: A message stating the status of the report made.
        '''
        if message == '':
            return 'You need to enter a message'
        bucket = self.storage_client.bucket('sds_reports')

        blob = bucket.get_blob(page)
        if blob == None:
            blob = bucket.blob(page)
            blob.upload_from_string(message)

        else:
            new_report = message + '\n'
            with blob.open('r') as f:
                new_report += str(f.read())
            with blob.open('w') as f:
                f.write(new_report)
        return "Your report was sent successfully."

    def sign_up(self, name, password):
        '''
        Allows a person to create an account on the wiki if they are using it for the first time.

        Args:
            name = This acts as the username of the person
            password = The password associated with the account for the wiki

        Returns:
            A message letting you know if your account was successfully created,
            or if it was unsuccessful because the user already exists.
        '''

        blobs = self.storage_client.list_blobs('sdsusers_passwords')
        for blob in blobs:
            if blob.name == name:
                return f"user {name} already exists in the database. Please sign in."

        blob = self.users_bucket.blob(name)
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
        stored = False

        for blob in self.users_blobs:
            if username == blob.name:
                with blob.open("r") as username:
                    secure_password = username.read()
                stored = True
        if not stored:
            return False

        if hashed == secure_password:
            return True
        return False

    def get_image(self, name):
        '''
        Allows images to be pulled from the bucket and sent to the html pages. 

        Args:
            name = The name of the picture

        Returns:
            Binary form of the image reqested.
        '''
        blob = self.images_bucket.get_blob(name)

        if blob == None:
            return None

        with blob.open("rb") as f:
            img = f.read()

        return img

    def check_page_author(self, page_name):
        """
        Retrieves the author metadata of a blob with the given name from the Google Cloud Storage bucket.

        Args:
            name (str): The name of the blob to retrieve the author metadata from.

        Returns:
        If the specified blob exists and has an author metadata, returns the author's name as a string.
        If the specified blob does not exist or does not have an author metadata, returns None.
        If an error occurs while retrieving the metadata, returns None and prints an error message.
        """
        bucket = self.storage_client.bucket("sdswiki_contents")
        blob = bucket.get_blob(page_name)
        if blob:
            try:
                metadata = blob.metadata
                author = metadata.get('author')
                if author:
                    return author
                else:
                    return None

            except AttributeError:
                return None

        else:
            return None

    def delete_page(self, name):
        '''
        Allows pages to be deleted from the wiki. 

        Args:
            name = The name of the page to delete

        Returns:
            True upon successful delete, false otherwise
        '''
        #Deleting the page's blob
        blobs = self.storage_client.list_blobs('sdswiki_contents')
        for blob in blobs:
            if blob.name == name:
                blob.delete()
                return True
        #Return false if it was never found
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

    def search_pages(self, search_content, max_distance, wiki_searcher=None):
        if wiki_searcher is None:
            wiki_searcher = self

        if len(search_content) < 1:
            return []

        search_words = search_content.lower().split()

        search_results = []

        all_pages = wiki_searcher.get_all_page_names()

        for page_title in all_pages:
            title_match_counter = 0
            content_match_counter = 0

            close_title_match_counter = 0
            close_content_match_counter = 0
            title_words = page_title.lower().split()
            page_content = wiki_searcher.get_wiki_page(page_title)
            page_words = page_content.lower().split()

            for search_word in search_words:

                for title_word in title_words:
                    if search_word == title_word:
                        title_match_counter += 1
                    elif levenshtein_distance(search_word,
                                              title_word) <= max_distance:
                        close_title_match_counter += 1

                for page_word in page_words:

                    if search_word == page_word:
                        content_match_counter += 1
                    elif levenshtein_distance(search_word,
                                              page_word) <= max_distance:
                        close_content_match_counter += 1

            match_score = title_match_counter * 0.8 + content_match_counter * 0.1 + close_title_match_counter * 0.08 + close_content_match_counter * 0.02

            if match_score > 0:
                search_results.append((page_title, match_score))

        # Sort search_results by match score
        search_results.sort(key=lambda x: x[1], reverse=True)

        # Extract page titles from search_results and return them
        page_titles = [result[0] for result in search_results]

        return page_titles
