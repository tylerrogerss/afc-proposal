from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import util

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobDetails(BaseModel):
    client_name: str
    contact_info: str
    job_address: str
    job_scope: str
    notes: str = ""

class FenceDetails(BaseModel):
    job_id: str
    fence_type: str
    linear_feet: float
    corner_posts: int
    end_posts: int
    height: int
    option_d: str = "No"

class Notes(BaseModel):
    job_id: str
    notes: str

class CostEstimation(BaseModel):
    job_id: str
    price_per_square_foot: float
    pricing_strategy: str = "Master Halo Pricing"
    material_prices: dict = {}
    daily_rate: float = 150.0
    num_days: int = 5
    num_employees: int = 3


@app.get("/")
def hello_world():
    return {"message": "AFC Fencing API is running!"}

@app.post("/new_bid/job_details")
def submit_job_details(details: JobDetails):
    try:
        job_id, job_data = util.save_job_details(
            details.client_name, details.contact_info, details.job_address, details.job_scope, details.notes
        )
        return {"message": "Job details saved successfully", "job_id": job_id, "job_data": job_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new_bid/fence_details")
def submit_fence_details(details: FenceDetails):
    try:
        materials_needed = util.save_fence_details(
            details.job_id, details.fence_type, details.linear_feet, details.corner_posts,
            details.end_posts, details.height, details.option_d
        )
        return {"message": "Fence details saved successfully", "job_id": details.job_id,
                "materials_needed": materials_needed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new_bid/add_notes")
def add_notes(note_data: Notes):
    try:
        util.add_notes_to_job(note_data.job_id, note_data.notes)
        return {"notes": note_data.notes}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new_bid/cost_estimation")
def cost_estimation(data: CostEstimation):
    try:
        if data.job_id not in util.job_database:
            raise HTTPException(status_code=404, detail="Job ID does not exist")

        fence_details = util.job_database[data.job_id].get("fence_details")
        if not fence_details:
            raise HTTPException(status_code=400, detail="Fence details not provided for this job")

        total_costs = util.calculate_total_costs(
            fence_details,
            data.material_prices,
            data.pricing_strategy,
            data.daily_rate,
            data.num_days,
            data.num_employees
        )

        square_footage_cost = round(data.price_per_square_foot * fence_details["linear_feet"], 2)
        grand_total = round(
            total_costs["material_total"] +
            total_costs["labor_costs"]["total_labor_cost"] +
            square_footage_cost, 2
        )

        return {
            "message": "Cost estimation completed successfully",
            "job_id": data.job_id,
            "price_per_square_foot": data.price_per_square_foot,
            "costs": {
                "materials_needed": total_costs["materials_needed"],
                "detailed_costs": total_costs["detailed_costs"],
                "material_total": total_costs["material_total"],
                "labor_costs": total_costs["labor_costs"],
                "square_footage_cost": square_footage_cost,
                "total_cost": grand_total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
