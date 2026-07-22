import enum


class BloodGroup(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class RequestUrgency(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RequestStatus(str, enum.Enum):

    ACTIVE = "ACTIVE"

    DONOR_MATCHED = "DONOR_MATCHED"

    DONATION_IN_PROGRESS = "DONATION_IN_PROGRESS"

    DONATION_VERIFIED = "DONATION_VERIFIED"

    COMPLETED = "COMPLETED"

    CANCELLED = "CANCELLED"


class VolunteerStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"

class RelationshipType(str, enum.Enum):

    FAMILY = "family"

    FRIEND = "friend"

    COLLEAGUE = "colleague"

    NGO = "ngo"

    OTHER = "other"