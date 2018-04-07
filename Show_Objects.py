import uuid


class anime_show_object:
    def __init__(self, showname='', showimage=None, showlink='', id=uuid.uuid4()):
        self.id=id
        self.showname=showname
        self.showimage=showimage
        self.showlink=showlink


class cartoon_show_object:
    def __init__(self, showname='', showimage=None, showlink='', id=uuid.uuid4()):
        self.id=id
        self.showname=showname
        self.showimage=showimage
        self.showlink=showlink
