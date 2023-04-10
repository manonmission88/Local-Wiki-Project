from flaskr import create_app
from flaskr.backend import User ,Backend
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from unittest.mock import patch
import pytest
import base64

# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():

    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })

    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def test_user():
    username = 'testing'
    password = 'testing'
    user = User(username)
    # Upload a test user to the bucket.
    user.save(password)
    yield user
    blob = user.bucket.blob(username)
    # After we have finished testing, just delete it.
    blob.delete()


@pytest.fixture
def test_newuser():
    username = 'new_user'
    password = 'new_user'
    user = User(username)
    # Upload a test user to the bucket.
    user.save(password)
    yield user
    blob = user.bucket.blob(username)
    # After we have finished testing, just delete it.
    blob.delete()


@pytest.fixture
def test_repeatuser():
    username = 'new_user_same'
    password = 'new_user'
    user = User(username)
    # Upload a test user to the bucket.
    user.save(password)
    yield user
    # blob = user.bucket.blob(username)


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Welcome To Our Wiki-fun in your local\n" in resp.data


# TODO(Project 1): Write tests for other routes.
def test_about_page(client):

    '''  Test function to test about route 

        Arg : Client 
    '''

    with patch('flaskr.backend.Backend.get_image') as mock_get_image:

        expected = base64.b64encode(b'Fake_Image_Data').decode('utf-8')
        mock_get_image.return_value = expected
        response = client.get('/about')

        assert response.status_code == 200
        expected_html = f"<img src='data:image/jpeg;base64,{expected}' alt='Author Image'>"
        assert expected_html.encode() in response.data



def fixittest_pages_page(client):
    with patch('flaskr.backend.Backend.get_all_page_names') as mock_page:
        mock_page.return_value = ['Page 1','Page 2']
        resp = client.get('/pages')
        assert resp.status_code == 200
        assert b"Page 1" in resp.data
        assert b"Page 2" in resp.data


def test_wiki_page(client):
    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
        mock_page.return_value = 'Content Of The Wiki'
        resp = client.get('/pages/GeorgeTown%20Waterfront%20Park')
        assert resp.status_code == 200
        assert b'Content Of The Wiki' in resp.data 


def fixit_test_login(client, test_user):
    # Send a response to the route trying to verify for the test user.
    response = client.post('/login',
                           data={
                               'username': 'testing',
                               'password': 'testing'
                           })
    # We should get redirected to the home page, resulting in a 302 code.
    assert response.status_code == 302
    # The current_user should be updated to 'testing'.
    assert current_user.username == 'testing'


def fixit_test_login_incorrect_password(client, test_user):
    # If we pass the wrong information, we will not be redirected.
    response = client.post('/login',
                           data={
                               'username': 'testing',
                               'password': 'wrongpassword'
                           })
    assert response.status_code == 200
    # We do not have a user authenticated as nobody actually logged in.
    assert current_user.is_authenticated == False


def fixit_test_logout(client, test_user):
    response = client.post('/login',
                           data={
                               'username': 'testing',
                               'password': 'testing'
                           })
    assert response.status_code == 302
    assert current_user.is_authenticated
    assert current_user.username == 'testing'

    # Check if logging out actually works
    response = client.get('/logout')
    assert response.status_code == 302
    assert current_user.is_anonymous


def fixit_test_signup(client, test_user):
    # Send a response to the route trying to verify for the test user.
    response = client.post('/signup',
                           data={
                               'username': 'new_user',
                               'password': 'new_user'
                           })
    # We should get redirected to the home page, resulting in a 302 code.
    assert response.status_code == 302
    # The current_user should be updated to 'testing'.
    assert current_user.username == 'new_user'


def fixit_test_incorrect_signup(client, test_repeatuser):
    # Send a response to the route trying to hit the same user.
    response = client.post('/signup',
                           data={
                               'username': 'new_user_same',
                               'password': 'new_user'
                           })
    # We should not go to the home page, resulting in a 200 code.
    assert response.status_code == 200



def test_search_for_title_with_results(client):

    ''' Testing the search route for search_by_title post with some results 

          Args : 
            client : Flask Client Object 

    '''
    with patch('flaskr.backend.Backend.search_by_title') as mock_search:

        mock_search.return_value = ['title_1','title_2']
        response = client.post('/search' ,data={'search_query':'query' , 'search_by':'title'})
        assert response.status_code == 200
        assert b'title_1' in response.data
        assert b'title_2' in response.data

    mock_search.assert_called_once_with('query')

    

def test_search_for_title_with_no_result(client):

    ''' Testing the search route for search_by_title post for  empty list 

         Args : 
            client : Flask Client Object 

    '''
    with patch('flaskr.backend.Backend.search_by_title') as mock_search:
        mock_search.return_value = []
        response=client.post('/search',data={'search_query':'query', 'search_by' : 'title'})

        assert response.status_code == 200
        assert b'No such pages found for' in response.data

    
def test_search_for_content_with_results(client):
    '''  Testing the search rout for search_by_content post with some results

        Args : 
            client : Flask Client Object 
    ''' 
    with patch('flaskr.backend.Backend.search_by_content') as mock_search:
        mock_search.return_value = ['title_3' ,'title_4']

        # print(Backend.search_by_content())
        response=client.post('/search',data={'search_query':'query', 'search_by' : 'content'})
      
        assert response.status_code == 200
        assert b'title_3' in response.data
        assert b'title_4' in response.data
def test_search_for_content_with_no_result(client):
    '''  Testing the search rout for search_by_content post with some results

        Args : 
            client : Flask Client Object 
    ''' 
    with patch('flaskr.backend.Backend.search_by_content') as mock_search:

        mock_search.return_value = []
        response=client.post('/search',data={'search_query':'query', 'search_by' : 'content'})
      
        assert response.status_code == 200
        assert b'No such pages found with ' in response.data







