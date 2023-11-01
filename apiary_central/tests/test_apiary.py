from rest_framework import status
from rest_framework.test import APIClient

class TestCreateApiary:
    def test_if_user_is_anonymous_returns_401(self):
        client = APIClient()
        response = client.post('/api/apiaries/', {'name': 'a', 
                                                'latitude':-38.80895, 
                                                'longitude':118.35449,
                                                'description': 'a',
                                                'registration_number': 'kb99887' })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_200(self):
        client = APIClient()
        response = client.post('/api/apiaries/', {'name': 'a', 
                                                'latitude':-38.80895, 
                                                'longitude':118.35449,
                                                'description': 'a',
                                                'registration_number': 'kb99887' })
        
        assert response.status_code == status.HTTP_200_OK