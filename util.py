import math
import uuid
from collections import OrderedDict


# Default labor values
default_labor_values = {
    "daily_rate": 150.0,
    "num_days": 5,
    "num_employees": 3,
}

# Master Halco pricing unit sizes and unit prices
master_halco_pricing = {
    ("6", True): {
        "chain_link": {"unit_size": 50, "unit_price": 133.50},
        "top_rail": {"unit_size": 21, "unit_price": 30.24},
        "terminal_posts": {"unit_size": 1, "unit_price": 16.49},
        "line_posts": {"unit_size": 1, "unit_price": 13.31},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.64},
        "eye_tops": {"unit_size": 1, "unit_price": 2.73},
        "tension_wire": {"unit_size": 1250, "unit_price": 77.00},
        "brace_bands": {"unit_size": 1, "unit_price": 1.20},
        "tension_bands": {"unit_size": 1, "unit_price": 1.10},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.20},
        "tension_bars": {"unit_size": 1, "unit_price": 8.25},
        "rail_ends": {"unit_size": 1, "unit_price": 1.94},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.00},
        "hog_rings": {"unit_size": 100, "unit_price": 4.73},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 5.14},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 8.53},
    },
    ("6", False): {
        "chain_link": {"unit_size": 50, "unit_price": 109.00},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "line_post_caps": {"unit_size": 1, "unit_price": 1.04},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    ("5", True): {
        "chain_link": {"unit_size": 50, "unit_price": 109.00},
        "top_rail": {"unit_size": 25, "unit_price": 24.00},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "eye_tops": {"unit_size": 1, "unit_price": 3.82},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "brace_bands": {"unit_size": 1, "unit_price": 2.58},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "rail_ends": {"unit_size": 1, "unit_price": 1.34},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    ("5", False): {
        "chain_link": {"unit_size": 50, "unit_price": 133.50},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "line_post_caps": {"unit_size": 1, "unit_price": 1.04},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    ("4", True): {
        "chain_link": {"unit_size": 50, "unit_price": 109.00},
        "top_rail": {"unit_size": 25, "unit_price": 24.00},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "eye_tops": {"unit_size": 1, "unit_price": 3.82},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "brace_bands": {"unit_size": 1, "unit_price": 2.58},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "rail_ends": {"unit_size": 1, "unit_price": 1.34},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    ("4", False): {
        "chain_link": {"unit_size": 50, "unit_price": 133.50},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "line_post_caps": {"unit_size": 1, "unit_price": 1.04},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
}

# Fence Specialties pricing unit sizes and unit prices
fence_specialties_pricing = {
    ("6", True): {
        "chain_link": {"unit_size": 50, "unit_price": 133.50},
        "top_rail": {"unit_size": 21, "unit_price": 30.24},
        "terminal_posts": {"unit_size": 1, "unit_price": 16.49},
        "line_posts": {"unit_size": 1, "unit_price": 13.31},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.64},
        "eye_tops": {"unit_size": 1, "unit_price": 2.73},
        "tension_wire": {"unit_size": 1250, "unit_price": 77.00},
        "brace_bands": {"unit_size": 1, "unit_price": 1.20},
        "tension_bands": {"unit_size": 1, "unit_price": 1.10},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.20},
        "tension_bars": {"unit_size": 1, "unit_price": 8.25},
        "rail_ends": {"unit_size": 1, "unit_price": 1.94},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.00},
        "hog_rings": {"unit_size": 100, "unit_price": 4.73},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 5.14},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 8.53},
    },
    ("5", True): {
        "chain_link": {"unit_size": 50, "unit_price": 109.00},
        "top_rail": {"unit_size": 25, "unit_price": 24.00},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "eye_tops": {"unit_size": 1, "unit_price": 3.82},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "brace_bands": {"unit_size": 1, "unit_price": 2.58},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "rail_ends": {"unit_size": 1, "unit_price": 1.34},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    ("4", True): {
        "chain_link": {"unit_size": 50, "unit_price": 109.00},
        "top_rail": {"unit_size": 25, "unit_price": 24.00},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "eye_tops": {"unit_size": 1, "unit_price": 3.82},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "brace_bands": {"unit_size": 1, "unit_price": 2.58},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "rail_ends": {"unit_size": 1, "unit_price": 1.34},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    ("6", False): {
        "chain_link": {"unit_size": 50, "unit_price": 109.00},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "line_post_caps": {"unit_size": 1, "unit_price": 1.04},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    ("5", False): {
        "chain_link": {"unit_size": 50, "unit_price": 133.50},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "line_post_caps": {"unit_size": 1, "unit_price": 1.04},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
    (4, False): {
        "chain_link": {"unit_size": 50, "unit_price": 133.50},
        "terminal_posts": {"unit_size": 1, "unit_price": 38.00},
        "line_posts": {"unit_size": 1, "unit_price": 32.00},
        "terminal_post_caps": {"unit_size": 1, "unit_price": 1.17},
        "line_post_caps": {"unit_size": 1, "unit_price": 1.04},
        "tension_wire": {"unit_size": 1250, "unit_price": 41.63},
        "tension_bands": {"unit_size": 1, "unit_price": 3.27},
        "nuts_and_bolts": {"unit_size": 1, "unit_price": 0.35},
        "tension_bars": {"unit_size": 1, "unit_price": 8.77},
        "chain_link_ties": {"unit_size": 100, "unit_price": 9.68},
        "hog_rings": {"unit_size": 100, "unit_price": 14.45},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.98},
        "cans_of_spray_paint": {"unit_size": 1, "unit_price": 5.98},
    },
}

default_material_prices = {}
job_database = {}

pricing_tables = {
    "Master Halco Pricing": master_halco_pricing,
    "Fence Specialties Pricing": fence_specialties_pricing
}

def save_job_details(proposal_to, phone, email, job_address, job_name, notes=''):
    job_id = str(uuid.uuid4())
    job_data = {
        "proposal_to": proposal_to,
        "phone": phone,
        "email": email,
        "job_address": job_address,
        "job_name": job_name,
        "notes": notes,
    }
    job_database[job_id] = job_data
    return job_id, job_data

def save_fence_details(
    job_id,
    fence_type,
    linear_feet,
    corner_posts,
    end_posts,
    height,
    option_d="No",
    dirt_complexity="soft",
    grade_of_slope_complexity=10.0
):
    if job_id not in job_database:
        raise ValueError("Job ID does not exist")

    # Calculate both scores
    slope_score = calculate_slope_complexity_score(grade_of_slope_complexity)

    dirt_scores = {
        "soft": 1.0,
        "hard": 1.5,
        "jack hammer": 2.0,
        "core drill": 1.8
    }
    dirt_score = dirt_scores.get(dirt_complexity.lower(), 1.0)

    materials_needed = calculate_materials(
        fence_type, linear_feet, corner_posts, end_posts, height, option_d=option_d
    )

    job_database[job_id]["fence_details"] = {
        "fence_type": fence_type,
        "linear_feet": linear_feet,
        "corner_posts": corner_posts,
        "end_posts": end_posts,
        "height": height,
        "option_d": option_d,
        "dirt_complexity": dirt_complexity,
        "dirt_complexity_score": dirt_score,
        "grade_of_slope_complexity": grade_of_slope_complexity,
        "slope_complexity_score": slope_score,
        "materials_needed": materials_needed,
    }

    return materials_needed

def calculate_materials(fence_type, lf, cp, ep, height, spacing=8, option_d="No"):
    def round_up(value):
        return math.ceil(value * 100) / 100

    if fence_type.lower() == "chain link":
        terminal_posts = cp + ep
        line_posts = round_up((lf / spacing) - cp - ep)
        top_rail = round_up(lf)
        terminal_post_caps = round_up(terminal_posts)
        eye_tops = round_up(line_posts)
        tension_wire = round_up((lf + 10) + (cp * 5) + (ep * 5))
        brace_bands = round_up(ep + (2 * cp))
        tension_bands = round_up((height - 1) * ((cp * 2) + ep))
        nuts_and_bolts = round_up(brace_bands + tension_bands)
        tension_bars = round_up(ep + (2 * cp))
        rail_ends = round_up(ep + (2 * cp))
        chain_link_ties = round_up((lf * 12 / 10) + (line_posts * 6))
        hog_rings = round_up((lf * 12) / 10)
        bags_of_concrete = round_up((line_posts + terminal_posts) * 1.75)
        cans_of_spray_paint = round_up(terminal_posts)
        include_top_rail = option_d.lower() != "no"

        # Assemble materials
        materials = OrderedDict([
            ("chain_link", round_up(lf)),
            ("top_rail", top_rail if include_top_rail else 0),
            ("terminal_posts", round_up(terminal_posts)),
            ("line_posts", line_posts),
            ("terminal_post_caps", terminal_post_caps),
            ("eye_tops", eye_tops if include_top_rail else 0),
            ("tension_wire", tension_wire),
            ("brace_bands", brace_bands),
            ("tension_bands", tension_bands),
            ("nuts_and_bolts", nuts_and_bolts),
            ("tension_bars", tension_bars),
            ("rail_ends", rail_ends if include_top_rail else 0),
            ("chain_link_ties", chain_link_ties),
            ("hog_rings", hog_rings),
            ("bags_of_concrete", bags_of_concrete),
            ("cans_of_spray_paint", cans_of_spray_paint),
        ])

        # Only add line_post_caps if top rail is not included
        if not include_top_rail:
            materials["line_post_caps"] = round_up(line_posts)

        return materials

    raise ValueError(f"Unsupported fence type: {fence_type}")

def add_notes_to_job(job_id, notes):
    if job_id not in job_database:
        raise ValueError(f"Job ID {job_id} does not exist.")
    job_database[job_id]["notes"] = notes

def calculate_material_costs(materials, custom_prices=None, pricing_strategy=None, height=None, top_rail=True):
    custom_prices = custom_prices or {}

    if pricing_strategy in pricing_tables:
        price_table = pricing_tables[pricing_strategy].get((str(height), top_rail), {})
        merged_prices = {k: v["unit_price"] for k, v in price_table.items()}
        unit_sizes = {k: v["unit_size"] for k, v in price_table.items()}
    else:
        merged_prices = default_material_prices.copy()
        unit_sizes = {k: 1 for k in materials}

    merged_prices.update(custom_prices)

    detailed_costs = {}
    total_cost = 0

    for material, quantity in materials.items():
        unit_size = unit_sizes.get(material, 1)
        order_size = math.ceil(quantity / unit_size)
        unit_price = round(merged_prices.get(material, 0), 2)
        material_total = round(order_size * unit_price, 2)
        detailed_costs[material] = {
            "quantity": quantity,
            "unit_size": unit_size,
            "order_size": order_size,
            "unit_price": unit_price,
            "total_cost": material_total
        }
        total_cost += material_total

    return detailed_costs, round(total_cost, 2)

def calculate_labor_cost(daily_rate=None, num_days=None, num_employees=None):
    daily_rate = daily_rate if daily_rate is not None else default_labor_values["daily_rate"]
    num_days = num_days if num_days is not None else default_labor_values["num_days"]
    num_employees = num_employees if num_employees is not None else default_labor_values["num_employees"]

    labor_cost_per_day = daily_rate * num_employees
    total_labor_cost = labor_cost_per_day * num_days

    return {
        "labor_cost_per_day": round(labor_cost_per_day, 2),
        "total_labor_cost": round(total_labor_cost, 2),
    }

def calculate_total_costs(
    fence_details,
    material_prices,
    pricing_strategy="Master Halo Pricing",
    daily_rate=None,
    num_days=None,  # <- ADD THIS BACK IN
    num_employees=3,  # Default to 3 workers
    dirt_complexity="soft",
    grade_of_slope_complexity=0.0,
    productivity=1.0
):
    materials_needed = fence_details["materials_needed"]
    height = fence_details.get("height")
    top_rail = fence_details.get("option_d", "No").lower() != "no"
    linear_feet = fence_details.get("linear_feet")

    # === Material cost calculation
    detailed_material_costs, material_total = calculate_material_costs(
        materials_needed, material_prices, pricing_strategy, height, top_rail
    )

    # === Complexity score calculations
    dirt_scores = {
        "soft": 1.0,
        "hard": 1.5,
        "core drill": 1.8,
        "jack hammer": 2.0
    }
    dirt_score = dirt_scores.get(str(dirt_complexity).lower(), 1.0)
    slope_score = calculate_slope_complexity_score(grade_of_slope_complexity)

    # === Adjusted Days Formula (Excel Equivalent)
    if not linear_feet or not productivity or num_employees <= 0:
        raise ValueError("Missing or invalid values to calculate adjusted_days")

    adjusted_days = round(
        (linear_feet * 60 / 22 * (slope_score + dirt_score - 1)) / (60 * productivity * num_employees * 6), 2
    )

    # === Labor cost calculation
    labor_costs = calculate_labor_cost(daily_rate, adjusted_days, num_employees)

    # === Taxes & delivery
    tax_rate = 0.072 if pricing_strategy == "Master Halo Pricing" else 0.0825
    delivery_charge = 100.00 if pricing_strategy == "Master Halo Pricing" else 0.00
    material_tax = round(material_total * tax_rate, 2)

    # === Final cost calculation
    subtotal = material_total + material_tax + delivery_charge + labor_costs["total_labor_cost"]
    price_per_linear_foot = round(subtotal / linear_feet, 2) if linear_feet else 0

    # === Profit margin breakdown
    profit_margins = {}
    for margin in [0.2, 0.3, 0.4, 0.5]:
        revenue = round(subtotal / (1 - margin), 2)
        profit = round(revenue - subtotal, 2)
        price_per_foot = round(revenue / linear_feet, 2) if linear_feet else 0
        profit_margins[f"{int(margin * 100)}%"] = {
            "revenue": revenue,
            "profit": profit,
            "price_per_linear_foot": price_per_foot
        }

    return {
        "materials_needed": materials_needed,
        "detailed_costs": detailed_material_costs,
        "material_total": material_total,
        "material_tax": material_tax,
        "delivery_charge": delivery_charge,
        "labor_costs": labor_costs,
        "price_per_linear_foot": price_per_linear_foot,
        "profit_margins": profit_margins
    }

def calculate_slope_complexity_score(percentage: float) -> float:
    # Clamp to 10–45%
    percentage = max(10, min(45, percentage))
    # Linear interpolation between 10% → 1.2 and 45% → 2.0
    return round(1.2 + (percentage - 10) * ((2.0 - 1.2) / (45 - 10)), 3)
