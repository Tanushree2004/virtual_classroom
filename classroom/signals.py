from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Classroom, ClassroomResource
from resource_library.models import Category, Resource

@receiver(post_save, sender=Classroom)
def create_category_for_new_classroom(sender, instance, created, **kwargs):
    if created:
        Category.objects.get_or_create(name=instance.title, classroom=instance)

@receiver(post_save, sender=ClassroomResource)
def sync_classroom_resource_to_library(sender, instance, created, **kwargs):
    if created:
        category, _ = Category.objects.get_or_create(name=instance.classroom.title)
        if instance.resource_type == 'file' and instance.file:
            Resource.objects.create(
                title=instance.title,
                category=category,
                file=instance.file,
                user=instance.uploaded_by
            )

@receiver(post_delete, sender=ClassroomResource)
def delete_classroom_resource_from_library(sender, instance, **kwargs):
    try:
        category = Category.objects.get(name=instance.classroom.title)
        resource = Resource.objects.get(title=instance.title, category=category, user=instance.uploaded_by)
        resource.delete()
    except Resource.DoesNotExist:
        pass
