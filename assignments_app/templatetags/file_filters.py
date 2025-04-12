from django import template
import os

register = template.Library()

@register.filter
def file_icon(extension):
    """Returns FontAwesome class for file extension."""
    icons = {
        "pdf": "fa-solid fa-file-pdf",
        "doc": "fa-solid fa-file-word",
        "docx": "fa-solid fa-file-word",
        "txt": "fa-solid fa-file-word",
        "ppt": "fa-solid fa-file-powerpoint",
        "pptx": "fa-solid fa-file-powerpoint",
        "xls": "fa-solid fa-file-excel",
        "xlsx": "fa-solid fa-file-excel",
        "zip": "fa-solid fa-file-archive",
        "rar": "fa-solid fa-file-archive",
        "jpg": "fa-solid fa-file-image",
        "jpeg": "fa-solid fa-file-image",
        "png": "fa-solid fa-file-image",
        "gif": "fa-solid fa-file-image",
        "mp3": "fa-solid fa-file-audio",
        "wav": "fa-solid fa-file-audio",
        "mp4": "fa-solid fa-file-video",
        "avi": "fa-solid fa-file-video",
        "exe": "fa-solid fa-triangle-exclamation text-danger",
        "css": "fa-solid fa-code",
        "py": "fa-solid fa-code",
        "html": "fa-solid fa-code",
        "js": "fa-solid fa-code",
        "c": "fa-solid fa-code",
        "cpp": "fa-solid fa-code",
        
    }
    return icons.get(extension, "fa-solid fa-file")  # Default icon

@register.filter
def basename(value):
    return os.path.basename(value)