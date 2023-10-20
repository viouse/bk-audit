# Generated by Django 3.2.12 on 2023-02-28 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("databus", "0005_auto_20230105_1002"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collectorconfig",
            name="collector_plugin_id",
            field=models.IntegerField(db_index=True, verbose_name="BK-LOG 采集插件ID"),
        ),
        migrations.AlterField(
            model_name="collectorconfig",
            name="custom_type",
            field=models.CharField(
                choices=[("log", "容器日志上报"), ("otlp_trace", "otlpTrace上报"), ("otlp_log", "otlp日志上报")],
                db_index=True,
                default="log",
                max_length=30,
                verbose_name="自定义类型",
            ),
        ),
        migrations.AlterIndexTogether(
            name="collectorconfig",
            index_together={("system_id", "custom_type")},
        ),
    ]