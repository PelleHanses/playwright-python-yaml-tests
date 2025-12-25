ACTIONS = {}

def upload_file(page, context, payload):
    page.set_input_files(
        payload["selector"],
        payload["path"]
    )

ACTIONS["upload_file"] = upload_file
