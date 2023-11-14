    
from uuid import uuid4


class UUIDs():

    def add_hyphens_to_uuid(uuid_string_without_hyphens):
        # Ensure the UUID string has no hyphens
        uuid_string_without_hyphens = uuid_string_without_hyphens.replace('-', '')
        # Add hyphens to the UUID string
        return '{0}-{1}-{2}-{3}-{4}'.format(
            uuid_string_without_hyphens[:8],
            uuid_string_without_hyphens[8:12],
            uuid_string_without_hyphens[12:16],
            uuid_string_without_hyphens[16:20],
            uuid_string_without_hyphens[20:]
        )
    
    def generate_api_key():
        return uuid4().hex # may change implimentation hence not dry
    
    def generate_uuid():
        return uuid4().hex
    

