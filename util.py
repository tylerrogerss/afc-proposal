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
    # -------------------- CHAIN LINK --------------------
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

    # -------------------- WOOD --------------------
    ("wood", "good neighbor", "6", True): {
        "postmaster_posts": {"unit_size": 1, "unit_price": 28.00},
        "horizontal_rails": {"unit_size": 1, "unit_price": 4.98},
        "boards": {"unit_size": 1, "unit_price": 3.85},
        "caps": {"unit_size": 1, "unit_price": 4.98},
        "trim_boards": {"unit_size": 1, "unit_price": 3.50},
        "screws": {"unit_size": 50, "unit_price": 24.95},
        "nails": {"unit_size": 100, "unit_price": 44.49},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.58},
    },
    ("wood", "good neighbor", "6", False): {
        "postmaster_posts": {"unit_size": 1, "unit_price": 28.00},
        "horizontal_rails": {"unit_size": 1, "unit_price": 4.98},
        "boards": {"unit_size": 1, "unit_price": 3.85},
        "caps": {"unit_size": 1, "unit_price": 4.98},
        "trim_boards": {"unit_size": 1, "unit_price": 3.50},
        "screws": {"unit_size": 50, "unit_price": 24.95},
        "nails": {"unit_size": 100, "unit_price": 44.49},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.58},
    },
    ("wood", "dogeared", "6", False): {
        "postmaster_posts": {"unit_size": 1, "unit_price": 28.00},
        "horizontal_rails": {"unit_size": 1, "unit_price": 4.98},
        "boards": {"unit_size": 1, "unit_price": 3.85},
        "screws": {"unit_size": 50, "unit_price": 24.95},
        "nails": {"unit_size": 100, "unit_price": 44.49},
        "bags_of_concrete": {"unit_size": 1, "unit_price": 2.58},
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

def save_fence_details(job_id, fence_type, **kwargs):
    if job_id not in job_database:
        raise ValueError("Job ID does not exist")

    # === Dynamically compute materials based on fence type
    materials_needed = calculate_materials_router(fence_type, **kwargs)

    # === Build fence_details dictionary dynamically
    fence_details = {
        "fence_type": fence_type,
        "materials_needed": materials_needed,
    }

    # === Save only the relevant fields based on fence_type
    if fence_type.lower() == "chain link":
        fence_details.update({
            "linear_feet": kwargs["lf"],
            "corner_posts": kwargs["cp"],
            "end_posts": kwargs["ep"],
            "height": kwargs["height"],
            "top_rail": kwargs["top_rail"],
        })

    elif fence_type.lower() == "vinyl":
        fence_details.update({
            "linear_feet": kwargs["lf"],
            "corner_posts": kwargs["cp"],
            "end_posts": kwargs["ep"],
            "height": kwargs["height"],
            "with_chain_link": kwargs["with_chain_link"],
        })


    elif fence_type.lower() == "wood":
        fence_details.update({
            "linear_feet": kwargs["lf"],
            "style": kwargs["style"],
            "bob": kwargs.get("bob", False),
            "height": kwargs.get("height", 6)
        })

    elif fence_type.lower() == "sp wrought iron":
        fence_details.update({
            "linear_feet": kwargs["lf"],
            "corner_posts": kwargs["cp"],
            "end_posts": kwargs["ep"],
        })

    # Save to job database
    job_database[job_id]["fence_details"] = fence_details

    return materials_needed

def calculate_materials_router(fence_type, **kwargs):
    if fence_type.lower() == "chain link":
        return calculate_materials_chain_link(
            lf=kwargs["lf"],
            cp=kwargs["cp"],
            ep=kwargs["ep"],
            height=kwargs["height"],
            top_rail=kwargs["top_rail"]
        )

    elif fence_type.lower() == "vinyl":
        return calculate_materials_vinyl(
            lf=kwargs["lf"],
            cp=kwargs["cp"],
            ep=kwargs["ep"],
            height=kwargs["height"],
            with_chain_link=kwargs["with_chain_link"]
        )

    elif fence_type.lower() == "wood":
        return calculate_materials_wood(
            lf=kwargs["lf"],
            style=kwargs["style"],
            bob=kwargs.get("bob", False),  # optional
            height=kwargs.get("height", 6)  # default 6 if not passed
        )

    elif fence_type.lower() == "sp wrought iron":
        return calculate_materials_sp_wrought_iron(
            lf=kwargs["lf"],
            height=kwargs["height"]
        )

    else:
        raise ValueError(f"Unsupported fence type: {fence_type}")

def calculate_materials_chain_link(lf, cp, ep, height, top_rail):
    def round_up(value):
        return math.ceil(value * 100) / 100

    terminal_posts = cp + ep
    line_posts = (lf / 8) - cp - ep
    tension_wire = (lf + 10) + (cp * 5) + (ep * 5)
    brace_bands = (cp * 2) + ep
    tension_bands = (cp * 2) * (height - 1) + (ep * (height - 1))
    nuts_and_bolts = brace_bands + tension_bands
    tension_bars = (cp * 2) + ep
    rail_ends = (cp * 2) + ep
    chain_link_ties = (lf * 12 / 10) + (line_posts * height)
    hog_rings = (lf * 12) / 10
    bags_of_concrete = (terminal_posts + line_posts) * 1.75
    cans_of_spray_paint = terminal_posts

    materials = OrderedDict([
        ("chain_link", round_up(lf)),
        ("terminal_posts", round_up(terminal_posts)),
        ("line_posts", round_up(line_posts)),
        ("terminal_post_caps", round_up(terminal_posts)),
        ("tension_wire", round_up(tension_wire if top_rail else tension_wire * 2)),
        ("tension_bands", round_up(tension_bands)),
        ("nuts_and_bolts", round_up(nuts_and_bolts if top_rail else tension_bands)),
        ("tension_bars", round_up(tension_bars)),
        ("chain_link_ties", round_up(chain_link_ties) if top_rail else round_up(line_posts * (height + 1))),
        ("hog_rings", round_up(hog_rings) if top_rail else round_up((tension_wire * 12) / 10) * 2),
        ("bags_of_concrete", round_up(bags_of_concrete)),
        ("cans_of_spray_paint", round_up(cans_of_spray_paint)),
    ])

    if top_rail:
        materials["top_rail"] = round_up(lf)
        materials["eye_tops"] = round_up(line_posts)
        materials["brace_bands"] = round_up(brace_bands)
        materials["rail_ends"] = round_up(rail_ends)
    else:
        materials["line_post_caps"] = round_up(line_posts)

    return materials

def calculate_materials_vinyl(lf, cp, ep, height, with_chain_link):
    def round_up(value):
        return math.ceil(value * 100) / 100

    # Base vinyl calculations
    line_posts = lf / 8 - cp - ep
    rails = (lf / 16) * 3
    post_caps = cp + ep + line_posts
    bags_of_concrete = (cp + ep + line_posts) * 1.75

    materials = OrderedDict([
        ("corner_posts", round_up(cp)),
        ("end_posts", round_up(ep)),
        ("line_posts", round_up(line_posts)),
        ("rails", round_up(rails)),
        ("post_caps", round_up(post_caps)),
        ("bags_of_concrete", round_up(bags_of_concrete)),
    ])

    if with_chain_link:
        tension_bars = (cp * 2) + ep
        hog_rings = (lf * 12) / 10
        tension_wire = (lf + 10) + (cp * 5) + (ep * 5)

        materials["chain_link_roll"] = round_up(lf)
        materials["tension_bars"] = round_up(tension_bars)
        materials["tension_wire"] = round_up(tension_wire)
        materials["hog_rings"] = round_up(hog_rings)
        materials["screws (1-1/4\\\" - smaller)"] = round_up(line_posts * 4)
        materials["steel_clips"] = round_up(line_posts * 4)  # Equal to smaller screws
        materials["screws (3/8\\\" - bigger)"] = round_up((tension_bars * 5) + (rails * 2))
    else:
        materials["screws"] = round_up(rails * 2)

    return materials

def calculate_materials_wood(lf, style, bob=False, height=6):
    def round_up(value):
        return math.ceil(value * 100) / 100

    materials = OrderedDict()

    if style.lower() == "dogeared":
        posts = lf / 8
        rails = (lf / 8) * 2
        boards = (lf * 12 / 5.5)  # Assuming 5.5" wide boards
        screws = (rails * 4)
        nails = boards * 4
        concrete = posts * 2

        materials.update({
            "postmaster_posts": round_up(posts),
            "horizontal_rails": round_up(rails),
            "boards": round_up(boards),
            "screws": round_up(screws),
            "nails": round_up(nails),
            "bags_of_concrete": round_up(concrete)
        })

    elif style.lower() == "good neighbor":
        posts = lf / 8
        rails = (lf / 8) * 3
        boards = (lf * 12 / 5.5) if bob else (lf * 12 / 7.5)
        caps = lf / 8
        trim_boards = (lf / 8) * 4
        screws = (rails * 4) + (caps * 4)
        nails = (boards * 3) + (trim_boards * 2)
        concrete = posts * 2

        materials.update({
            "postmaster_posts": round_up(posts),
            "horizontal_rails": round_up(rails),
            "boards": round_up(boards),
            "caps": round_up(caps),
            "trim_boards": round_up(trim_boards),
            "screws": round_up(screws),
            "nails": round_up(nails),
            "bags_of_concrete": round_up(concrete)
        })

    else:
        raise ValueError("Unsupported wood fence style. Use 'dogeared' or 'good neighbor'.")

    return materials

def calculate_materials_sp_wrought_iron(lf, height):
    def round_up(value):
        return math.ceil(value * 100) / 100

    panel = lf / 8
    posts = lf / 8
    sliders = panel * 4
    screws = sliders
    bags_of_concrete = posts * 1.75
    spray_paint = panel / 8

    materials = OrderedDict({
        "panel": round_up(panel),
        "posts": round_up(posts),
        "post_caps": round_up(posts),
        "sliders": round_up(sliders),
        "screws": round_up(screws),
        "cans_spray_paint": round_up(spray_paint),
        "bags_of_concrete": round_up(bags_of_concrete),
    })

    return materials

def add_notes_to_job(job_id, notes):
    if job_id not in job_database:
        raise ValueError(f"Job ID {job_id} does not exist.")
    job_database[job_id]["notes"] = notes

def calculate_material_costs(materials, custom_prices=None, pricing_strategy=None, height=None, top_rail=True):

    custom_prices = custom_prices or {}

    if pricing_strategy in pricing_tables:
        # Ensure correct key types for lookup
        height_key = str(height)
        top_rail_key = bool(top_rail)
        price_table = pricing_tables[pricing_strategy].get((height_key, top_rail_key), {})
        merged_prices = {k: v["unit_price"] for k, v in price_table.items()}
        unit_sizes = {k: v["unit_size"] for k, v in price_table.items()}
    else:
        merged_prices = default_material_prices.copy()
        unit_sizes = {k: 1 for k in materials}

    # Allow override with user-provided prices
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

# === Labor Duration (num_days) ===
def calculate_num_days(
    linear_feet: float,
    crew_size: int = 3,
    panel_install_time_min: float = 106.25,
    panel_length_ft: float = 8.0,
    work_hours_per_day: float = 6.0,
    dirt_complexity: float = 1.0,
    grade_of_slope_complexity: float = 1.0,
) -> float:
    panel_install_time_hr = panel_install_time_min / 60.0
    time_per_linear_foot = panel_install_time_hr / panel_length_ft
    total_hours = linear_feet * time_per_linear_foot

    # Combined complexity logic: (dirt + slope) - 1
    complexity_multiplier = (dirt_complexity + grade_of_slope_complexity) - 1
    adjusted_hours = total_hours * complexity_multiplier

    adjusted_hours_per_crew = adjusted_hours / crew_size
    estimated_days = adjusted_hours_per_crew / work_hours_per_day
    return estimated_days


# === Labor Cost ===
def calculate_labor_cost(
    linear_feet: float,
    crew_size: int = 3,
    daily_rate: float = None,
    dirt_complexity: float = 1.0,
    grade_of_slope_complexity: float = 1.0
) -> dict:
    daily_rate = daily_rate if daily_rate is not None else default_labor_values["daily_rate"]

    num_days = calculate_num_days(
        linear_feet=linear_feet,
        crew_size=crew_size,
        dirt_complexity=dirt_complexity,
        grade_of_slope_complexity=grade_of_slope_complexity
    )

    labor_cost_per_day = daily_rate * crew_size
    total_labor_cost = labor_cost_per_day * num_days

    return {
        "num_days": round(num_days, 2),
        "labor_cost_per_day": round(labor_cost_per_day, 2),
        "total_labor_cost": round(total_labor_cost, 2)
    }


# === Duration Table (Crew Sizes 3–15) ===
def generate_labor_duration_options(
    linear_feet: float,
    panel_install_time_min: float = 106.25,
    panel_length_ft: float = 8.0,
    work_hours_per_day: float = 6.0,
    dirt_complexity: float = 1.0,
    grade_of_slope_complexity: float = 1.0,
    productivity: float = 1.0  # <-- new parameter
) -> list[dict]:
    panel_install_time_hr = panel_install_time_min / 60.0
    time_per_linear_foot = panel_install_time_hr / panel_length_ft
    total_hours = linear_feet * time_per_linear_foot

    complexity_multiplier = (dirt_complexity + grade_of_slope_complexity) - 1
    adjusted_hours = (total_hours * complexity_multiplier) / productivity  # <-- updated line

    print("🔍 Labor Estimator Debug:")
    print(f"Linear Feet: {linear_feet}")
    print(f"Panel Install Time (min): {panel_install_time_min}")
    print(f"Panel Length (ft): {panel_length_ft}")
    print(f"Time per LF (hr): {time_per_linear_foot}")
    print(f"Total Raw Labor Hours: {total_hours}")
    print(f"Dirt Complexity: {dirt_complexity}")
    print(f"Slope Complexity: {grade_of_slope_complexity}")
    print(f"Productivity: {productivity}")
    print(f"Complexity Multiplier: {complexity_multiplier}")
    print(f"Adjusted Labor Hours: {adjusted_hours}")

    options = []
    for crew_size in range(3, 16, 3):
        adjusted_crew_hours = adjusted_hours / crew_size
        estimated_days = adjusted_crew_hours / work_hours_per_day

        print(f"Crew Size: {crew_size}, Estimated Days: {estimated_days}")

        options.append({
            "crew_size": crew_size,
            "estimated_days": round(estimated_days, 6)
        })

    return options



# === Dirt Complexity Lookup ===
dirt_scores = {
    "soft": 1.0,
    "hard": 1.5,
    "core drill": 1.8,
    "jack hammer": 2.0
}


# === Total Cost Calculation ===
def calculate_total_costs(
    fence_details,
    material_prices,
    pricing_strategy,
    daily_rate,
    num_employees,
    dirt_complexity,
    grade_of_slope_complexity,
    productivity=1.0
):
    print("📊 Starting calculate_total_costs()")

    try:
        materials_needed = fence_details["materials_needed"]
        height = fence_details.get("height")
        top_rail = fence_details.get("top_rail", False)
        if isinstance(top_rail, str):
            top_rail = top_rail.lower() == "true"
        linear_feet = fence_details.get("linear_feet")

        print("✅ Fence Details:")
        print("  materials_needed:", materials_needed)
        print("  height:", height)
        print("  top_rail:", top_rail)
        print("  linear_feet:", linear_feet)
    except Exception as e:
        print("❌ Error unpacking fence_details:", str(e))
        raise

    try:
        detailed_material_costs, material_total = calculate_material_costs(
            materials_needed, material_prices, pricing_strategy, height, top_rail
        )
        print("✅ Material costs calculated")
    except Exception as e:
        print("❌ Error in calculate_material_costs:", str(e))
        raise

    try:
        dirt_score = dirt_scores.get(str(dirt_complexity).lower(), 1.0)
        slope_score = calculate_slope_complexity_score(grade_of_slope_complexity)
        print("✅ Complexity Scores:")
        print("  dirt_score:", dirt_score)
        print("  slope_score:", slope_score)
    except Exception as e:
        print("❌ Error calculating complexity scores:", str(e))
        raise

    try:
        labor_costs = calculate_labor_cost(
            linear_feet=linear_feet,
            crew_size=num_employees,
            daily_rate=daily_rate,
            dirt_complexity=dirt_score,
            grade_of_slope_complexity=slope_score
        )
        print("✅ Labor cost calculated")
    except Exception as e:
        print("❌ Error in calculate_labor_cost:", str(e))
        raise

    try:
        labor_duration_options = generate_labor_duration_options(
            linear_feet=linear_feet,
            dirt_complexity=dirt_score,
            grade_of_slope_complexity=slope_score,
            productivity=productivity
        )
        print("✅ Labor duration options calculated")
    except Exception as e:
        print("❌ Error in generate_labor_duration_options:", str(e))
        raise

    try:
        tax_rate = 0.072 if pricing_strategy == "Master Halo Pricing" else 0.0825
        delivery_charge = 100.00 if pricing_strategy == "Master Halo Pricing" else 0.00
        material_tax = round(material_total * tax_rate, 2)

        subtotal = material_total + material_tax + delivery_charge + labor_costs["total_labor_cost"]
        price_per_linear_foot = round(subtotal / linear_feet, 2) if linear_feet else 0

        print("✅ Totals calculated")
    except Exception as e:
        print("❌ Error calculating totals:", str(e))
        raise

    try:
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
        print("✅ Profit margins calculated")
    except Exception as e:
        print("❌ Error calculating profit margins:", str(e))
        raise

    print("✅ Finished calculate_total_costs()\n")

    return {
        "materials_needed": materials_needed,
        "detailed_costs": detailed_material_costs,
        "material_total": material_total,
        "material_tax": material_tax,
        "delivery_charge": delivery_charge,
        "labor_costs": labor_costs,
        "labor_duration_options": labor_duration_options,
        "price_per_linear_foot": price_per_linear_foot,
        "profit_margins": profit_margins
    }

def calculate_slope_complexity_score(percentage: float) -> float:
    if percentage <= 0:
        return 1.0
    percentage = min(45, percentage)
    return round(1.2 + (percentage - 10) * ((2.0 - 1.2) / (45 - 10)), 3)
