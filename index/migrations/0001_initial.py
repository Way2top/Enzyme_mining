# Generated by Django 3.2 on 2025-03-20 01:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FastaFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='文件名称')),
                ('description', models.TextField(blank=True, null=True, verbose_name='文件描述')),
                ('file_path', models.CharField(max_length=255, verbose_name='文件路径')),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='上传时间')),
            ],
            options={
                'verbose_name': 'FASTA文件',
                'verbose_name_plural': 'FASTA文件',
            },
        ),
        migrations.CreateModel(
            name='VisitLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP地址')),
                ('user_agent', models.TextField(verbose_name='用户代理')),
                ('visit_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='访问时间')),
                ('viewed_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='index.fastafile', verbose_name='查看的文件')),
            ],
            options={
                'verbose_name': '访问记录',
                'verbose_name_plural': '访问记录',
            },
        ),
    ]
