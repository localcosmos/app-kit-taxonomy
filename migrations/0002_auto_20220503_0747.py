# Generated by Django 3.1.14 on 2022-05-03 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metavernacularnames',
            name='taxon_source',
            field=models.CharField(choices=[('taxonomy.sources.col', 'Catalogue Of Life 2019'), ('taxonomy.sources.algaebase', 'AlgaeBase 2020'), ('taxonomy.sources.custom', 'Custom Taxa')], max_length=255),
        ),
    ]
