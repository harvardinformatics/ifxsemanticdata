
# -*- coding: utf-8 -*-

'''
migrate data from semantic_data table into other app tables using
migrate_config.py
'''
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import models
from django.apps import apps
from ifxsemanticdata.models import SemanticData
from datetime import datetime
import time
import pytz
import re
import json

# old table name to new model name
# only need to be listed if they:
#   require a name change,
#   function for the value,
#   type other than string
table_map = {
    # 'old_table_name': 'new_table_name'
}

# common new column names
# only need to be listed if they:
#   require a name change,
#   function for the value,
#   type other than string
base_col_map = {
    'date_modified': {'type': 'datetime'},
    'date_created': {'type': 'datetime'}
}

# by old table, list of new columns
# only need to be listed if they:
#   require a name change {old_name},
#   value is constant {val},
#   function for the value {func},
#   type other than string (type}
col_maps = {
    """'Helium_Node':{
        'credit_code': {'old_name': 'Credit_Expense_Code'},
        'active': {'val': 1}
    }"""
}

"""
Functions for column value translation
custom functions for any app can be added
"""

def times_10(row, col, info):
    val = re.sub('[^0-9.]+', '', row[col])
    return int(float(val) * 10)

def get_fk(row, col, info):
    pk = None
    model = apps.get_model(target_app, info['fk_model'])
    if 'fk_value' in info:
        val =  globals()[info['fk_value']](row, col, info)
    else:
        val = row[col]
    filter = {info['fk_field']: val}
    exists = model.objects.filter(**filter)
    if len(exists) == 1:
        pk = exists[0].id
    return pk


