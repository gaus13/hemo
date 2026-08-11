from app.models.donor import DonorProfile
from app.schemas.donor import DonorProfileResponse


def donor_to_response(donor: DonorProfile) -> DonorProfileResponse:
    latitude = None
    longitude = None

    if donor.location is not None:
        latitude = donor.location.y
        longitude = donor.location.x

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