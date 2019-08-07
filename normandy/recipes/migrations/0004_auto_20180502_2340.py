# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-02 23:40
# flake8: noqa
from __future__ import unicode_literals

import hashlib

from django.db import migrations


def create_tmp_from_revision(apps, revision, parent=None):
    ApprovalRequest = apps.get_model("recipes", "ApprovalRequest")
    TmpRecipeRevision = apps.get_model("recipes", "TmpRecipeRevision")

    tmp = TmpRecipeRevision(
        created=revision.created,
        updated=revision.updated,
        comment=revision.comment,
        name=revision.name,
        arguments_json=revision.arguments_json,
        extra_filter_expression=revision.extra_filter_expression,
        identicon_seed=revision.identicon_seed,
        action=revision.action,
        parent=parent,
        recipe=revision.recipe,
        user=revision.user,
    )

    tmp.save()

    if revision.approved_for_recipe.count():
        tmp.approved_for_recipe.add(revision.approved_for_recipe.get())

    if revision.latest_for_recipe.count():
        tmp.latest_for_recipe.add(revision.latest_for_recipe.get())

    try:
        approval_request = revision.approval_request
        approval_request.tmp_revision = tmp
        approval_request.save()
    except ApprovalRequest.DoesNotExist:
        pass

    for channel in revision.channels.all():
        tmp.channels.add(channel)

    for country in revision.countries.all():
        tmp.countries.add(country)

    for locale in revision.locales.all():
        tmp.locales.add(locale)

    return tmp


def copy_revisions_to_tmp(apps, schema_editor):
    RecipeRevision = apps.get_model("recipes", "RecipeRevision")

    for revision in RecipeRevision.objects.filter(parent=None):
        current_rev = revision
        parent_tmp = create_tmp_from_revision(apps, current_rev)

        try:
            while current_rev.child:
                parent_tmp = create_tmp_from_revision(apps, current_rev.child, parent=parent_tmp)
                current_rev = current_rev.child
        except RecipeRevision.DoesNotExist:
            pass


def get_filter_expression(revision):
    parts = []

    if revision.locales.count():
        locales = ", ".join(["'{}'".format(l.code) for l in revision.locales.all()])
        parts.append("normandy.locale in [{}]".format(locales))

    if revision.countries.count():
        countries = ", ".join(["'{}'".format(c.code) for c in revision.countries.all()])
        parts.append("normandy.country in [{}]".format(countries))

    if revision.channels.count():
        channels = ", ".join(["'{}'".format(c.slug) for c in revision.channels.all()])
        parts.append("normandy.channel in [{}]".format(channels))

    if revision.extra_filter_expression:
        parts.append(revision.extra_filter_expression)

    expression = ") && (".join(parts)

    return "({})".format(expression) if len(parts) > 1 else expression


def hash(revision):
    data = "{}{}{}{}{}{}".format(
        revision.recipe.id,
        revision.created,
        revision.name,
        revision.action.id,
        revision.arguments_json,
        get_filter_expression(revision),
    )
    return hashlib.sha256(data.encode()).hexdigest()


def create_revision_from_tmp(apps, tmp, parent=None):
    ApprovalRequest = apps.get_model("recipes", "ApprovalRequest")
    RecipeRevision = apps.get_model("recipes", "RecipeRevision")

    rev = RecipeRevision(
        created=tmp.created,
        updated=tmp.updated,
        comment=tmp.comment,
        name=tmp.name,
        arguments_json=tmp.arguments_json,
        extra_filter_expression=tmp.extra_filter_expression,
        identicon_seed=tmp.identicon_seed,
        action=tmp.action,
        parent=parent,
        recipe=tmp.recipe,
        user=tmp.user,
    )

    initial_id = hash(tmp)
    rev.id = initial_id

    rev.save()

    if tmp.approved_for_recipe.count():
        rev.approved_for_recipe.add(tmp.approved_for_recipe.get())

    if tmp.latest_for_recipe.count():
        rev.latest_for_recipe.add(tmp.latest_for_recipe.get())

    try:
        approval_request = tmp.approval_request
        approval_request.revision = rev
        approval_request.save()
    except ApprovalRequest.DoesNotExist:
        pass

    for channel in tmp.channels.all():
        rev.channels.add(channel)

    for country in tmp.countries.all():
        rev.countries.add(country)

    for locale in tmp.locales.all():
        rev.locales.add(locale)

    return rev


def copy_tmp_to_revisions(apps, schema_editor):
    TmpRecipeRevision = apps.get_model("recipes", "TmpRecipeRevision")

    for tmp in TmpRecipeRevision.objects.filter(parent=None):
        current_tmp = tmp
        parent_rev = create_revision_from_tmp(apps, current_tmp)

        try:
            while current_tmp.child:
                parent_rev = create_revision_from_tmp(apps, current_tmp.child, parent=parent_rev)
                current_tmp = current_tmp.child
        except TmpRecipeRevision.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [("recipes", "0003_tmpreciperevision")]

    operations = [migrations.RunPython(copy_revisions_to_tmp, copy_tmp_to_revisions)]