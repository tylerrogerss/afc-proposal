from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from typing import Union
import os
from fastapi import Body
from models import ChainLinkDetails, VinylDetails, WoodDetails, SPWroughtIronDetails

import util
from models import (
    ChainLinkDetails,
    VinylDetails,
    WoodDetails,
    SPWroughtIronDetails,
    JobDetails,
    Notes,
    CostEstimation,
    ProposalRequest,
    JobIDRequest,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def submit_fence_details(details: dict = Body(...)):
    try:
        fence_type = details.get("fence_type", "").lower()
        job_id = details.get("job_id")

        if not job_id:
            raise HTTPException(status_code=400, detail="Missing job_id")

        if fence_type == "chain link":
            validated = ChainLinkDetails(**details)
            materials = util.calculate_materials_chain_link(
                lf=validated.linear_feet,
                cp=validated.corner_posts,
                ep=validated.end_posts,
                height=validated.height,
                top_rail=validated.top_rail
            )

        elif fence_type == "vinyl":
            validated = VinylDetails(**details)
            materials = util.calculate_materials_vinyl(
                lf=validated.linear_feet,
                cp=validated.corner_posts,
                ep=validated.end_posts,
                height=validated.height,
                with_chain_link=validated.with_chain_link
            )

        elif fence_type == "wood":
            validated = WoodDetails(**details)
            materials = util.calculate_materials_wood(
                lf=validated.linear_feet,
                style=validated.style,
                bob=validated.bob,
                height=validated.height
            )

        elif fence_type == "sp wrought iron":
            validated = SPWroughtIronDetails(**details)
            materials = util.calculate_materials_sp_wrought_iron(
                lf=validated.linear_feet,
                height=validated.height
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported fence type: {fence_type}")

        util.job_database[job_id]["fence_details"] = {
            **details,
            "materials_needed": materials
        }

        return {
            "message": "Fence details saved successfully",
            "job_id": job_id,
            "materials_needed": materials
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/new_bid/material_costs")
def get_material_costs(data: CostEstimation):
    if data.job_id not in util.job_database:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    fence_details = util.job_database[data.job_id].get("fence_details")
    if not fence_details:
        raise HTTPException(status_code=400, detail="Fence details not found for this job.")

    height = fence_details.get("height")
    top_rail = fence_details.get("top_rail", False)
    if isinstance(top_rail, str):
        top_rail = top_rail.lower() == "true"

    materials_needed = fence_details.get("materials_needed", {})
    if not materials_needed:
        raise HTTPException(status_code=400, detail="No materials needed found in fence details.")

    detailed_costs, material_total = util.calculate_material_costs(
        materials_needed,
        data.material_prices,
        data.pricing_strategy,
        height,
        top_rail
    )

    return {
        "material_total": material_total,
        "detailed_costs": detailed_costs
    }


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
            fence_details=fence_details,
            material_prices=data.material_prices,
            pricing_strategy=data.pricing_strategy,
            daily_rate=data.daily_rate,
            num_employees=data.num_employees,
            dirt_complexity=data.dirt_complexity,
            grade_of_slope_complexity=data.grade_of_slope_complexity
        )

        grand_total = round(
            total_costs["material_total"] +
            total_costs["material_tax"] +
            total_costs["delivery_charge"] +
            total_costs["labor_costs"]["total_labor_cost"], 2
        )

        labor_duration_options = util.generate_labor_duration_options(
            linear_feet=fence_details.get("linear_feet"),
            dirt_complexity=util.dirt_scores.get(data.dirt_complexity.lower(), 1.0),
            grade_of_slope_complexity=util.calculate_slope_complexity_score(data.grade_of_slope_complexity),
            productivity=data.productivity  # ✅ added here
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
                "profit_margins": total_costs["profit_margins"],
                "labor_duration_options": labor_duration_options
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Body, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import os
import util

@app.post("/generate_proposal")
def generate_proposal(data: ProposalRequest):
    job_id = data.job_id

    if job_id not in util.job_database:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = util.job_database[job_id]
    first_name = job.get("proposal_to", "").split()[0] if job.get("proposal_to") else "Client"

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # === Logo ===
    logo_path = "american-fence-concepts-logo_sm.webp"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_width = 180
        c.drawImage(logo, (width - logo_width) / 2, height - 100, width=logo_width, preserveAspectRatio=True, mask='auto')

    # === Company Info ===
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 110, "2383 Via Rancheros, Fallbrook, CA 92028")
    c.drawCentredString(width / 2, height - 123, "www.americanfenceconcepts.com")
    c.drawCentredString(width / 2, height - 135, "CA LIC #1037833")

    # === Contact Info ===
    c.setFont("Helvetica", 11)
    contact_text = """Jon Keys
760-877-9951
j.keys@americanfenceconcepts.com

Beau Postal
949-259-8868
bpostal@americanfenceconcepts.com"""
    contact_obj = c.beginText(50, height - 200)
    for line in contact_text.splitlines():
        contact_obj.textLine(line)
    c.drawText(contact_obj)

    # === Greeting Paragraph ===
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 12
    style.leading = 16

    greeting_paragraph = Paragraph(
        f"{first_name},<br/><br/>"
        "American Fence Concepts appreciates the opportunity to offer the following proposal. "
        "We agree to perform the below stated work and hereby agrees to fabricate, furnish, and install "
        "the described work in a professional and timely work like manner. We look forward to doing business with you.",
        style
    )

    frame = Frame(
        x1=50,
        y1=height - 560,
        width=width - 100,
        height=140,
        showBoundary=0
    )
    frame.addFromList([greeting_paragraph], c)

    c.showPage()
    c.save()
    buffer.seek(0)

    output_path = f"proposal_{job_id}.pdf"
    with open(output_path, "wb") as f:
        f.write(buffer.read())

    return FileResponse(output_path, filename="AFC_Proposal.pdf", media_type="application/pdf")

@app.post("/generate_materials_list")
def generate_materials_list(request: JobIDRequest):
    return util.generate_materials_list_pdf(request.job_id)