class Command(BaseCommand):
    '''
    find the data types in semantic_data and split them into new tables and
    models
    '''
    help = 'Takes list of types in semantic_data and splits them into new' +  \
    'tables and models. Pass in the create flag to actually do the creation,' + \
    'otherwise what would be created is just output. Usage:\n' + \
        './manage.py migrateSemanticData --thing Helium_Node --create'

    def add_arguments(self, parser):
        # allow multiple thing args
        parser.add_argument('app', help='the name of the app which contains the models you want to migrate data to')
        parser.add_argument('--thing', action='append', help='a semantic type to pivot into a new table and model')
        parser.add_argument('--create', action='store_true', help='create the table rather than just outputing what whould be created')
        parser.add_argument('--since', help='only move data created since, date (YYYY-MM-DD)')

    def handle(self, *args, **options):
        create = False
        since = False
        global target_app
        target_app = options['app']
        config = __import__('%s.%s' % (target_app, 'ifxsemanticdata_config'), globals(), locals())
        config = config.ifxsemanticdata_config
        # set the default config maps
        self.table_map = table_map
        self.base_col_map = base_col_map
        self.col_maps = col_maps
        # add custom config to default config variables
        self.customize_config(config)
        if options['create']:
            create = True
        if options['since']:
            since = int(datetime.strptime(options['since'], '%Y-%m-%d').timestamp())
        semantic_data_model = apps.get_model('ifxsemanticdata', 'SemanticData')
        for thing in options['thing']:
            data, cols = self.get_pivoted_data(thing)
            model_name = self.get_model_name(thing)
            model = apps.get_model(target_app, model_name)
            col_map = self.col_maps[thing] if thing in self.col_maps else {}
            for k, row in data.items():
                # skip data before since, if provided
                if since and 'Date_Modified' in row and int(row['Date_Modified']) < since:
                    continue
                row_dict = self.get_insert_vals(row, model, col_map)
                pk = self.add_instance(model, row_dict, create)
                if pk:
                    semantic_data_model.objects.filter(id__in=row['ids']).update(table=model_name, key=pk)
                    print('Updated semantic_data with table, key (%s/ %s) for ids: %s' % (model_name, str(pk), json.dumps(row['ids'])))

    def customize_config(self, custom):
        if hasattr(custom, 'table_map'):
            self.table_map = custom.table_map
        if hasattr(custom, 'col_maps'):
            self.col_maps = custom.col_maps
        if hasattr(custom, 'base_col_map'):
            self.base_col_map.update(custom.base_col_map)

    def get_pivoted_data(self, thing):
        rows = SemanticData.objects.filter(thing=thing)
        cols = [a['property'] for a in rows.values('property').distinct()]
        data = {}
        for row in rows:
            if row.name not in data:
                data[row.name] = {a: '' for a in cols}
                data[row.name]['ids'] = []
            data[row.name]['ids'].append(row.id)
            data[row.name][row.property] = row.value
        return data, cols

    def get_model_name(self, thing):
        if thing in self.table_map:
            new_name = self.table_map[thing]
        else:
            new_name = self.snake_to_camel(thing)
        return new_name

    def get_old_col_name(self, name, field_map):
        if 'old_name' in field_map:
            old_name = field_map['old_name']
        else:
            old_name = self.snake_caps(name)
        return old_name

    def get_new_col_val(self, old_col, new_col, row, field_map):
        if 'val' in field_map:
            new_val = field_map['val']
        elif 'func' in field_map:
            func_name = field_map['func']
            new_val =  globals()[func_name](row, old_col, field_map)
        else:
            new_val = row[old_col]
        if 'type' in field_map:
            if field_map['type'] == 'datetime':
                new_val = self.str_to_date(new_val)
            elif field_map['type'] == 'int':
                if not new_val:
                    new_val = 0
                new_val = int(float(new_val))
        return new_val

    def get_field_map(self, new_col, col_map):
        field_map = {}
        if new_col in col_map:
            field_map = col_map[new_col]
        elif new_col in self.base_col_map:
            field_map = self.base_col_map[new_col]
        return field_map

    def get_insert_vals(self, row, model, col_map):
        vals = {}
        for field in model._meta.fields:
            if field.name in ['id', 'date_modified']:
                continue
            field_map = self.get_field_map(field.name, col_map)
            name = field.name
            # this is a little hack to make django insert the int rather than
            # the model instance for fks, that way we can still use json.dumps
            if 'fk_model' in field_map:
                name = '%s_id' % name
            old_col = self.get_old_col_name(field.name, field_map)
            new_val = self.get_new_col_val(old_col, field.name, row, field_map)
            vals[name] = new_val
        return vals

    def add_instance(self, model, data, create):
        id = None
        # check if dupliate data exists
        exists = model.objects.filter(**data)
        if exists:
            for res in exists:
                print('Skipping existing row: %s, %s' % (str(res.id), json.dumps(data)))
        else: # insert row
            if create:
                inst = model(**data)
                inst.save()
                id = inst.id
                print('Inserted row: %s, %s' % (str(id), json.dumps(data)))
            else:
                print('Would be inserted row: %s' % json.dumps(data))
        return id

    @staticmethod
    def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
        """
        Create specified model
        """
        class Meta:
            # Using type('Meta', ...) gives a dictproxy error during model creation
            pass

        if app_label:
            # app_label must be set using the Meta inner class
            setattr(Meta, 'app_label', app_label)

        # Update Meta with any options that were provided
        if options is not None:
            for key, value in options.iteritems():
                setattr(Meta, key, value)

        # Set up a dictionary to simulate declarations within a class
        attrs = {'__module__': module, 'Meta': Meta}

        # Add in any fields that were provided
        if fields:
            attrs.update(fields)

        # Create the class, which automatically triggers ModelBase processing
        model = type(name, (models.Model,), attrs)

        # Create an Admin class if admin options were provided
        if admin_opts is not None:
            class Admin(admin.ModelAdmin):
                pass
            for key, value in admin_opts:
                setattr(Admin, key, value)
            admin.site.register(model, Admin)
        return model

    @staticmethod
    def str_to_date(date_str):
        if '-' in date_str:
            date_format = '%Y-%m-%d'
            # clean up some dates that have _ and min and sec
            date_str = date_str.replace('_', ' ')
            date_str = date_str.split()[0]
            date = datetime.fromtimestamp(time.mktime(time.strptime(date_str, date_format)))
        elif '/' in date_str:
            date_format = '%m/%d/%y'
            date = datetime.fromtimestamp(time.mktime(time.strptime(date_str, date_format)))
        else:
            date = datetime.fromtimestamp(int(date_str))
        # localize date to EST
        # return as a string to prevent errors in json serializing when printed
        date = str(pytz.timezone('EST').localize(date))
        return date

    @staticmethod
    def snake_to_camel(word):
        return ''.join(x.capitalize() or '_' for x in word.split('_'))

    @staticmethod
    def camel_to_snake(word):
        return ''.join('_' + i if i.isupper() else i for i in word).lstrip('_')

    @staticmethod
    def snake_caps(word):
        return ''.join(x.capitalize() or '_' for x in re.split('(_)', word))
