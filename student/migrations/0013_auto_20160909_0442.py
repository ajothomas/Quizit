# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-09 04:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0012_student_answer_log'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student_answer_log',
            old_name='activityTimestamp',
            new_name='answerTimestamp',
        ),
        migrations.RemoveField(
            model_name='student_answer_log',
            name='course',
        ),
        migrations.AddField(
            model_name='student_answer_log',
            name='activityFK',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='student.Student_Answers_ActivityLog'),
        ),
        migrations.AddField(
            model_name='student_answer_log',
            name='answerFlag',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='student_answers_activitylog',
            name='source',
            field=models.CharField(default='Old', max_length=200),
        ),
    ]