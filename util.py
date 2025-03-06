import math
import uuid


# Default labor values
default_labor_values = {
    "daily_rate": 150.0,
    "num_days": 5,
    "num_employees": 3,
}

# Default material prices
default_material_prices = {
    "top_rail": 2.50,
    "terminal_posts": 38.00,
    "line_posts": 32.00,
    "terminal_post_caps": 4.98,
    "line_post_caps": 4.98,
    "eye_tops": 3.82,
    "tension_wire": 41.63,
    "brace_bands": 2.58,
    "tension_bands": 3.27,
    "nuts_and_bolts": 11.85,
    "tension_bars": 8.77,
    "rail_ends": 1.34,
    "chain_link_ties": 9.68,
    "hog_rings": 14.45,
    "bags_of_concrete": 4.48,
    "cans_of_spray_paint": 6.48,
    "boards": 10.0,
    "caps": 10.0,
    "horizontal_rails": 10.0,
    "nails": 10.0,
    "postmaster_posts": 10.0,
    "screws": 10.0,
    "trim_boards": 10.0,
    "post_caps": 10.0,
    "rails": 10.0,
    "panel": 10.0,
    "posts": 10.0,
    "sliders": 10.0,
}

job_database = {}

def save_job_details(client_name, contact_info, job_address, job_scope, notes=''):
    """
    Save job details to the in-memory database.
    """
    job_id = str(uuid.uuid4())  # Generate a unique job ID
    job_data = {
        "client_name": client_name,
        "contact_info": contact_info,
        "job_address": job_address,
        "job_scope": job_scope,
        "notes": notes,
    }
    job_database[job_id] = job_data
    return job_id, job_data

def save_fence_details(job_id, fence_type, linear_feet, corner_posts, end_posts, height, option_d="No"):
    """
    Save fence details and calculate materials needed.
    """
    if job_id not in job_database:
        raise ValueError("Job ID does not exist")

    # Calculate materials
    materials_needed = calculate_materials(
        fence_type, linear_feet, corner_posts, end_posts, height, option_d=option_d
    )

    # Add to the job record
    job_database[job_id]["fence_details"] = {
        "fence_type": fence_type,
        "linear_feet": linear_feet,
        "corner_posts": corner_posts,
        "end_posts": end_posts,
        "height": height,
        "option_d": option_d,
        "materials_needed": materials_needed,
    }

    return materials_needed

