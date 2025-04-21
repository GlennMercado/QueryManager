def is_image_file(attachment):
    """Check if the attachment is an image file based on its extension."""
    if attachment and attachment.name:
        return attachment.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    return False