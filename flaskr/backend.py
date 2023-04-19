from google.cloud import storage
from google.cloud import exceptions
from .search_algo import levenshtein_distance
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

    def search_pages(self, search_content, max_distance, wiki_searcher=None):
        if wiki_searcher is None:
            wiki_searcher = self

        if len(search_content) < 1:
            return []

        search_words = search_content.lower().split()
        print("search words " + str(search_words))

        search_results = []

        all_pages = wiki_searcher.get_all_page_names()

        for page_title in all_pages:
            title_match_counter = 0
            content_match_counter = 0

            close_title_match_counter = 0
            close_content_match_counter = 0
            title_words = page_title.lower().split()
            print("title words" + str(title_words))
            page_content = wiki_searcher.get_wiki_page(page_title)
            page_words = page_content.lower().split()

            for search_word in search_words:

                for title_word in title_words:
                    if search_word == title_word:
                        print("search word: " + search_word + " title word: " +
                              title_word)
                        title_match_counter += 1
                    elif levenshtein_distance(search_word,
                                              title_word) <= max_distance:
                        print("close match: search word: " + search_word +
                              " page word: " + title_word)
                        close_title_match_counter += 1

                for page_word in page_words:

                    if search_word == page_word:
                        print("match: search word: " + search_word +
                              " page word: " + page_word)
                        content_match_counter += 1
                    elif levenshtein_distance(search_word,
                                              page_word) <= max_distance:
                        print("close match: search word: " + search_word +
                              " page word: " + page_word)
                        close_content_match_counter += 1

            print("title_match_counter: " + str(title_match_counter) +
                  " content_match_counter: " + str(content_match_counter) +
                  " close_title_match_counter: " +
                  str(close_title_match_counter) +
                  " close_content_match_counter: " +
                  str(close_content_match_counter))
            match_score = title_match_counter * 0.8 + content_match_counter * 0.1 + close_title_match_counter * 0.08 + close_content_match_counter * 0.02
            print(page_title + " match score: " + str(match_score))

            if match_score > 0:
                search_results.append((page_title, match_score))

            print("")
            print("")

        # Sort search_results by match score
        search_results.sort(key=lambda x: x[1], reverse=True)

        # Extract page titles from search_results and return them
        page_titles = [result[0] for result in search_results]

        return page_titles
