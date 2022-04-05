class DocumentUpdate:

    def __init__(self, text, focus, status):

        self._base_text = text
        self._user_focus = focus
        self._status = status

    def get_base_text(self):
        return self._base_text

    def get_user_focus(self):
        return self._user_focus

    def get_status(self):
        return self._status
