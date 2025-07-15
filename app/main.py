from fastapi import FastAPI, Form
from app.chains.risk_chain import assess_risk_flexible

app = FastAPI()

@app.post("/assess-risk/")
def assess_risk_endpoint(request: str = Form(...)) -> dict[str, object]:
    print(f"Received applicant profile: {request}")
    """Assess the risk of a loan applicant based on their profile.
    """
    result = assess_risk_flexible(request)
    return result