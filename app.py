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


        # ─── Persist cost data for later summary ────────────────────────
        util.job_database[data.job_id]["costs"] = {
            "material_total":       total_costs["material_total"],
            "material_tax":         total_costs["material_tax"],
            "delivery_charge":      total_costs["delivery_charge"],
            "labor_costs":          total_costs["labor_costs"],             # contains num_days, total_labor_cost, etc.
            "price_per_linear_foot": total_costs["price_per_linear_foot"],
        }
        util.job_database[data.job_id]["estimated_days"] = total_costs["labor_costs"]["num_days"]
        # ────────────────────────────────────────────────────────────────


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
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
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

    writer = PdfWriter()
    writer.append(PdfReader(buffer))  # First page
    writer.append(PdfReader("afc-pro-pg2.pdf"))  # Second page

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    return FileResponse(output_path, filename="AFC_Proposal.pdf", media_type="application/pdf")

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


from fastapi import HTTPException
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import os
import util

from datetime import datetime

@app.post("/generate_job_spec_sheet")
def generate_job_spec_sheet(data: ProposalRequest):
    job_id = data.job_id

    if job_id not in util.job_database:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = util.job_database[job_id]
    fence_details = job.get("fence_details", {})
    materials_needed = fence_details.get("materials_needed", {})

    proposal_to = job.get("proposal_to", "Client")
    job_address = job.get("job_address", "Unknown Address")
    fence_type = fence_details.get("fence_type", "Unknown Type")
    height = fence_details.get("height", "N/A")
    top_rail = fence_details.get("top_rail", False)
    notes = job.get("notes", "")
    today = datetime.today().strftime("%m/%d/%y")

    # === Job Scope ===
    scope_parts = [f"{height}' {fence_type}"]
    if top_rail:
        scope_parts.append("Top Rail")
    job_scope = ", ".join(scope_parts)

    # === Notes Section ===
    notes_text = f"{height}' {fence_type}"
    if notes:
        notes_text += f" — {notes}"

    # === Create PDF ===
    output_path = f"job_spec_sheet_{job_id}.pdf"
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height_pt = letter

    x_margin = 50
    y = height_pt - inch

    # === Title ===
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x_margin, y, "American Fence Concepts")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Job Specification Sheet")
    y -= 29

    # === Basic Info ===
    c.setFont("Helvetica", 10)
    c.drawString(x_margin, y, f"Project Name: {proposal_to} - {fence_type.title()} Fence")
    y -= 14
    c.drawString(x_margin, y, f"Client: {proposal_to}")
    y -= 14
    c.drawString(x_margin, y, f"Date: {today}")
    y -= 14
    c.drawString(x_margin, y, f"Address: {job_address}")
    y -= 20

    # === Job Scope Section ===
    y -= 14
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_margin, y, "Job Scope:")
    y -= 14
    c.setFont("Helvetica", 11)
    c.drawString(x_margin + 20, y, f"- {height}' High {fence_type.title()}")
    y -= 14
    if top_rail:
        c.drawString(x_margin + 20, y, "- Top Rail")
        y -= 14

    # === Materials Table Section ===
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    # c.drawString(x_margin, y, "Materials:")
    y -= 20

    # Build table data
    table_data = [["Material", "Quantity", "Unit Size", "Order Size"]]
    for material, details in materials_needed.items():
        if isinstance(details, dict):  # structured format
            quantity = round(details.get("quantity", 0))
            unit_size = round(details.get("unit_size", 1))
            order_size = round(details.get("order_size", 0))
        else:  # fallback
            quantity = round(details)
            unit_size = 1
            order_size = quantity

        label = material.replace("_", " ").title()
        table_data.append([label, quantity, unit_size, order_size])

    table = Table(table_data, colWidths=[180, 80, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    # Render the table
    table_height = len(table_data) * 18
    table.wrapOn(c, width, height)
    table.drawOn(c, x_margin, y - table_height)
    y -= table_height + 20

    # === Notes Section ===
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Notes:")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(x_margin + 20, y, f"- {height}' High {fence_type.title()}")
    y -= 18
    if notes.strip():
        c.drawString(x_margin + 20, y, f"- {notes.strip()}")
        y -= 18

    c.save()

    return FileResponse(output_path, filename="AFC_Job_Spec_Sheet.pdf", media_type="application/pdf")

from fastapi import HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
import util

@app.post("/generate_internal_summary")
def generate_internal_summary(data: ProposalRequest):
    job_id = data.job_id

    if job_id not in util.job_database:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = util.job_database[job_id]
    fence_details = job.get("fence_details", {})
    proposal_to = job.get("proposal_to", "Client")
    linear_feet = fence_details.get("linear_feet", 0)
    height = fence_details.get("height", "N/A")

    # Cost breakdown
    costs = job.get("costs", {})
    material_total = costs.get("material_total", 0)
    material_tax = costs.get("material_tax", 0)
    delivery_charge = costs.get("delivery_charge", 0)
    labor_info = costs.get("labor_costs", {})
    total_labor = labor_info.get("total_labor_cost", 0)

    total_cost = material_total + material_tax + delivery_charge + total_labor
    estimated_days = job.get("estimated_days", "N/A")

    # Price per linear foot
    price_per_lf = total_cost / linear_feet if linear_feet else 0

    # Margin calculations
    def margin_calc(margin_pct):
        revenue = total_cost / (1 - margin_pct)
        profit = revenue - total_cost
        return revenue, profit, revenue / linear_feet if linear_feet else 0

    margins = {
        "20%": margin_calc(0.20),
        "30%": margin_calc(0.30),
        "40%": margin_calc(0.40),
    }

    # === PDF generation ===
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height_pt = letter
    x = 50
    y = height_pt - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Internal Job Summary")
    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"Job ID: {job_id}")
    y -= 15
    c.drawString(x, y, f"Client: {proposal_to}")
    y -= 15
    c.drawString(x, y, f"Fence Type: {fence_details.get('fence_type', '')} - {height}'")
    y -= 15
    c.drawString(x, y, f"Date: {datetime.now().strftime('%m/%d/%y')}")
    y -= 25

    # === Cost Breakdown ===
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Cost Breakdown:")
    y -= 18
    c.setFont("Helvetica", 11)

    c.drawString(x, y, f"Material Cost: ${material_total:,.2f}")
    y -= 16
    c.drawString(x, y, f"Material Tax: ${material_tax:,.2f}")
    y -= 16
    c.drawString(x, y, f"Delivery Charge: ${delivery_charge:,.2f}")
    y -= 16

    c.drawString(x, y, f"Labor Cost: ${total_labor:,.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"Total Job Cost: ${total_cost:,.2f}")
    y -= 25

    # === Production Info ===
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Production Info:")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"Estimated Production Time: {estimated_days} days")
    y -= 16
    c.drawString(x, y, f"Price Per Linear Foot: ${price_per_lf:,.2f}")
    y -= 25

    # === Margin Breakdown ===
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Margin Projections:")
    y -= 18
    c.setFont("Helvetica", 11)

    for label, (revenue, profit, price_per_lf_margin) in margins.items():
        c.drawString(x + 10, y, f"{label} Margin:")
        y -= 16
        c.drawString(x + 30, y, f"Revenue: ${revenue:,.2f}")
        y -= 16
        c.drawString(x + 30, y, f"Profit: ${profit:,.2f}")
        y -= 16
        c.drawString(x + 30, y, f"Price Per LF: ${price_per_lf_margin:,.2f}")
        y -= 20

    c.save()
    buffer.seek(0)

    output_path = f"internal_summary_{job_id}.pdf"
    with open(output_path, "wb") as f:
        f.write(buffer.read())

    return FileResponse(output_path, filename="AFC_Internal_Summary.pdf", media_type="application/pdf")
