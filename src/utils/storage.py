import uuid, werkzeug, os

def gen_unique_filename(user_name, file_name):
    return f"{user_name}-{uuid.uuid4()}-{file_name}"

# for form data upload
class BaseFile:
    def __init__(self, file_object:werkzeug.datastructures.FileStorage, owner) -> None:
        self.file_object = file_object
        self.owner = owner
        self.file_name = gen_unique_filename(self.owner, self.file_object.filename)

    def save(self):
        self.file_object.save(self.get_full_loc())

    def get_full_loc(self):
        pass

class VmFile(BaseFile):
    _ROOT_FOLDER = os.path.join(os.getenv("STORAGE_PATH"), os.getenv("VM_FOLDER"))

    def get_full_loc(self):
        return os.path.join(self._ROOT_FOLDER, self.file_name)

class ImgFile(BaseFile):
    _ROOT_FOLDER = os.path.join(os.getenv("STORAGE_PATH"), os.getenv("IMG_FOLDER"))

    def get_full_loc(self):
        return os.path.join(self._ROOT_FOLDER, self.file_name)

# for base64 save
import base64


class ImgEncoded:
    _ROOT_FOLDER = os.path.join(os.getenv("STORAGE_PATH"), os.getenv("IMG_FOLDER"))

    def __init__(self, data:bytes, file_name:str) -> None:
        #file_name assume to be unique
        self.data = data
        self.full_loc = os.path.join(self._ROOT_FOLDER, file_name)

    def save(self):
        with open(self.full_loc, "wb") as fh:
            fh.write(base64.decodebytes(self.data))
        