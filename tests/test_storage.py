from pathlib import Path

from app.services.storage import upload_property_image


file_path = Path("test.jpg")

with open(file_path, "rb") as file:
    file_content = file.read()


result = upload_property_image(
    file_content=file_content,
    file_path="test/test-2.jpg",
    content_type="image/jpeg",
)

print(result)