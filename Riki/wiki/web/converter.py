

class Converter(object):

    def __init__(self, page, filetype):
        self.page = page
        self.path = page.get_path()
        self.filetype = filetype

    def get_path(self):
        return self.path


class PDFConverter(Converter):
    pass


class TXTConverter(Converter):
    pass


class HTMLConverter(Converter):
    pass


class docxConverter(Converter):
    pass
