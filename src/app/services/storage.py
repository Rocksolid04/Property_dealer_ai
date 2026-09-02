from supabase import create_client

from app.core.config import settings


supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY,
)


BUCKET_NAME = "property-images"


def upload_property_image(
    file_content: bytes,
    file_path: str,
    content_type: str,
) -> dict:
    response = supabase.storage.from_(BUCKET_NAME).upload(
        path=file_path,
        file=file_content,
        file_options={
            "content-type": content_type,
        },
    )

    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(
        file_path
    )

    return {
        "storage_path": file_path,
        "public_url": public_url,
    }

def delete_property_image(
    file_path: str,
):
    return supabase.storage.from_(BUCKET_NAME).remove(
        [file_path]
    )