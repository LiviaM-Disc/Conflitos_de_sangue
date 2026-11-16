from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("ranking_app", "0002_gameresult_completed_gameresult_phase")]
    operations = [migrations.AddField(model_name="gameresult", name="campaign",
                                     field=models.CharField(default="classic", max_length=16))]
