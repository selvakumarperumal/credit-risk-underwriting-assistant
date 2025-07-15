from pydantic import BaseModel, Field

class ApplicantProfileRequest(BaseModel):
    applicant_profile: str = Field(
        ...,
        description=(
            """A string containing the applicant's profile information, including name, age, income,
            credit score, loan amount, employment status, debt-to-income ratio, and any other relevant details."""
        )
    )