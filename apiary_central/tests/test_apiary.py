from rest_framework import status
from rest_framework.test import APIClient

class TestCreateApiary:
    def test_it_user_is_anonymous_returns_401(self):
        client = APIClient()
        response = client.post('/api/apiary/', {'name': 'a'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED