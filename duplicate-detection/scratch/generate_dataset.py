"""
Scratch script to create evaluation_dataset.json with 55 labeled evaluation cases.
"""

json_content = """[
  {
    "case_id": "CASE-001",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1001",
      "title": "Garbage burning near school",
      "description": "Garbage is being burned near a school, producing harmful smoke.",
      "location": {"lat": 23.3441, "long": 85.3096, "address": "School Road, District Ranchi"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Air Pollution"
    },
    "problem_b": {
      "problemId": "P1002",
      "title": "Unprocessed waste burning near school",
      "description": "Unprocessed waste is being burned close to the school and causing air pollution.",
      "location": {"lat": 23.3450, "long": 85.3100, "address": "School Road, District Ranchi"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Air Pollution"
    }
  },
  {
    "case_id": "CASE-002",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1003",
      "title": "Potholes on Main Street market",
      "description": "Potholes on Main Street near the central market are causing heavy traffic and minor accidents.",
      "location": {"lat": 23.3600, "long": 85.3300, "address": "Main Street Market"},
      "primaryDomain": "Infrastructure",
      "secondaryDomains": ["Transport"],
      "subcategory": "Road Maintenance"
    },
    "problem_b": {
      "problemId": "P1004",
      "title": "Deep craters on Main St",
      "description": "Deep road craters near the central market on Main St are creating traffic jams and vehicle damage.",
      "location": {"lat": 23.3605, "long": 85.3305, "address": "Main Street Market"},
      "primaryDomain": "Infrastructure",
      "secondaryDomains": ["Transport"],
      "subcategory": "Road Maintenance"
    }
  },
  {
    "case_id": "CASE-003",
    "category": "exact_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1005",
      "title": "Water pipe leak in Sector 4",
      "description": "Drinking water pipeline broken near Sector 4 community hall, causing severe water leakage.",
      "location": {"lat": 23.3700, "long": 85.3400, "address": "Sector 4 Hall"},
      "primaryDomain": "Water & Sanitation",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "Pipe Leakage"
    },
    "problem_b": {
      "problemId": "P1006",
      "title": "Water pipe leak in Sector 4",
      "description": "Drinking water pipeline broken near Sector 4 community hall, causing severe water leakage.",
      "location": {"lat": 23.3700, "long": 85.3400, "address": "Sector 4 Hall"},
      "primaryDomain": "Water & Sanitation",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "Pipe Leakage"
    }
  },
  {
    "case_id": "CASE-004",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1007",
      "title": "Health center emergency drug shortage",
      "description": "Primary health center lacks basic emergency medicines and essential first-aid supplies.",
      "location": {"lat": 23.3800, "long": 85.3500, "address": "PHC Center"},
      "primaryDomain": "Healthcare",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Medical Supplies"
    },
    "problem_b": {
      "problemId": "P1008",
      "title": "Shortage of drugs at local PHC",
      "description": "The local primary health facility has a shortage of critical emergency drugs and first-aid kits.",
      "location": {"lat": 23.3802, "long": 85.3503, "address": "PHC Center"},
      "primaryDomain": "Healthcare",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Medical Supplies"
    }
  },
  {
    "case_id": "CASE-005",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1009",
      "title": "Power cuts in industrial zone",
      "description": "Frequent unexpected power outages occurring in the industrial zone during peak working hours.",
      "location": {"lat": 23.3900, "long": 85.3600, "address": "Industrial Estate"},
      "primaryDomain": "Energy & Power",
      "secondaryDomains": ["Economy"],
      "subcategory": "Power Outage"
    },
    "problem_b": {
      "problemId": "P1010",
      "title": "Electricity supply cuts in industrial estate",
      "description": "Unannounced electricity supply cuts happening repeatedly in the industrial estate in working hours.",
      "location": {"lat": 23.3905, "long": 85.3608, "address": "Industrial Estate"},
      "primaryDomain": "Energy & Power",
      "secondaryDomains": ["Economy"],
      "subcategory": "Power Outage"
    }
  },
  {
    "case_id": "CASE-006",
    "category": "short_vs_detailed",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1011",
      "title": "Open sewage leak on Road 5",
      "description": "Open sewage overflow.",
      "location": {"lat": 23.3400, "long": 85.3100, "address": "Road 5"},
      "primaryDomain": "Water & Sanitation",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Sewage Overflow"
    },
    "problem_b": {
      "problemId": "P1012",
      "title": "Massive sewage overflow spilling onto Road 5",
      "description": "Underground sewer pipe breached on Road 5 creating foul smelling black wastewater spill across 100 meters.",
      "location": {"lat": 23.3405, "long": 85.3105, "address": "Road 5"},
      "primaryDomain": "Water & Sanitation",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Sewage Overflow"
    }
  },
  {
    "case_id": "CASE-007",
    "category": "nearby_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1013",
      "title": "Toxic chemical dumping near river",
      "description": "Illegal industrial waste dumping happening beside North River bank near bridge.",
      "location": {"lat": 23.3500, "long": 85.3200, "address": "North River Bridge"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Water & Sanitation"],
      "subcategory": "Water Pollution"
    },
    "problem_b": {
      "problemId": "P1014",
      "title": "Chemical waste dumped into river",
      "description": "Factories are releasing untreated toxic liquid chemical waste near the river bank next to North bridge.",
      "location": {"lat": 23.3520, "long": 85.3220, "address": "North River Bridge"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Water & Sanitation"],
      "subcategory": "Water Pollution"
    }
  },
  {
    "case_id": "CASE-008",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1015",
      "title": "Streetlight failure near bus stand",
      "description": "Dark stretch near central bus terminus due to broken street lights.",
      "location": {"lat": 23.3550, "long": 85.3250, "address": "Bus Terminus"},
      "primaryDomain": "Infrastructure",
      "secondaryDomains": ["Public Safety"],
      "subcategory": "Street Lighting"
    },
    "problem_b": {
      "problemId": "P1016",
      "title": "Non-functional street lamps at bus station",
      "description": "Streetlights around central bus stand are burnt out causing darkness and safety risk.",
      "location": {"lat": 23.3552, "long": 85.3253, "address": "Bus Terminus"},
      "primaryDomain": "Infrastructure",
      "secondaryDomains": ["Public Safety"],
      "subcategory": "Street Lighting"
    }
  },
  {
    "case_id": "CASE-009",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1017",
      "title": "School building ceiling collapse risk",
      "description": "Government primary school building roof concrete chunks falling off in classrooms.",
      "location": {"lat": 23.3650, "long": 85.3350, "address": "Govt Primary School"},
      "primaryDomain": "Education",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "School Building Damage"
    },
    "problem_b": {
      "problemId": "P1018",
      "title": "Damaged classroom ceiling at Govt school",
      "description": "Roof structure of government school is dilapidated and plaster is crumbling over students.",
      "location": {"lat": 23.3651, "long": 85.3351, "address": "Govt Primary School"},
      "primaryDomain": "Education",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "School Building Damage"
    }
  },
  {
    "case_id": "CASE-010",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1019",
      "title": "Lack of cold storage for tomato harvest",
      "description": "Vegetable farmers losing produce due to absence of cold storage facilities in block market.",
      "location": {"lat": 23.3750, "long": 85.3450, "address": "Block APMC Market"},
      "primaryDomain": "Agriculture",
      "secondaryDomains": ["Economy"],
      "subcategory": "Post-Harvest Storage"
    },
    "problem_b": {
      "problemId": "P1020",
      "title": "No refrigerated warehouse for local farmers",
      "description": "Farmers suffering heavy losses as local APMC market has no refrigerated cold chain warehouse.",
      "location": {"lat": 23.3755, "long": 85.3455, "address": "Block APMC Market"},
      "primaryDomain": "Agriculture",
      "secondaryDomains": ["Economy"],
      "subcategory": "Post-Harvest Storage"
    }
  },
  {
    "case_id": "CASE-011",
    "category": "same_domain_different_issue",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1021",
      "title": "Garbage burning near school",
      "description": "Garbage is being burned near a school, producing harmful smoke.",
      "location": {"lat": 23.3441, "long": 85.3096, "address": "School Road"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Air Pollution"
    },
    "problem_b": {
      "problemId": "P1022",
      "title": "Irregular garbage truck pickup",
      "description": "Garbage collection trucks are not visiting the neighborhood regularly, leaving bins overflowing.",
      "location": {"lat": 23.3441, "long": 85.3096, "address": "School Road"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Waste Management"],
      "subcategory": "Waste Collection"
    }
  },
  {
    "case_id": "CASE-012",
    "category": "same_domain_different_issue",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1023",
      "title": "Drinking water pipe leak",
      "description": "Drinking water pipeline broken near Sector 4 community hall, causing severe water leakage.",
      "location": {"lat": 23.3700, "long": 85.3400, "address": "Sector 4"},
      "primaryDomain": "Water & Sanitation",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "Pipe Leakage"
    },
    "problem_b": {
      "problemId": "P1024",
      "title": "Contaminated drinking water quality",
      "description": "Water supply in Sector 4 is contaminated with brown silt and smells bad when faucets are turned on.",
      "location": {"lat": 23.3700, "long": 85.3400, "address": "Sector 4"},
      "primaryDomain": "Water & Sanitation",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Water Quality"
    }
  },
  {
    "case_id": "CASE-013",
    "category": "same_subcategory_different_incident",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1025",
      "title": "Potholes on Main Street market",
      "description": "Potholes on Main Street near the central market are causing heavy traffic and minor accidents.",
      "location": {"lat": 23.3600, "long": 85.3300, "address": "Main Street Market"},
      "primaryDomain": "Infrastructure",
      "secondaryDomains": ["Transport"],
      "subcategory": "Road Maintenance"
    },
    "problem_b": {
      "problemId": "P1026",
      "title": "Potholes on Highway 33 bypass",
      "description": "Deep potholes on Highway 33 bypass near toll plaza damaging heavy trucks.",
      "location": {"lat": 23.4500, "long": 85.4500, "address": "Highway 33 Bypass"},
      "primaryDomain": "Infrastructure",
      "secondaryDomains": ["Transport"],
      "subcategory": "Road Maintenance"
    }
  },
  {
    "case_id": "CASE-014",
    "category": "same_domain_different_issue",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1027",
      "title": "Primary health center medicine shortage",
      "description": "Primary health center lacks basic emergency medicines and essential first-aid supplies.",
      "location": {"lat": 23.3800, "long": 85.3500, "address": "PHC Center"},
      "primaryDomain": "Healthcare",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Medical Supplies"
    },
    "problem_b": {
      "problemId": "P1028",
      "title": "Primary health center roof leaking",
      "description": "Primary health center building roof is leaking water during heavy rainfall.",
      "location": {"lat": 23.3800, "long": 85.3500, "address": "PHC Center"},
      "primaryDomain": "Healthcare",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "Hospital Infrastructure"
    }
  },
  {
    "case_id": "CASE-015",
    "category": "distant_duplicate",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1029",
      "title": "Garbage burning near school in Ranchi",
      "description": "Garbage is being burned near a school, producing harmful smoke.",
      "location": {"lat": 23.3441, "long": 85.3096, "address": "Ranchi School Road"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Air Pollution"
    },
    "problem_b": {
      "problemId": "P1030",
      "title": "Garbage burning near school in Delhi",
      "description": "Unprocessed waste is being burned close to the school and causing air pollution.",
      "location": {"lat": 28.6139, "long": 77.2090, "address": "Delhi School Road"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Air Pollution"
    }
  },
  {
    "case_id": "CASE-016",
    "category": "different_domain",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1031",
      "title": "Garbage burning near school",
      "description": "Garbage is being burned near a school, producing harmful smoke.",
      "location": {"lat": 23.3441, "long": 85.3096, "address": "School Road"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Air Pollution"
    },
    "problem_b": {
      "problemId": "P1032",
      "title": "High school teacher shortage",
      "description": "High school lacks qualified computer science teachers and functioning desktop computers.",
      "location": {"lat": 23.3441, "long": 85.3096, "address": "School Road"},
      "primaryDomain": "Education",
      "secondaryDomains": ["Human Resources"],
      "subcategory": "Teacher Staffing"
    }
  },
  {
    "case_id": "CASE-017",
    "category": "different_domain",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1033",
      "title": "Potholes on Main Street market",
      "description": "Potholes on Main Street near the central market are causing heavy traffic and minor accidents.",
      "location": {"lat": 23.3600, "long": 85.3300, "address": "Main Street Market"},
      "primaryDomain": "Infrastructure",
      "secondaryDomains": ["Transport"],
      "subcategory": "Road Maintenance"
    },
    "problem_b": {
      "problemId": "P1034",
      "title": "Fertilizer shortage for farmers",
      "description": "Farmers are facing shortage of certified seeds and fertilizers for the upcoming sowing season.",
      "location": {"lat": 23.3600, "long": 85.3300, "address": "Main Street Market"},
      "primaryDomain": "Agriculture",
      "secondaryDomains": ["Economy"],
      "subcategory": "Farm Inputs"
    }
  },
  {
    "case_id": "CASE-018",
    "category": "different_domain",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1035",
      "title": "Power outages in industrial zone",
      "description": "Frequent unexpected power outages occurring in the industrial zone during peak working hours.",
      "location": {"lat": 23.3900, "long": 85.3600, "address": "Industrial Estate"},
      "primaryDomain": "Energy & Power",
      "secondaryDomains": ["Economy"],
      "subcategory": "Power Outage"
    },
    "problem_b": {
      "problemId": "P1036",
      "title": "Blood shortage at hospital blood bank",
      "description": "Public hospital blood bank requires urgent blood donors for rare blood groups.",
      "location": {"lat": 23.3900, "long": 85.3600, "address": "Industrial Estate"},
      "primaryDomain": "Healthcare",
      "secondaryDomains": ["Public Safety"],
      "subcategory": "Blood Bank"
    }
  },
  {
    "case_id": "CASE-019",
    "category": "same_keywords_different_meaning",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1037",
      "title": "Fire outbreak at commercial market",
      "description": "Major electrical short circuit fire in market building causing property damage.",
      "location": {"lat": 23.3600, "long": 85.3300, "address": "Market Building"},
      "primaryDomain": "Public Safety",
      "secondaryDomains": ["Disaster Management"],
      "subcategory": "Fire Hazard"
    },
    "problem_b": {
      "problemId": "P1038",
      "title": "Fire brigade vehicle recruitment drive",
      "description": "Local municipal corporation firing underperforming contractors and recruiting new fire safety drivers.",
      "location": {"lat": 23.3600, "long": 85.3300, "address": "Municipal Office"},
      "primaryDomain": "Governance",
      "secondaryDomains": ["Public Safety"],
      "subcategory": "Contractor Oversight"
    }
  },
  {
    "case_id": "CASE-020",
    "category": "missing_location",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1039",
      "title": "Overflowing dustbins in Ward 12",
      "description": "Public garbage bins overflowing in Ward 12 attracting stray dogs and flies.",
      "location": null,
      "primaryDomain": "Environment",
      "secondaryDomains": ["Sanitation"],
      "subcategory": "Waste Collection"
    },
    "problem_b": {
      "problemId": "P1040",
      "title": "Uncollected trash bins in Ward 12",
      "description": "Trash containers in Ward 12 have not been emptied for five days creating health hazard.",
      "location": null,
      "primaryDomain": "Environment",
      "secondaryDomains": ["Sanitation"],
      "subcategory": "Waste Collection"
    }
  },
  {
    "case_id": "CASE-021",
    "category": "missing_classification",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1041",
      "title": "Broken footbridge over railway track",
      "description": "Pedestrian footbridge over railway line has rusted iron steps and loose railings.",
      "location": {"lat": 23.3440, "long": 85.3090, "address": "Railway Colony"},
      "primaryDomain": null,
      "secondaryDomains": [],
      "subcategory": null
    },
    "problem_b": {
      "problemId": "P1042",
      "title": "Unsafe railway pedestrian overbridge",
      "description": "Rusted footover bridge across railway tracks is dangerous for pedestrians with broken steps.",
      "location": {"lat": 23.3442, "long": 85.3092, "address": "Railway Colony"},
      "primaryDomain": null,
      "secondaryDomains": [],
      "subcategory": null
    }
  },
  {
    "case_id": "CASE-022",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1043",
      "title": "Stray dog pack attacking commuters near park",
      "description": "Group of aggressive stray dogs biting pedestrians near green park entrance.",
      "location": {"lat": 23.3510, "long": 85.3150, "address": "Green Park"},
      "primaryDomain": "Public Safety",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Animal Menace"
    },
    "problem_b": {
      "problemId": "P1044",
      "title": "Dangerous stray dogs near park gate",
      "description": "Pack of feral street dogs harassing and attacking people walking near green park.",
      "location": {"lat": 23.3512, "long": 85.3152, "address": "Green Park"},
      "primaryDomain": "Public Safety",
      "secondaryDomains": ["Public Health"],
      "subcategory": "Animal Menace"
    }
  },
  {
    "case_id": "CASE-023",
    "category": "borderline_similarity",
    "expected_duplicate": false,
    "problem_a": {
      "problemId": "P1045",
      "title": "Drainage canal blocked with plastic debris",
      "description": "Major stormwater drain clogged with single-use plastic bottles preventing rainwater flow.",
      "location": {"lat": 23.3550, "long": 85.3200, "address": "Drainage Lane"},
      "primaryDomain": "Water & Sanitation",
      "secondaryDomains": ["Environment"],
      "subcategory": "Drainage Maintenance"
    },
    "problem_b": {
      "problemId": "P1046",
      "title": "Plastic bottle recycling center shut down",
      "description": "Private plastic bottle recycling unit closed operations leaving plastic scrap piles.",
      "location": {"lat": 23.3550, "long": 85.3200, "address": "Drainage Lane"},
      "primaryDomain": "Environment",
      "secondaryDomains": ["Economy"],
      "subcategory": "Recycling Operations"
    }
  },
  {
    "case_id": "CASE-024",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1047",
      "title": "Low voltage burning household appliances",
      "description": "Severe voltage fluctuation in residential area blowing out refrigerators and fans.",
      "location": {"lat": 23.3710, "long": 85.3410, "address": "Housing Colony B"},
      "primaryDomain": "Energy & Power",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "Voltage Fluctuation"
    },
    "problem_b": {
      "problemId": "P1048",
      "title": "Extreme voltage drops destroying electronic items",
      "description": "Continuous low voltage spikes in housing colony damaging home electrical equipment.",
      "location": {"lat": 23.3712, "long": 85.3413, "address": "Housing Colony B"},
      "primaryDomain": "Energy & Power",
      "secondaryDomains": ["Infrastructure"],
      "subcategory": "Voltage Fluctuation"
    }
  },
  {
    "case_id": "CASE-025",
    "category": "paraphrased_duplicate",
    "expected_duplicate": true,
    "problem_a": {
      "problemId": "P1049",
      "title": "Primary school teacher absenteeism",
      "description": "Appointed government teachers rarely attending classes in rural primary school.",
      "location": {"lat": 23.3810, "long": 85.3510, "address": "Rural School"},
      "primaryDomain": "Education",
      "secondaryDomains": ["Governance"],
      "subcategory": "Teacher Staffing"
    },
    "problem_b": {
      "problemId": "P1050",
      "title": "Teachers missing from rural primary school",
      "description": "Government school teachers remain absent frequently leaving students unsupervised.",
      "location": {"lat": 23.3811, "long": 85.3512, "address": "Rural School"},
      "primaryDomain": "Education",
      "secondaryDomains": ["Governance"],
      "subcategory": "Teacher Staffing"
    }
  }
]"""

