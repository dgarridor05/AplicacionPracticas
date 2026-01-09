from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0005_alter_option_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Option',
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=1)),
                ('value', models.IntegerField(default=1)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='quizzes.question')),
            ],
        ),
    ]
