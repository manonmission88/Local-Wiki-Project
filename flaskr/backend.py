'''
This module works as the backend for a Wiki Page.

Contains two classes: The User and the Backend class
which define how the application interacts with the storage system.
'''

from google.cloud import storage
from datetime import datetime
import hashlib
import base64
import hashlib
import json


class User:

    def __init__(self, username):
        '''Initializes a User object'''
        self.username = username
        self.client = storage.Client()
        self.bucket = self.client.bucket('wiki_login')
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.username

    def save(self, password):
        '''
        This method uploads a user information into the wiki_login bucket.
        '''
        blob = self.bucket.blob(self.username)
        salted = f"{self.username}{'gamma'}{password}"
        hashed = hashlib.md5(salted.encode())
        with blob.open("w") as f:
            f.write(hashed.hexdigest())
        return True

    def load(self):
        '''This method returns the password of the current user from the users bucket.'''
        blob = self.bucket.blob(self.username)
        data = blob.download_as_bytes()
        return data.decode('utf-8')

    @staticmethod
    def get(username):
        '''
        This method tries to find a user with the associated username in our users bucket,
        and returns a Username object with its information
        '''
        user = User(username)
        try:
            user.load()
            return User(username)
        except:
            return None


class Backend:

    def __init__(self,
                 storage_client=storage.Client(),
                 info_bucket_name='wiki_info',
                 user_bucket_name='wiki_login'):
        '''
        storage: Instantiates a client
        info_bucket_name : bucket name to store the data related to pages and about 
        '''
        self.storage_client = storage_client
        self.info_bucket = self.storage_client.bucket(info_bucket_name)
        self.user_bucket = self.storage_client.bucket(user_bucket_name)

    def get_wiki_page(self, name):  # 1
        ''' Gets an uploaded page from the content bucket
            name : name of the page files 
           '''

        # Find the wiki-page's file in the GCS bucket.
        blob = self.info_bucket.blob(name)

        # Get its content as a dictionary using the JSON API
        name_data = json.loads((blob.download_as_string()), parse_constant=None)

        # If we don't get anything, the wiki-page does not exist.
        if not name_data:
            return None

        return name_data

    def get_all_page_names(self):
        ''' Gets all the names of the pages uploaded to the wiki'''
        page_names = []

        pages = self.storage_client.list_blobs(self.info_bucket)

        for page in pages:
            extension = page.name.find('.')

            if page.name[extension:] == '.txt':
                page_names.append(page.name[:extension])

        return page_names

    def upload(self, file, filename):
        ''' Adds data to the content bucket 
         file : path of the file 
         filename : name of the file user selected
         username: username of current user
         '''
        blob = self.info_bucket.blob(filename)

        # Get today's date in YYYY-MM-DD format.
        date = datetime.today().strftime('%Y-%m-%d')

        # Set up the dictionary containing all the wiki-page's metadata.
        metadata = {
            'wiki_page': filename,
            'content': file.read().decode('utf-8'),
            'date_created': date,
            'upvotes': 0,
            'who_upvoted': None,
            'downvotes': 0,
            'who_downvoted': None,
            'comments': []
        }

        # Convert it to a JSON file.
        metadata_json = json.dumps(metadata)

        # Save it to the GCS bucket.
        blob.upload_from_string(metadata_json, content_type='application/json')

    def sign_up(self, username, password):
        ''' Adds data to the content bucket 
         username : user created username 
         password : user created password
         '''
         # Hashes username and password with salt
        salted = f"{username}{'gamma'}{password}"
        hashed = hashlib.md5(salted.encode())

        # Checks if blob exist with username and raise error if it does
        blob = self.user_bucket.get_blob(username)
        if blob is not None:
            # raise ValueError((f"{username} already exists!"))
            return None

        # Creates blob with username
        blob = self.user_bucket.blob(username)

        # Get today's date in YYYY-MM-DD format.
        date = datetime.today().strftime('%Y-%m-%d')

        # Set up the dictionary containing all the author's metadata.
        metadata = {
            'hashed_password': hashed.hexdigest(),
            'account_creation': date,
            'wikis_uploaded': [],
            'wiki_history': [],
            'pfp_filename': None,
            'about_me': '',
        }

        # Convert it to a JSON file.
        metadata_json = json.dumps(metadata)

        # Save it to the GCS bucket.
        blob.upload_from_string(metadata_json, content_type='application/json')
        return User(username)

    def sign_in(self, username, password):
        '''Checks if the given username and password matches a user in our GCS bucket'''
        if storage.Blob(bucket=self.user_bucket,
                        name=username).exists(self.storage_client):
            blob = self.user_bucket.blob(username)

            # Get its content as a dictionary using the JSON API and returns none if doesn't exist
            account_data = json.loads((blob.download_as_string()), parse_constant=None)
            if not account_data:
                return None

            salted = f"{username}{'gamma'}{password}"
            hashed_password = hashlib.md5(salted.encode()).hexdigest()

            # Takes password from GCS JSON
            if hashed_password == account_data['hashed_password']:
                return User(username)
        return None

    def get_image(self, image_name):  # 2
        ''' Gets an image from the content bucket.
            image_name : name of the image to be get from bucket  '''

        try:
            blob = self.info_bucket.blob(image_name)
            image_data = blob.download_as_bytes()
            if image_data:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return base64_image
        except FileNotFoundError:  #handling the not existing file
            raise ValueError('Image Name does not exist in the bucket')
    
    def get_user_account(self, username):
        ''' Gets a user's account settings
            username: Current user
        '''

        # Find the user's account settings
        blob = self.user_bucket.blob(username)

        # Get its dictionary using JSON API
        account_data = json.loads((blob.download_as_string()), parse_constant=None)

        # If doesn't exist, return none
        if not account_data:
            return None
        
        return account_data


    def update_wikiupload(self, username, fileuploaded):
        ''' Changes and overwrites account json when a user uploads a new wiki.
            username : Current user that caused action.
            fileuploaded : Filename that user uploaded
        '''
        blob = self.user_bucket.blob(username)
        
        # Get the current wiki_page's json file as a dictionary.
        user_metadata = Backend.get_user_account(self, username)
        user_metadata['wikis_uploaded'].append(fileuploaded)

        # Overwrite current account metadata
        blob.upload_from_string(json.dumps(user_metadata), content_type='application/json')
        return user_metadata
                