# Let's generate 25 more cases programmatically to reach 50 cases total.
import json
base_cases = json.loads(json_content)

more_cases = [
    # 26-30 Duplicate pairs
    ("CASE-026", "paraphrased_duplicate", True, "Dengue outbreak due to stagnant water in ditch", "Stagnant rainwater in roadside trench breeding mosquitoes causing dengue", "Health", "Vector Control", 23.34, 85.31),
    ("CASE-027", "paraphrased_duplicate", True, "Broken playground equipment in municipal park", "Damaged children slides and rusty swings in public park posing injury risk", "Infrastructure", "Public Parks", 23.35, 85.32),
    ("CASE-028", "paraphrased_duplicate", True, "Delayed midday meal supply in elementary school", "School children not receiving midday meals on time due to vendor failure", "Education", "School Nutrition", 23.36, 85.33),
    ("CASE-029", "paraphrased_duplicate", True, "Encroachment of public footpath by illegal stalls", "Footpath completely blocked by unauthorized hawker shops forcing pedestrians onto road", "Urban Planning", "Encroachment", 23.37, 85.34),
    ("CASE-030", "paraphrased_duplicate", True, "Loud commercial speakers blaring past midnight", "Commercial event venue playing loud music beyond permissible night hours", "Public Safety", "Noise Pollution", 23.38, 85.35),

    # 31-35 Non-duplicate related
    ("CASE-031", "same_domain_different_issue", False, "Broken playground equipment in municipal park", "Park boundary wall damaged allowing stray cattle inside", "Infrastructure", "Public Parks", 23.35, 85.32),
    ("CASE-032", "same_domain_different_issue", False, "Delayed midday meal supply in elementary school", "School drinking water filter broken causing stomach infections", "Education", "Sanitation", 23.36, 85.33),
    ("CASE-033", "same_domain_different_issue", False, "Encroachment of public footpath by illegal stalls", "Pavement tiles broken causing tripping hazard", "Urban Planning", "Pedestrian Walkway", 23.37, 85.34),
    ("CASE-034", "same_domain_different_issue", False, "Loud commercial speakers blaring past midnight", "Exhaust fumes from generator set behind venue", "Public Safety", "Air Pollution", 23.38, 85.35),
    ("CASE-035", "same_domain_different_issue", False, "Dengue outbreak due to stagnant water in ditch", "Municipal hospital lacking dengue testing kits", "Health", "Medical Supplies", 23.34, 85.31),

    # 36-40 Paraphrases
    ("CASE-036", "paraphrased_duplicate", True, "Clogged culvert causing street flooding during rain", "Waterlogging on road due to blocked storm culvert", "Infrastructure", "Drainage", 23.39, 85.36),
    ("CASE-037", "paraphrased_duplicate", True, "Public handpump handle broken in Harijan Basti", "Community handpump out of order due to snapped handle", "Water & Sanitation", "Handpump", 23.40, 85.37),
    ("CASE-038", "paraphrased_duplicate", True, "Illegal sand mining in riverbed damaging embankment", "Unlawful extraction of river sand causing bank erosion", "Environment", "Illegal Mining", 23.41, 85.38),
    ("CASE-039", "paraphrased_duplicate", True, "Public library closed during declared opening hours", "Municipal library locked during official working shift", "Culture & Civic", "Public Services", 23.42, 85.39),
    ("CASE-040", "paraphrased_duplicate", True, "Shortage of ambulances at district hospital", "District hospital has insufficient emergency response vehicles", "Healthcare", "Emergency Services", 23.43, 85.40),

    # 41-45 Non-duplicate different domains
    ("CASE-041", "different_domain", False, "Clogged culvert causing street flooding during rain", "Public library closed during declared opening hours", "Infrastructure", "Public Services", 23.39, 85.36),
    ("CASE-042", "different_domain", False, "Public handpump handle broken in Harijan Basti", "Illegal sand mining in riverbed damaging embankment", "Water & Sanitation", "Environment", 23.40, 85.37),
    ("CASE-043", "different_domain", False, "Shortage of ambulances at district hospital", "Loud commercial speakers blaring past midnight", "Healthcare", "Public Safety", 23.43, 85.40),
    ("CASE-044", "different_domain", False, "Subsidized rice missing from ration shop", "Electric wire hanging dangerously low near market", "Governance", "Energy & Power", 23.44, 85.41),
    ("CASE-045", "different_domain", False, "Public toilet building locked for months", "Bridges over canal has loose concrete guard rails", "Sanitation", "Infrastructure", 23.45, 85.42),

    # 46-50 Paraphrase & Borderline
    ("CASE-046", "paraphrased_duplicate", True, "Subsidized rice missing from ration shop", "Fair price shop owner denying ration grain to cardholders", "Governance", "Public Distribution", 23.44, 85.41),
    ("CASE-047", "paraphrased_duplicate", True, "Public toilet building locked for months", "Community restroom facility kept locked by caretaker", "Sanitation", "Public Sanitation", 23.45, 85.42),
    ("CASE-048", "paraphrased_duplicate", True, "Electric wire hanging dangerously low near market", "Overhead high voltage wire sagging close to street vendor stalls", "Energy & Power", "Electrical Safety", 23.46, 85.43),
    ("CASE-049", "borderline_similarity", False, "Public toilet building locked for months", "Sewage treatment plant maintenance overhaul", "Sanitation", "Waste Treatment", 23.45, 85.42),
    ("CASE-050", "borderline_similarity", False, "Subsidized rice missing from ration shop", "Wheat crop harvest procurement center opened", "Governance", "Agriculture Procurement", 23.44, 85.41),
]

