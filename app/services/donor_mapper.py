from app.models.donor import DonorProfile
from app.schemas.donor import DonorProfileResponse
from app.services.location_service import get_coordinates
from app.schemas.matching import DonorMatchResponse


def donor_to_response(donor: DonorProfile) -> DonorProfileResponse:
    latitude = None
    longitude = None

    if donor.location is not None:
        latitude, longitude = get_coordinates(donor.location)

    return DonorProfileResponse(
        id=donor.id,
        full_name=donor.full_name,
        phone=donor.phone,
        blood_group=donor.blood_group,
        gender=donor.gender,
        date_of_birth=donor.date_of_birth,
        weight=donor.weight,
        city=donor.city,
        state=donor.state,
        latitude=latitude,
        longitude=longitude,
        is_available=donor.is_available,
        created_at=donor.created_at,
    )

"""What this function does,, 
PostgreSQL / SQLAlchemy
        ↓
DonorProfile
location = POINT(longitude, latitude)
        ↓
donor_to_response()
        ↓
DonorProfileResponse
latitude
longitude"""

def donor_match_to_response(
        donor,
        distance_km,       
) -> DonorMatchResponse:

    return DonorMatchResponse(
        donor_id=donor.id,
        full_name=donor.full_name,
        blood_group=donor.blood_group,
        city=donor.city,
        state=donor.state,
        distance_km=round(float(distance_km), 2),
    )