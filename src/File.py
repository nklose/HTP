class File:
    
    def __init__(self, file_name, parent_id, content, file_type, file_size):
        self.file_name = file_name
        self.parent_id = parent_id
        self.content = content
        self.file_type = file_type
        self.file_level = 1
        self.file_size = file_size
