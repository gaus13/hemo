from app.models.bloodrequest import BloodRequest
from app.schemas.bloodRequest import BloodRequestResponse
from app.services.location_service import get_coordinates


def blood_request_to_response(
    blood_request: BloodRequest,
) -> BloodRequestResponse:

    latitude = None
    longitude = None

    if blood_request.location is not None:
        latitude, longitude = get_coordinates(
            blood_request.location
        )

    return BloodRequestResponse(
        id=blood_request.id,
        requester_id=blood_request.requester_id,
        blood_group=blood_request.blood_group,
        units_required=blood_request.units_required,
        hospital_name=blood_request.hospital_name,
        hospital_address=blood_request.hospital_address,
        city=blood_request.city,
        urgency=blood_request.urgency,
        required_by=blood_request.required_by,
        remarks=blood_request.remarks,
        status=blood_request.status,
        created_at=blood_request.created_at,
        patient_name=blood_request.patient_name,
        relationship_to_patient=blood_request.relationship_to_patient,
        latitude=latitude,
        longitude=longitude,
    )