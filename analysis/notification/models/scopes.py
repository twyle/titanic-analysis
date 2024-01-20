from enum import Enum


class Scopes(Enum):
    # https://developers.google.com/gmail/api/auth/scopes
    drafts = 'https://www.googleapis.com/auth/gmail.compose'
    labels = 'https://www.googleapis.com/auth/gmail.labels'