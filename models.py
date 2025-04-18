# models.py

from pydantic import BaseModel
from typing import Optional, Dict


# === Job Details ===
class JobDetails(BaseModel):
    proposal_to: str
    phone: str
    email: str
    job_address: str
    job_name: str
    notes: str = ""


# === Fence Type Base ===
class BaseFenceDetails(BaseModel):
    job_id: str
    fence_type: str


# === Chain Link Fence ===
class ChainLinkDetails(BaseFenceDetails):
    linear_feet: float
    corner_posts: int
    end_posts: int
    height: int
    top_rail: bool


# === Vinyl Fence ===
class VinylDetails(BaseFenceDetails):
    linear_feet: float
    corner_posts: int
    end_posts: int
    height: int
    with_chain_link: bool


# === Wood Fence ===
class WoodDetails(BaseFenceDetails):
    linear_feet: float
    style: str
    bob: Optional[bool] = False
    height: int = 6


# === SP Wrought Iron Fence ===
class SPWroughtIronDetails(BaseFenceDetails):
    linear_feet: float
    height: int


# === Notes ===
class Notes(BaseModel):
    job_id: str
    notes: str


# === Cost Estimation ===
class CostEstimation(BaseModel):
    job_id: str
    pricing_strategy: str = "Master Halco Pricing"
    material_prices: Dict[str, float] = {}
    daily_rate: float = 150.0
    num_employees: int = 3
    dirt_complexity: str = "soft"
    grade_of_slope_complexity: float = 0.0
    productivity: float = 1.0


# === Proposal / Materials Generation ===
class ProposalRequest(BaseModel):
    job_id: str


class JobIDRequest(BaseModel):
    job_id: str
