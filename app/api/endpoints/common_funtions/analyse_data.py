async def process_analysis_result(result, file_name="unknown_file"):
    """
    Process and clean Azure Form Recognizer analysis result.
    - **result:** The analysis result from Azure Form Recognizer.
    - **file_name:** The name of the file being processed.
    """
    def clean_value(value):
        """
        Recursively clean a value by:
        - Removing `None` or `null` values.
        - Excluding unwanted keys like `spans`, `polygon`, `boundingRegions`.
        """
        if isinstance(value, dict):
            return {
                k: clean_value(v) for k, v in value.items()
                if v is not None and k not in ["spans", "polygon", "boundingRegions"]
            }
        elif isinstance(value, list):
            return [clean_value(v) for v in value if v is not None]
        else:
            return value

    extracted_data = {
        "apiVersion": "2023-07-31",
        "modelId": result.model_id if hasattr(result, 'model_id') else "unknown",
        "fileName": file_name,  # Include file name
        "documents": []
    }

    # Process each document in the result
    for document in result.documents:
        document_data = {"fields": []}

        for field_name, field in document.fields.items():
            field_entry = {
                "Name": field_name,
                "Type": field.value_type,
                "Content": getattr(field, 'content', None)
            }

            # Handle Items (Array of Objects)
            if field_name == "Items" and field.value_type == "list":
                field_entry["Type"] = "array"
                field_entry["Content"] = []

                for item in field.value:
                    if item.value is not None:
                        item_data = {
                            "type": "object",
                            "Rows": {}
                        }
                        for key, sub_field in item.value.items():
                            if key not in ["spans", "polygon", "boundingRegions"] and sub_field.value is not None:
                                item_data["Rows"][key] = {
                                    "type": sub_field.value_type,
                                    "content": getattr(sub_field, 'content', None)
                                }
                        field_entry["Content"].append(item_data)

            # Handle Address fields
            elif field.value_type == "address":
                field_entry["Type"] = "address"
                field_entry["Content"] = getattr(field, 'content', None)

            # Handle Nested Objects
            elif field.value_type == "object":
                field_entry["Type"] = "object"
                field_entry["Content"] = {
                    key: {
                        "type": sub_field.value_type,
                        "content": getattr(sub_field, 'content', None)
                    }
                    for key, sub_field in field.value.items()
                    if key not in ["spans", "polygon", "boundingRegions"]
                }

            # Generic Fields
            else:
                if field.value is not None:
                    field_entry["Content"] = getattr(field, 'content', None)

            # Append only if the Content is not None
            if field_entry["Content"] is not None:
                document_data["fields"].append(field_entry)

        # Remove top-level 'content' from each document
        document_data = clean_value(document_data)
        document_data.pop("content", None)

        # Append document only if fields exist
        if document_data["fields"]:
            extracted_data["documents"].append(document_data)

    return extracted_data
