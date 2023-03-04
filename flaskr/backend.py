# TODO(Project 1): Implement Backend according to the requirements.

# Imports the Google Cloud client library
from google.cloud import storage
import base64

class Backend:

    def __init__(self,bucket_name):
        '''
        client :  Instantiates a client
        '''
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        
    def get_wiki_page(self, name): # 1 
        ''' Gets an uploaded page from the content bucket '''
        blob = self.bucket.blob(name)
        name_data = blob.download_as_bytes()
        if not name_data.strip():
            return None 
        return name_data.decode('utf-8')

    def get_all_page_names(self):
        pass

    def upload(self):
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self,image_name): # 2

        ''' Gets an image from the content bucket. '''

        blob = self.bucket.blob(image_name)
        image_data=blob.download_as_bytes()
        if image_data:
            base64_image=base64.b64encode(image_data).decode('utf-8')
        return base64_image
        
# custom=Backend('wiki_info')
# print(custom.get_image('manish.jpeg'))
        
    

        






