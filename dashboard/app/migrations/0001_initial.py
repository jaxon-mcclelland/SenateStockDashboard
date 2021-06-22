# Generated by Django 3.2.4 on 2021-06-22 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='transactions',
            fields=[
                ('transaction_date', models.DateTimeField()),
                ('position', models.TextField()),
                ('name', models.TextField()),
                ('party', models.TextField()),
                ('state', models.TextField()),
                ('symbol', models.TextField()),
                ('transaction_type', models.TextField()),
                ('index', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'transactions',
            },
        ),
    ]