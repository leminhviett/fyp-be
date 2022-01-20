import uuid, werkzeug, os

def gen_unique_filename(file_name):
    return f"{uuid.uuid4()}_{file_name}"

# for form data upload
class BaseFile:
    def __init__(self, file_object:werkzeug.datastructures.FileStorage, root_storage=os.getenv("STORAGE_PATH")) -> None:
        self.root_storage = root_storage

        if file_object is None: return 

        self.file_object = file_object
        self.file_name = gen_unique_filename(self.file_object.filename)

    def save(self):
        full_loc = os.path.join(self.root_storage, self.get_subfolder(), self.file_name)
        if self.file_object:
            self.file_object.save(full_loc)
    
    def get_subfolder(self):
        pass

    def delete(self, file_loc):
        try:
            os.remove(os.path.join(self.root_storage, file_loc))
        except OSError:
            pass

class VmFile(BaseFile):
    def get_subfolder(self):
        return os.getenv("VM_FOLDER")
        
class ImgFile(BaseFile):
    def get_subfolder(self):
        return os.getenv("IMG_FOLDER")

# for base64 save
import base64

class ImgEncoded:
    def __init__(self, data:str, file_name:str) -> None:
        #file_name assume to be unique
        if data == '': return 

        try:
            self.data = data.encode()
        except Exception as e:
            raise e
        self.file_name = file_name
        self.sub_folder = os.getenv("IMG_FOLDER")

    def save(self):
        
        loc = os.path.join(os.getenv("STORAGE_PATH"), self.sub_folder, self.file_name)
        with open(loc, "wb") as fh:
            fh.write(base64.decodebytes(self.data))
    
    def delete(self, file_loc):
        try:
            os.remove(os.path.join(os.getenv("STORAGE_PATH"), file_loc))
        except OSError:
            pass
        