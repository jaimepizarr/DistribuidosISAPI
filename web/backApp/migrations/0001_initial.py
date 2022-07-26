# Generated by Django 3.1.1 on 2021-10-21 01:04

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('number_id', models.CharField(max_length=10)),
                ('is_operador', models.BooleanField(default=False, verbose_name='Es un operador')),
                ('is_motorizado', models.BooleanField(default=False, verbose_name='Es un motorizado')),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='images/profiles/')),
                ('birth_date', models.DateField(null=True)),
                ('gender', models.CharField(max_length=4, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_number', models.CharField(max_length=10, null=True, verbose_name='id number of Client')),
                ('name', models.CharField(max_length=50, verbose_name='Client name')),
                ('apellido', models.CharField(max_length=50, verbose_name='Client last name')),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='Client email')),
            ],
        ),
        migrations.CreateModel(
            name='ColorVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=15, unique=True, verbose_name='Color of car')),
            ],
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('ruc', models.CharField(max_length=15, primary_key=True, serialize=False, verbose_name='Local RUC')),
                ('password', models.CharField(max_length=128, verbose_name='Local Password')),
                ('name', models.CharField(max_length=20, verbose_name='Local name')),
                ('email', models.EmailField(max_length=254, verbose_name='Local email')),
                ('logo_img', models.ImageField(blank=True, null=True, upload_to='images/Locals/logos', verbose_name='Logo image')),
                ('reg_date', models.DateField(auto_now_add=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('reference', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('map_name', models.CharField(max_length=15, verbose_name='Name of the table map.')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('details', models.CharField(max_length=100, verbose_name='Details of the order')),
                ('price', models.FloatField(verbose_name='Order price')),
                ('delivery_price', models.FloatField(null=True, verbose_name='Delivery price')),
                ('state', models.PositiveSmallIntegerField(null=True, verbose_name='State of the order')),
                ('start_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date and hour that the order is received by us')),
                ('mot_assigned_time', models.DateTimeField(null=True, verbose_name='Time the order has been assigned to a motorizado')),
                ('deliv_start_time', models.DateTimeField(null=True, verbose_name='Time the order begins its delivery')),
                ('arriv_estimated_time', models.DateTimeField(null=True, verbose_name='Arrival Estimated Time')),
                ('real_arriv_time', models.DateTimeField(null=True, verbose_name='Real arrival time')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is paid')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backApp.client')),
                ('destiny_loc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backApp.location')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.local')),
                ('operador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='OrderOperador', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(max_length=50, verbose_name='Type of payment')),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pho_number', models.CharField(max_length=11)),
            ],
        ),
        migrations.CreateModel(
            name='RegErrorType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Error type')),
            ],
        ),
        migrations.CreateModel(
            name='TypeVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_vehicle', models.CharField(max_length=15, unique=True, verbose_name='Type of vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='Motorizado',
            fields=[
                ('user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='backApp.user')),
                ('is_busy', models.BooleanField(default=False, verbose_name='')),
                ('isOnline', models.BooleanField(default=False, verbose_name='')),
                ('id_front_photo', models.ImageField(upload_to='images/ids/', verbose_name='Front photo of id')),
                ('id_back_photo', models.ImageField(upload_to='images/ids/', verbose_name='Back photo of id')),
                ('license_front_photo', models.ImageField(upload_to='images/licenses/', verbose_name='Front license photo')),
                ('license_back_photo', models.ImageField(upload_to='images/licenses/', verbose_name='Back license photo')),
                ('phone_number', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector_name', models.CharField(max_length=15, verbose_name='Name of the sector')),
                ('limits', models.TextField(verbose_name='Coordinates defining the limits of this sector')),
                ('map_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.map')),
            ],
        ),
        migrations.CreateModel(
            name='PhoneLocal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idPhone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.phone')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.local')),
            ],
        ),
        migrations.CreateModel(
            name='PhoneClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.client')),
                ('idPhone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.phone')),
            ],
        ),
        migrations.CreateModel(
            name='OrderComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='Comments about the delivery of the order')),
                ('grade', models.FloatField(verbose_name='Delivery grading')),
                ('idOrder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backApp.payment'),
        ),
        migrations.CreateModel(
            name='MotValidation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Operador', to=settings.AUTH_USER_MODEL)),
                ('motorizado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Motorizado', to='backApp.motorizado')),
            ],
        ),
        migrations.CreateModel(
            name='MotRegistComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='Comment about the error in register')),
                ('error', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backApp.regerrortype')),
                ('validation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.motvalidation')),
            ],
        ),
        migrations.CreateModel(
            name='ModelsVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=15, unique=True, verbose_name='Model of vehicle')),
                ('type_vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.typevehicle')),
            ],
        ),
        migrations.CreateModel(
            name='LocalSector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(verbose_name='Price set by the Local for the Sector')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.local')),
                ('sector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.sector')),
            ],
        ),
        migrations.CreateModel(
            name='LocalKM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('km_max', models.FloatField(verbose_name='Maximum Kilometer of delivery')),
                ('price_km', models.FloatField(verbose_name='Price per km')),
                ('km_min', models.FloatField(verbose_name='Maximum Kilometer of delivery')),
                ('price_min', models.FloatField(verbose_name='Min price to charge')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.local')),
            ],
        ),
        migrations.AddField(
            model_name='local',
            name='location_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='backApp.location'),
        ),
        migrations.AddField(
            model_name='user',
            name='home_loc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backApp.location'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Year of bought')),
                ('plate_number', models.CharField(max_length=10, verbose_name='Number of the car plate')),
                ('plate_photo', models.ImageField(upload_to='images/plates', verbose_name='Plate photo')),
                ('right_photo', models.ImageField(upload_to='images/vehicles/', verbose_name='Right photo of the vehicle')),
                ('left_photo', models.ImageField(upload_to='images/vehicles/', verbose_name='Left photo of the vehicle')),
                ('front_photo', models.ImageField(upload_to='images/vehicles/', verbose_name='Front photo of the vehicle')),
                ('back_photo', models.ImageField(upload_to='images/vehicles/', verbose_name='Back photo of the vehicle')),
                ('front_regis_photo', models.ImageField(upload_to='images/registrations/', verbose_name='Registration Front Photo')),
                ('back_regis_photo', models.ImageField(upload_to='images/registrations/', verbose_name='Registration back Photo')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.colorvehicle')),
                ('type_vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.typevehicle')),
                ('veh_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.modelsvehicle')),
                ('motorizado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backApp.motorizado')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='motorizado',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='OrderMotorizado', to='backApp.motorizado'),
        ),
    ]
