# Generated by Django 5.1.5 on 2025-04-11 16:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('group', models.CharField(blank=True, max_length=255, null=True)),
                ('deadline', models.DateField(null=True)),
                ('start_duration', models.TimeField(null=True)),
                ('end_duration', models.TimeField(null=True)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to=settings.AUTH_USER_MODEL)),
                ('seen_by', models.ManyToManyField(blank=True, related_name='seen_exams', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExamQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('is_mcq', models.BooleanField(default=False)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examquestions', to='exam.exam')),
            ],
        ),
        migrations.CreateModel(
            name='ExamMCQOptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examoptions', to='exam.examquestion')),
            ],
        ),
        migrations.CreateModel(
            name='ExamSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('mcq_answers', models.JSONField(blank=True, null=True)),
                ('descriptive_answers', models.JSONField(blank=True, null=True)),
                ('uploaded_files', models.FileField(blank=True, null=True, upload_to='uploads/')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examsubmissions', to='exam.exam')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
