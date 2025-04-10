from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
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
    proposal_to: str
    phone: str
    email: str
    job_address: str
    job_name: str
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
    pricing_strategy: str = "Master Halco Pricing"
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
            proposal_to=details.proposal_to,
            phone=details.phone,
            email=details.email,
            job_address=details.job_address,
            job_name=details.job_name,
            notes=details.notes
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

        grand_total = round(
            total_costs["material_total"] +
            total_costs["material_tax"] +
            total_costs["delivery_charge"] +
            total_costs["labor_costs"]["total_labor_cost"], 2
        )

        return {
            "message": "Cost estimation completed successfully",
            "job_id": data.job_id,
            "price_per_linear_foot": total_costs["price_per_linear_foot"],
            "costs": {
                "materials_needed": total_costs["materials_needed"],
                "detailed_costs": total_costs["detailed_costs"],
                "material_total": total_costs["material_total"],
                "material_tax": total_costs["material_tax"],
                "delivery_charge": total_costs["delivery_charge"],
                "labor_costs": total_costs["labor_costs"],
                "total_cost": grand_total,
                "profit_margins": total_costs["profit_margins"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_proposal")
def generate_proposal(job_id: str):
    if job_id not in util.job_database:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = util.job_database[job_id]
    first_name = job.get("proposal_to", "").split()[0]

    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Draw Logo (centered)
    logo_path = "american-fence-concepts-logo_sm.webp"  # make sure this file exists in root
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_width = 180
        c.drawImage(logo, (width - logo_width) / 2, height - 100, width=logo_width, preserveAspectRatio=True, mask='auto')

    # Company Address
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 110, "2383 Via Rancheros, Fallbrook, CA 92028")
    c.drawCentredString(width / 2, height - 123, "www.americanfenceconcepts.com")
    c.drawCentredString(width / 2, height - 135, "CA LIC #1037833")

    # Jon Keys & Beau Postal
    c.setFont("Helvetica", 11)
    contact_text = """Jon Keys
760-877-9951
j.keys@americanfenceconcepts.com

Beau Postal
949-259-8868
bpostal@americanfenceconcepts.com"""
    text_object = c.beginText(50, height - 200)
    for line in contact_text.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)

    # Greeting
    c.setFont("Helvetica", 12)
    greeting = f"{first_name},\n\nAmerican Fence Concepts appreciates the opportunity to offer the following proposal. " \
               "We agree to perform the below stated work and hereby agrees to fabricate, furnish, and install the described " \
               "work in a professional and timely work like manner. We look forward to doing business with you."
    text_obj = c.beginText(50, height - 330)
    for line in greeting.splitlines():
        text_obj.textLine(line)
    c.drawText(text_obj)

    c.showPage()
    c.save()
    buffer.seek(0)

    output_path = f"proposal_{job_id}.pdf"
    with open(output_path, "wb") as f:
        f.write(buffer.read())

    return FileResponse(output_path, filename="AFC_Proposal.pdf", media_type="application/pdf")
