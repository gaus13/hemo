from app.models.enums import BloodGroup

BLOOD_COMPATIBILITY = {
    BloodGroup.O_NEGATIVE: [
        BloodGroup.O_NEGATIVE,
    ],
    BloodGroup.O_POSITIVE: [
        BloodGroup.O_NEGATIVE,
        BloodGroup.O_POSITIVE,
    ],
    BloodGroup.A_NEGATIVE: [
        BloodGroup.O_NEGATIVE,
        BloodGroup.A_NEGATIVE,
    ],
    BloodGroup.A_POSITIVE: [
        BloodGroup.O_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.A_NEGATIVE,
        BloodGroup.A_POSITIVE,
    ],
    BloodGroup.B_NEGATIVE: [
        BloodGroup.O_NEGATIVE,
        BloodGroup.B_NEGATIVE,
    ],
    BloodGroup.B_POSITIVE: [
        BloodGroup.O_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.B_POSITIVE,
    ],
    BloodGroup.AB_NEGATIVE: [
        BloodGroup.O_NEGATIVE,
        BloodGroup.A_NEGATIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.AB_NEGATIVE,
    ],
    BloodGroup.AB_POSITIVE: [
        BloodGroup.O_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.A_NEGATIVE,
        BloodGroup.A_POSITIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.B_POSITIVE,
        BloodGroup.AB_NEGATIVE,
        BloodGroup.AB_POSITIVE,
    ],
}


def get_compatible_blood_groups(
    requested_group: BloodGroup,
) -> list[BloodGroup]:

    return BLOOD_COMPATIBILITY[requested_group]