for case_id, cat, is_dup, t1, t2, dom, subcat, lat, long in more_cases:
    case_obj = {
        "case_id": case_id,
        "category": cat,
        "expected_duplicate": is_dup,
        "problem_a": {
            "problemId": f"P{case_id.replace('CASE-', '20')}",
            "title": t1,
            "description": t1 + " reported by local resident.",
            "location": {"lat": lat, "long": long, "address": f"Location {case_id}"},
            "primaryDomain": dom,
            "secondaryDomains": [],
            "subcategory": subcat
        },
        "problem_b": {
            "problemId": f"P{case_id.replace('CASE-', '30')}",
            "title": t2,
            "description": t2 + " observed in the neighborhood.",
            "location": {"lat": lat + 0.001 if is_dup else lat + 0.5, "long": long + 0.001 if is_dup else long + 0.5, "address": f"Location {case_id}"},
            "primaryDomain": dom if cat != "different_domain" else "Other",
            "secondaryDomains": [],
            "subcategory": subcat if is_dup else "Other"
        }
    }
    base_cases.append(case_obj)

import os
target_file = r"d:\CivicFix\duplicate-detection\tests\evaluation_dataset.json"
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(base_cases, f, indent=2)

print(f"Successfully wrote {len(base_cases)} labeled evaluation cases to {target_file}")
