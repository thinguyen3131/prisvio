from prismvio.utils.firebase.firebase_admin import FirebaseAdminService

firebase_admin_service = None


def get_firebase_admin_service() -> FirebaseAdminService:
    global firebase_admin_service
    if firebase_admin_service is None:
        firebase_admin_service = FirebaseAdminService()

    return firebase_admin_service
