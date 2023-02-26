# TODO(Project 1): Implement Backend according to the requirements.

from google.cloud import storage

BUCKET_NAME = "sdswiki_contents"

class Backend:

    def __init__(self):
        pass
    
    #Gets an uploaded page from the content bucket.
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

        return pages_names_list
            
    def upload(self):
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self):
        pass



backend = Backend()

print(backend.get_wiki_page("page_one.txt"))
print(backend.get_all_page_names())