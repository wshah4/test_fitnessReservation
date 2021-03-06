# Generated by Django 3.1.3 on 2021-02-01 21:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_auto_20210201_1628'),
        ('fitnessClass', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaitList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wait', models.CharField(max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classDate', models.DateField(default=None)),
                ('reservationStatus', models.CharField(default=None, max_length=20)),
                ('reservationDate', models.DateField(default=None)),
                ('reservationTime', models.TimeField(default=None)),
                ('waitNumber', models.IntegerField(default='0')),
                ('classReserved', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='fitnessClass.fitnessclass')),
                ('customerReserving', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='accounts.customer')),
            ],
        ),
    ]