def calculate_materials(fence_type, lf, cp, ep, height, spacing=8, option_d="No"):
    """
    Calculate materials needed for fencing based on the specified type.
    """
    def round_up(value):
        return math.ceil(value * 100) / 100

    if fence_type.lower() == "chain link":
        terminal_posts = math.ceil(cp + ep)
        line_posts = math.ceil(lf / spacing) - terminal_posts
        top_rail = lf
        tension_wire = (lf * 2) + 10 if option_d.lower() == "no" else (cp + 10) + (ep + line_posts) * 5

        return {
            "top_rail": round_up(top_rail),
            "terminal_posts": round_up(terminal_posts),
            "line_posts": round_up(line_posts),
            "terminal_post_caps": round_up(terminal_posts),
            "line_post_caps": round_up(line_posts),
            "eye_tops": round_up(line_posts),
            "tension_wire": round_up(tension_wire),
            "brace_bands": round_up(ep + (2 * cp)),
            "tension_bands": round_up((height - 1) * ((cp * 2) + ep)),
            "nuts_and_bolts": round_up((height - 1) * ((cp * 2) + ep)),
            "tension_bars": round_up(ep + (2 * cp)),
            "rail_ends": round_up(ep + (2 * cp)),
            "chain_link_ties": round_up(lf + (line_posts * height)),
            "hog_rings": round_up((lf * 12) / 10),
            "bags_of_concrete": round_up((terminal_posts + line_posts) * 1.5),
            "cans_of_spray_paint": round_up(terminal_posts),
        }

    elif fence_type.lower() == "sp wrought iron":
        panel = (lf * 12) / 94
        posts = math.ceil((lf / 8) - (cp + ep))
        sliders = math.ceil(panel * 4)
        screws = sliders
        bags_of_concrete = math.ceil(posts * 1.5)
        spray_paint = math.ceil(panel / 4)

        return {
            "panel": round_up(panel),
            "posts": round_up(posts),
            "post_caps": round_up(posts),
            "sliders": round_up(sliders),
            "screws": round_up(screws),
            "bags_of_concrete": round_up(bags_of_concrete),
            "cans_spray_paint": round_up(spray_paint),
        }

    elif fence_type.lower() == "vinyl":
        line_posts = lf / 8
        rails = (lf / 8) * 4
        post_caps = cp + ep
        screws = rails * 2
        bags_of_concrete = (cp + ep) * 1.5

        return {
            "line_posts": round_up(line_posts),
            "rails": round_up(rails),
            "post_caps": round_up(post_caps),
            "screws": round_up(screws),
            "bags_of_concrete": round_up(bags_of_concrete),
        }

    elif fence_type.lower() == "wood":
        postmaster_posts = lf / 8
        horizontal_rails = postmaster_posts * 3
        boards = math.ceil(lf * 12 / 5.5)
        caps = lf / 8
        trim_boards = (lf / 8) * 2
        screws = horizontal_rails * 4
        nails = math.ceil((boards + trim_boards) * 4)
        bags_of_concrete = (cp + ep) * 1.5

        return {
            "postmaster_posts": round_up(postmaster_posts),
            "horizontal_rails": round_up(horizontal_rails),
            "boards": round_up(boards),
            "caps": round_up(caps),
            "trim_boards": round_up(trim_boards),
            "screws": round_up(screws),
            "nails": round_up(nails),
            "bags_of_concrete": round_up(bags_of_concrete),
        }

    else:
        raise ValueError(f"Unsupported fence type: {fence_type}")

def add_notes_to_job(job_id, notes):
    """
    Add notes to an existing job.

    Args:
    job_id (str): The job ID.
    notes (str): Notes to be added.

    Returns:
    None
    """
    if job_id not in job_database:
        raise ValueError(f"Job ID {job_id} does not exist.")

    # Append the notes to the existing job data
    job_database[job_id]["notes"] = notes

def calculate_material_costs(materials, prices):
    """
    Calculate the total cost of materials based on amounts and prices.
    """
    merged_prices = {**default_material_prices, **prices}

    individual_costs = {}
    total_cost = 0

    for material, amount in materials.items():
        price_per_unit = round(merged_prices.get(material, 0), 2)
        individual_cost = round(amount * price_per_unit, 2)
        individual_costs[material] = individual_cost
        total_cost += individual_cost

    total_cost = round(total_cost, 2)

    return individual_costs, total_cost

def calculate_labor_cost(daily_rate=None, num_days=None, num_employees=None):
    """
    Calculate the labor costs based on daily rate, number of days, and number of employees.
    """
    daily_rate = daily_rate if daily_rate is not None else default_labor_values["daily_rate"]
    num_days = num_days if num_days is not None else default_labor_values["num_days"]
    num_employees = num_employees if num_employees is not None else default_labor_values["num_employees"]

    labor_cost_per_day = daily_rate * num_employees
    total_labor_cost = labor_cost_per_day * num_days

    return {
        "labor_cost_per_day": round(labor_cost_per_day, 2),
        "total_labor_cost": round(total_labor_cost, 2),
    }

def calculate_total_costs(fence_details, material_prices):
    """
    Calculate the total costs including material and labor.
    """
    materials_needed = fence_details["materials_needed"]
    material_costs, material_total = calculate_material_costs(materials_needed, material_prices)

    labor_costs = calculate_labor_cost()

    return {
        "material_costs": material_costs,
        "material_total": material_total,
        "labor_costs": labor_costs,
        "total_cost": round(material_total + labor_costs["total_labor_cost"], 2),
    }


