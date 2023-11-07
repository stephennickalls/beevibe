    
class FormatUUIDs():

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