# Generated by Django 2.1.7 on 2020-08-19 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SemanticData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('thing', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('property', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('value', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('table', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('key', models.IntegerField(blank=True, default=None, help_text='id for this data in the table from table column', null=True)),
            ],
            options={
                'db_table': 'semantic_data',
            },
        ),
    ]