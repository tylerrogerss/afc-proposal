from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Frame
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT
from datetime import datetime
from io import BytesIO
from pypdf import PdfReader, PdfWriter
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
    num_days: int = None
    num_employees: int = 3
    dirt_complexity: str = "soft"
    grade_of_slope_complexity: float = 0.0
    productivity: float = 1.0

class ProposalRequest(BaseModel):
    job_id: str

class JobIDRequest(BaseModel):
    job_id: str

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
        # Save fence details and compute materials
        materials_needed = util.save_fence_details(
            job_id=details.job_id,
            fence_type=details.fence_type,
            linear_feet=details.linear_feet,
            corner_posts=details.corner_posts,
            end_posts=details.end_posts,
            height=details.height,
            option_d=details.option_d
        )

        return {
            "message": "Fence details saved successfully",
            "job_id": details.job_id,
            "materials_needed": materials_needed
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
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

        # === Validate productivity input
        if not (0.01 <= data.productivity <= 1.0):
            raise HTTPException(status_code=400, detail="Productivity must be between 0.01 and 1.0")

        # === Call cost calculation
        total_costs = util.calculate_total_costs(
            fence_details,
            data.material_prices,
            data.pricing_strategy,
            data.daily_rate,
            data.num_days,
            data.num_employees,
            data.dirt_complexity,
            data.grade_of_slope_complexity,
            data.productivity  # NEW ARGUMENT
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_proposal")
def generate_proposal(data: ProposalRequest):
    job_id = data.job_id

    if job_id not in util.job_database:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    job = util.job_database[job_id]
    first_name = job.get("proposal_to", "").split()[0]

    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # === Logo
    logo_path = "american-fence-concepts-logo_sm.webp"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_width = 180
        c.drawImage(logo, (width - logo_width) / 2, height - 100, width=logo_width, preserveAspectRatio=True,
                    mask='auto')

    # === Company Info (centered)
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 110, "2383 Via Rancheros, Fallbrook, CA 92028")
    c.drawCentredString(width / 2, height - 123, "www.americanfenceconcepts.com")
    c.drawCentredString(width / 2, height - 135, "CA LIC #1037833")

    # === Contact Info (left aligned, no indent)
    c.setFont("Helvetica", 11)
    contact_lines = [
        "Jon Keys",
        "760-877-9951",
        "j.keys@americanfenceconcepts.com",
        "",
        "Beau Postal",
        "949-259-8868",
        "bpostal@americanfenceconcepts.com"
    ]
    y = height - 180
    for line in contact_lines:
        c.drawString(50, y, line)
        y -= 15

    # === Job Info (aligned with contact info)
    job_info = {
        "Proposal To:": job.get("proposal_to", ""),
        "Date:": datetime.now().strftime("%B %d, %Y"),
        "Phone:": job.get("phone", ""),
        "Email:": job.get("email", ""),
        "Job Address:": job.get("job_address", ""),
        "Job Name:": job.get("job_name", "")
    }

    y -= 30  # space between sections
    for label, value in job_info.items():
        text = f"{label} {value}"
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, label)
        text_width = c.stringWidth(label, "Helvetica-Bold", 10)
        c.setFont("Helvetica", 10)
        c.drawString(50 + text_width + 5, y, value)  # 5px spacing after label
        y -= 15

    # Greeting and body text
    first_name = job.get("proposal_to", "").split()[0]
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 12
    style.leading = 16
    style.leftIndent = 0
    style.rightIndent = 0

    greeting_paragraph = Paragraph(
        f"{first_name},<br/><br/>"
        "American Fence Concepts appreciates the opportunity to offer the following proposal. "
        "We agree to perform the below stated work and hereby agrees to fabricate, furnish, and install "
        "the described work in a professional and timely work like manner. We look forward to doing business with you.",
        style
    )

    # Drop the paragraph further down the page to avoid overlap
    # y = height - 480 starts it well below the job info block
    frame = Frame(50, height - 560, width - 100, 140, showBoundary=0, leftPadding=0, bottomPadding=0, topPadding=0,
                  rightPadding=0)
    frame.addFromList([greeting_paragraph], c)

    # === Total Cost Bottom-Right
    try:
        fence_details = job.get("fence_details")
        if fence_details:
            total_costs = util.calculate_total_costs(
                fence_details,
                material_prices={},
                pricing_strategy="Master Halco Pricing",
                daily_rate=150.0,
                num_days=5,
                num_employees=3
            )
            grand_total = round(
                total_costs["material_total"] +
                total_costs["material_tax"] +
                total_costs["delivery_charge"] +
                total_costs["labor_costs"]["total_labor_cost"], 2
            )
            formatted_total = "${:,.2f}".format(grand_total)
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(width - 50, 60, f"Total: {formatted_total}")
    except Exception as e:
        print(f"Failed to calculate total cost for PDF: {e}")

    c.showPage()
    c.save()
    buffer.seek(0)

    # Save Page 1
    page1_path = f"page1_{job_id}.pdf"
    with open(page1_path, "wb") as f:
        f.write(buffer.read())

        # Combine with second page
    writer = PdfWriter()
    writer.append(PdfReader(page1_path))

    pg2_path = "afc-pro-pg2.pdf"
    if os.path.exists(pg2_path):
        writer.append(PdfReader(pg2_path))
    else:
        raise HTTPException(status_code=500, detail="Second page template not found.")

    final_path = f"proposal_{job_id}.pdf"
    with open(final_path, "wb") as f:
        writer.write(f)

    return FileResponse(final_path, filename="AFC_Proposal.pdf", media_type="application/pdf")

@app.post("/generate_materials_list")
def generate_materials_list(request: JobIDRequest):
    job_id = request.job_id

    if job_id not in util.job_database:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    fence_details = util.job_database[job_id].get("fence_details")
    if not fence_details:
        raise HTTPException(status_code=400, detail="Fence details not found.")

    materials = fence_details.get("materials_needed")
    if not materials:
        raise HTTPException(status_code=400, detail="Materials not calculated.")

    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📦 Materials List")

    c.setFont("Helvetica-Bold", 12)
    y = height - 80
    c.drawString(50, y, "Material")
    c.drawString(250, y, "Quantity")
    y -= 20

    c.setFont("Helvetica", 11)
    for material, quantity in materials.items():
        c.drawString(50, y, material)
        c.drawString(250, y, str(quantity))
        y -= 18
        if y < 50:
            c.showPage()
            y = height - 50

    c.showPage()
    c.save()
    buffer.seek(0)

    output_path = f"materials_list_{job_id}.pdf"
    with open(output_path, "wb") as f:
        f.write(buffer.read())

    return FileResponse(output_path, filename="Materials_List.pdf", media_type="application/pdf")