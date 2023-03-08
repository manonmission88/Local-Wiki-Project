# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import base64
import hashlib

class User:

    def __init__(self, username, password, pages_created = []):
        self.username = username
        self.password = password
        self.pages_created = pages_created
        self.is_authenticated = False
    
    def get_id(self):
        return self.username
    
class Backend:

    def __init__(self, storage_client = storage.Client(), bucket_name = 'wiki_info'):
        self.storage_client = storage_client
        self.bucket = self.storage_client.bucket(bucket_name)
        
    def get_wiki_page(self, name): # 1 
        ''' Gets an uploaded page from the content bucket '''
        blob = self.bucket.blob(name)
        name_data = blob.download_as_bytes()
        if not name_data.strip():
            return None 
        return name_data.decode('utf-8')

    def get_all_page_names(self):
        ''' Gets all the names of the pages uploaded to the wiki'''
        page_names = []

        pages = self.storage_client.list_blobs(self.bucket)

        for page in pages:
            extension = page.name.find('.')

            if page.name[extension:] == '.txt':
                page_names.append(page.name[:extension])

        return page_names

    def upload(self):
        pass

    def sign_up(self, username, password):
        # first create new sign_up html template (DONE)
        # have it follow the correct template (DONE)
        # currently the signup.html form sends action to /signup
        # store username & password variable, after submit button is pressed (DONE)
        # figure out how to save user object to GCS (DONE)
            # - save username as blob name and then write to blob (with hashpassword) (DONE)
            # - issue with pulling username from the form (need to typecheck and print) (FIXED)
            # can't user user object
        # can use JSON as a further implement
        # sub problem: figure out how to save object names
        # - handle empty suites (DONE)
        # - handle full suites (DONE)
        # - handle already signed up users 
        # - handle incorrect password
        # use login manager to pull
        # if user exist, render a new template
        ''' Adds data to the content bucket 
         user.get_id : username 
         user : user object
         '''
        # makes sure sign up handles duplicates
        # fix and add salt (DONE)
        # return user object & redirect home
        salted = f"{username}{'gamma'}{password}"
        print(salted)
        print(type(salted))
        hashed = hashlib.md5(salted.encode())
        print(hashed.hexdigest())
        blob = self.bucket.blob(username)
        with blob.open("w") as f:
            f.write(hashed.hexdigest())

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
        
    

        






