from __future__ import print_function

import re
import csv
import sys
import boto3

class NoteException(Exception):
    """ Internal exception for errors to do with a Note object. """
    pass

class NoteParserException(Exception):
    """ Internal exception for errors to do with a NoteParser object. """
    pass

class NoteWriterException(Exception):
    """ Internal exception for errors to do with a NoteWriter object. """
    pass

class Note:
    """

    Represents a note object.
    :param header, the header of the note
    :param body, the body of the note
    :param namespace, what namespace the note exists in

    """
    def __init__(self, header, body, namespace=None):
        assert isinstance(header, str), "Header is not a string."
        assert isinstance(body, str), "Body is not a string."
        assert isinstance(namespace, str), "Namespace is not a string."
        self.header = header
        self.body = body
        self.namespace = "" if not namespace else namespace

    def __repr__(self):
        """ Overwriting the repr method with a CSV representation. """
        return [self.header, self.body, self.namespace]


class NoteParser:
    """

    An object for parsing tagged segments of a note
    :param config, the config dictionary with environmental configuration properties

    """
    def __init__(self, config):
        assert isinstance(config, dict), "Config is not a dict."
        self._default_pattern = config.get("default_pattern") or "(?:^|/s)(?:%s)([a-zA-Z/d]+)"
        self._default_tag_char = config.get("tag_char") or "#"
        self._regex = re.compile(self._default_pattern % self._tag_char)

    def parse_tags(self, note):
        return self._regex.match(note.header), self._regex.match(note.body)

    def note_is_tagged(self, note):
        return any(self.parse_tags)


class TaggedNote(Note):
    """
    Represents a note with tags
    :param header, the header of the note
    :param body, the body of the note
    :param namespace, what namespace the note exists in
    :param header_tags, the tags of the header
    :param body_tags, the tags of the body
    """
    def __init__(self, header, body, namespace, header_tags, body_tags):
        super().__init__(header, body, namespace)
        assert isinstance(header_tags, list), "Header tags is not a list."
        assert isinstance(body_tags, list), "Body tags is not a list."
        assert all(map(lambda t: isinstance(t, str), header_tags)), "Header tags is not a list of strings"
        assert all(map(lambda t: isinstance(t, str), body_tags)), "Body tags is not a list of strings"
        self.header_tags = header_tags or []
        self.body_tags = body_tags or []

    @property
    def all_tags(self):
        return self.header_tags + self.body_tags

    @classmethod
    def parse_tagged_note(cls, note, parser):
        header_tags, body_tags = parser.parse_tags(note)
        return cls(note.header, note.body, note.namespace, header_tags, body_tags)


class NoteWriter:
    """

    Object for holding notes and syncing their content with the cloud.
    :param config, the config dictionary with environmental configuration properties

    """
    def __init__(self, config):
        assert isinstance(config, dict), "Config is not a dict."
        self._annotate = config.get("annotate") or False

    def _get_tags_dict(self, note):
        return zip(["headertags", "bodytags"], self._parse_all_tags(note))

    def to_dict(self, tagged=True):
        assert isinstance(note, Note), "%s is not a Note object."
        return note.__dict__.merge(self._get_tags_dict) if tagged else note.__dict__

    def to_csv(self, note):
        if not annotate:
            return note.__repr__
        return ["{}{}".format(key.capitalize(), value) for (key, value) in note.as_dict.items()]


class NoteBlock:
    def __init__(self):
        self._MAX_NOTE_BLOCK_SIZE = 1024*30
        self._note_block = []

    def _add_note_to_block(self, note):
        if self.note_block_size + sys.getsizeof(note) <= self._MAX_NOTE_BLOCK_SIZE:
            self._note_block += note
        else:
            raise NoteBlockException("Cannot add note to block.")

    def add_notes_to_block(self, notes):
        if isinstance(notes, list):
            for note in notes:
                self._add_note_to_block(note)
        elif isinstance(notes, note):
            self._add_note_to_block(note)
        else:
            raise NoteBlockException("Cannot add note to block.")


class NoteCompiler:
    def __init__(self, config):
        self._note_parser = NoteParser(config)
        self._note_writer = NoteWriter(config)
        self._note_block = NoteBlock()


class Backend:
    pass
