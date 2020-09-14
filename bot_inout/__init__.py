from pydantic import BaseModel, validator
from datetime import datetime


class BotInput(BaseModel):
    """
        Information that comes after setting the dataplugin and Bot creation with BotFather
    """
    dataplugin_id: int
    owner_id: int
    token_bot: str

    class Config:
        title = 'Bot Input data'

    @validator("token_bot")
    def validate_token(cls, v):
        if any(x.isspace() for x in v):
            raise ValueError("Token is invalid! It can't contains spaces.")
        left, sep, right = v.partition(':')
        if (not sep) or (not left.isdigit()) or (not right):
            raise ValueError('Token is invalid!, verify the entire structure')
        return v

    async def to_dict(self) -> object:
        """ This method returns a dict representation of the instance """
        new_dict = {}
        for key, item in self.__dict__.items():
            if key in ['created_at', 'updated_at']:
                new_dict[key] = item.isoformat()
            else:
                new_dict[key] = item
        return new_dict


class FormUpdate(BaseModel):
    """
        Instantiates the object as the information that comes from updating bot **status**
    """
    dataplugin_id: int
    status: str


class BotOutput:

    def __init__(self, args: object, kwargs: object) -> object:
        """Instantiates the attributes of Output data of Bot"""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = "RUN"
        if args is not None and len(args) > 0:
            pass
        if kwargs:
            for key, item in kwargs.items():
                if key in ['created_at', 'updated_at']:
                    item = datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f")
                    setattr(self, key, item)
                elif key == "__class__":
                    continue
                else:
                    setattr(self, key, item)
        else:
            self.dataplugin_id = 0
            self.owner_id = 0
            self.token_bot = ""
            self.status = ""

    async def to_dict(self) -> object:
        """ This method returns a dict representation of the instance """
        new_dict = {}
        for key, item in self.__dict__.items():
            if key in ['created_at', 'updated_at']:
                new_dict[key] = item.isoformat()
            else:
                new_dict[key] = item
        return new_dict


class BotUpdate:

    def __init__(self, args: object, kwargs: object) -> object:
        """Instantiates the attributes of Updated data of Bot"""
        if args is not None and len(args) > 0:
            pass
        if kwargs:
            for key, item in kwargs.items():
                if key in ['created_at', 'updated_at']:
                    item = datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f")
                    setattr(self, key, item)
                elif key == "__class__":
                    continue
                else:
                    setattr(self, key, item)
        else:
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            self.status = ""
            self.owner_id = 0
            self.token_bot = ""
            self.status = ""
            self.ubidots_token = ""

    async def to_dict(self) -> object:
        """ This method returns a dict representation of the instance """
        new_dict = {}
        for key, item in self.__dict__.items():
            if key in ['created_at', 'updated_at']:
                new_dict[key] = item.isoformat()
            else:
                new_dict[key] = item
        return new_dict
