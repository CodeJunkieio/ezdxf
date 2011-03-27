#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: tables contained in tables sections
# Created: 13.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from collections import OrderedDict

from .defaultchunk import DefaultChunk
from .tags import ExtendedTags, Tags, DXFTag, TagGroups

TABLENAMES = {
    'layer': 'layers',
    'ltype': 'linetypes',
    'appid': 'appids',
    'dimstyle': 'dimstyles',
    'style': 'styles',
    'ucs': 'ucs',
    'view': 'views',
    'vport': 'viewports',
    'block_record': 'block_records',
}

def tablename(dxfname):
    """ Translate DXF-table-name to attribute-name. ('LAYER' -> 'layers') """
    name = dxfname.lower()
    return TABLENAMES.get(name, name+'s')

class GenericTable(DefaultChunk):
    @property
    def name(self):
        return tablename(self.tags[1].value)

class Table:
    def __init__(self, tags, drawing):
        self._dxfname = tags[1].value
        self._drawing = drawing
        self._table_entries = list()
        self._table_header = None
        self._build_table_entries(tags)

    # start public interface

    def create(self, name, attribs=None):
        if self.__contains__(name):
            raise ValueError('%s %s already exists!' % (self._dxfname, name))
        if attribs is None:
            attribs = {}
        attribs['name'] = name
        return self.new_entry(attribs)

    def get(self, name):
        return self.get_entry(name)

    def remove(self, name):
        self.remove_entry(name)

    def __contains__(self, name):
        return self.entry_exists(name)

    def __len__(self):
        return len(self._table_entries)

    def __iter__(self):
        for handle in self._table_entries:
            yield self.get_table_entry_wrapper(handle)

    # end public interface

    @property
    def name(self):
        return tablename(self._dxfname)

    def _build_table_entries(self, tags):
        groups = TagGroups(tags)
        assert groups.getname(0) == 'TABLE'
        assert groups.getname(-1) == 'ENDTAB'

        self._table_header = ExtendedTags(groups[0][1:])
        for entrytags in groups[1:-1]:
            self._add_entry(ExtendedTags(entrytags))

    @property
    def entitydb(self):
        return self._drawing.entitydb

    @property
    def handles(self):
        return self._drawing.handles

    @property
    def dxffactory(self):
        return self._drawing.dxffactory

    def _iter_table_entries_as_tags(self):
        """ Iterate over table-entries as Tags(). """
        return ( self.entitydb[handle] for handle in self._table_entries )

    def entry_exists(self, name):
        """ Check if an table-entry 'name' exists. """
        try:
            entry = self.get_entry(name)
            return True
        except ValueError:
            return False

    def new_entry(self, attribs):
        """ Create new table-entry of type 'self._dxfname', and add new entry
        to table.

        Does not check if an entry attribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        handle = self.handles.next
        entry = self.dxffactory.new_entity(self._dxfname, handle, attribs)
        self._add_entry(entry)
        return entry

    def _add_entry(self, entry):
        """ Add table-entry to table and entitydb. """
        if isinstance(entry, Tags):
            handle = entry.gethandle(self.handles)
            tags = entry
        else:
            handle = entry.handle
            tags = entry.tags
        self.entitydb[handle] = tags
        self._table_entries.append(handle)

    def get_entry(self, name):
        """ Get table-entry by name as WrapperClass(). """
        for entry in iter(self):
            if entry.name == name:
                return entry
        raise ValueError(name)

    def get_table_entry_wrapper(self, handle):
        tags = self.entitydb[handle]
        return self.dxffactory.wrap_entity(tags)

    def remove_entry(self, name):
        """ Remove table-entry from table and entitydb by name. """
        entry = self.get_entry(name)
        handle = entry.handle
        self._table_entries.remove(handle)
        del self.entitydb[handle]

    def write(self, stream):
        """ Write DXF represention to stream, stream opened with mode='wt'. """
        def prologue():
            stream.write('  0\nTABLE\n')
            self._update_meta_data()
            self._table_header.write(stream)

        def content():
            for tags in self._iter_table_entries_as_tags():
                tags.write(stream)

        def epilogue():
            stream.write('  0\nENDTAB\n')

        prologue()
        content()
        epilogue()

    def _update_meta_data(self):
        count = len(self)
        if self._drawing.dxfversion > 'AC1009':
            self._table_header.subclass['AcDbSymbolTable'].update(70, count)
        else:
            self._table_header.update(70, count)

class ViewportTable(Table):
    ## TODO: Viewport-Table can have multiple entries with same name
    def create(self, name, attribs=None):
        if attribs is None:
            attribs = {}
        attribs['name'] = name
        return self.new_entry(attribs)
