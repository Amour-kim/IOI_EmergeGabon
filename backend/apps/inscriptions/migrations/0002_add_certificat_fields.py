from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificat',
            name='date_generation',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Date de génération'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificat',
            name='numero',
            field=models.CharField(
                default='',
                max_length=50,
                unique=True,
                verbose_name='Numéro du certificat'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificat',
            name='valide_jusqu_au',
            field=models.DateField(
                null=True,
                verbose_name="Date de fin de validité"
            ),
        ),
        migrations.AlterField(
            model_name='certificat',
            name='type_certificat',
            field=models.CharField(
                choices=[
                    ('SCOLARITE', 'Certificat de scolarité'),
                    ('INSCRIPTION', "Attestation d'inscription"),
                    ('CARTE', 'Carte étudiante'),
                ],
                max_length=20,
                verbose_name='Type de certificat'
            ),
        ),
        migrations.AlterField(
            model_name='certificat',
            name='fichier',
            field=models.FileField(
                upload_to='certificats/',
                verbose_name='Fichier PDF'
            ),
        ),
    ]
