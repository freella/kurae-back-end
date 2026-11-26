from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='name',
            field=models.CharField(max_length=120),
        ),
        migrations.AddField(
            model_name='lead',
            name='message',
            field=models.TextField(blank=True, default='', max_length=2000),
        ),
        migrations.AddField(
            model_name='lead',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='lead',
            name='privacy_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lead',
            name='privacy_policy_version',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
    ]
