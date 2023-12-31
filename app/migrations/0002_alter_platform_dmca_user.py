# Generated by Django 4.2 on 2023-07-09 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform',
            name='dmca',
            field=models.TextField(blank=True, default='\n            <br>\n            PapyStreaming .forum respecte la propriété intellectuelle d\'autrui et prend les questions de propriété intellectuelle très au sérieux et s’engage à répondre aux besoins des propriétaires de contenu tout en les aidant à gérer la publication de leur contenu en ligne.\n            <br>\n            <br>\n            Si vous pensez que votre travail protégé par un droit d\'auteur a été copié de manière à constituer une violation du droit d\'auteur et qu\'il est accessible sur ce site, vous pouvez en informer notre agent des droits d\'auteur, comme indiqué dans la loi DMCA (Digital Millennium Copyright Act of 1998). Pour que votre réclamation soit valide en vertu de la DMCA, vous devez fournir les informations suivantes lors de l\'envoi d\'un avis d\'infraction au droit d\'auteur:\n            <br>\n            <br>\n            Signature physique ou électronique d\'une personne autorisée à agir au nom du titulaire du droit d\'auteur Identification de l\'œuvre protégée qui aurait été violée\n            <br>\n            <br>\n            Identification du matériel présumé contrefaisant ou faisant l\'objet de l\'activité illicite et devant être enlevé\n            <br>\n            <br>\n            Informations raisonnablement suffisantes pour permettre au fournisseur de services de contacter la partie plaignante, telles qu\'une adresse, un numéro de téléphone et, le cas échéant, une adresse de courrier électronique\n            <br>\n            <br>\n            Une déclaration indiquant que la partie plaignante "croit de bonne foi que l\'utilisation du matériel de la manière incriminée n\'est pas autorisée par le titulaire du droit d\'auteur, son mandataire ou la loi"\n            <br>\n            <br>\n            Une déclaration selon laquelle "les informations figurant dans la notification sont exactes" et "sous peine de parjure, la partie plaignante est autorisée à agir au nom du titulaire d\'un droit exclusif prétendument violé"\n            <br>\n            <br>\n            Les informations ci-dessus doivent être envoyées par notification écrite, télécopiée ou par courrier électronique à l\'agent désigné suivant:\n            <br>\n            <br>\n            Attention: bureau DMCA\n            <br>\n            <br>\n            Contactez nous:\n            <br>\n            <br>\n            sapystreamingdmca@gmail.com\n            <br>\n            <br>\n            Ces informations ne doivent pas être interprétées comme des conseils juridiques. Pour plus d\'informations sur les informations requises pour les notifications DMCA valides, voir 17 États-Unis d\'Amérique. 512 (c) (3).\n        ', null=True),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('type', models.IntegerField(choices=[(0, 'Visitor'), (1, 'Movies Admin'), (2, 'Series Admin'), (3, 'Admin'), (4, 'Super Admin')], default=0)),
                ('password', models.CharField(max_length=255)),
                ('xp', models.FloatField(default=0.0)),
                ('prize', models.FloatField(default=0.0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(auto_now_add=True, null=True)),
                ('platform', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='app.platform')),
            ],
        ),
    ]
