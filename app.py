import streamlit as st
import sqlite3
import qrcode
from io import BytesIO
import pandas as pd
import os

# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------

st.set_page_config(
    page_title="R-Biowaste",
    page_icon="♻️",
    layout="wide"
)

DB_NAME = "r_biowaste.db"

# ===================================================
# IMPORTANT: PUBLIC APP URL
# ===================================================
# After deploying to Streamlit Cloud, replace this
# with your actual public URL.
#
# Example:
# APP_URL = "https://r-biowaste.streamlit.app"
#
APP_URL = "https://r---biowaste-jdsxgkkkuxxbsblztsczea.streamlit.app"


# ---------------------------------------------------
# DATABASE
# ---------------------------------------------------

def create_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste (
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            source TEXT,
            components TEXT,
            processing TEXT,
            applications TEXT,
            products TEXT,
            environmental_benefit TEXT,
            score INTEGER
        )
    """)

    data = [

        (
            "BW001",
            "Banana Peel",
            "Food / Plant Waste",
            "Banana consumption and fruit processing",
            "Cellulose, hemicellulose, lignin and organic matter",
            "Washing → Cutting → Drying → Grinding → Characterization",
            "Composting, biomaterial research and bioresource recovery",
            "Biochar, compost, banana-fiber biomaterial and extract research",
            "Reduces organic food waste and supports conversion into useful biomass",
            82
        ),

        (
            "BW002",
            "Corn Husk",
            "Agricultural Waste",
            "Corn cultivation and processing",
            "Cellulose, hemicellulose and lignin",
            "Cleaning → Drying → Size reduction → Characterization",
            "Fiber research, biomaterial research and composting",
            "Fiber-based packaging, paper/board, biodegradable composites and biochar",
            "Can reduce agricultural residue accumulation and burning",
            88
        ),

        (
            "BW003",
            "Eggshell",
            "Food Waste",
            "Egg consumption and food industry",
            "Calcium carbonate-rich material",
            "Cleaning → Drying → Grinding → Characterization",
            "Material research and agricultural applications",
            "Calcium-rich soil amendment, calcium carbonate material and adsorbent research",
            "Converts mineral-rich food waste into a potential useful resource",
            78
        ),

        (
            "BW004",
            "Coffee Waste",
            "Food / Biomass Waste",
            "Coffee preparation and processing",
            "Organic matter, cellulose and lignocellulosic components",
            "Drying → Grinding → Characterization",
            "Composting and bioresource recovery research",
            "Compost, biochar, mushroom-substrate research and biomass fuel research",
            "Reduces organic waste accumulation and supports resource recovery",
            76
        ),

        (
            "BW005",
            "Orange Peel",
            "Food / Plant Waste",
            "Orange consumption and juice processing",
            "Pectin, cellulose, hemicellulose, essential oils and organic compounds",
            "Washing → Drying → Grinding → Extraction / Characterization",
            "Pectin recovery, essential oil research, composting and biomaterial research",
            "Pectin-based material, citrus essential oil, compost and bio-based material research",
            "Reduces fruit waste and supports recovery of useful plant compounds",
            85
        ),

        (
            "BW006",
            "Potato Peel",
            "Food / Plant Waste",
            "Potato processing and household food preparation",
            "Starch, cellulose, hemicellulose and organic compounds",
            "Washing → Drying → Grinding → Characterization",
            "Composting, starch recovery research and biomaterial research",
            "Starch-based biofilm research, compost, biochar and recovered starch products",
            "Reduces organic food waste and supports biomass recovery",
            80
        ),

        (
            "BW007",
            "Mango Peel",
            "Food / Plant Waste",
            "Mango consumption and fruit processing",
            "Pectin, cellulose, hemicellulose and polyphenolic compounds",
            "Washing → Drying → Grinding → Extraction / Characterization",
            "Pectin recovery, antioxidant research, composting and biomaterial research",
            "Pectin-based material, antioxidant extract research, compost and biochar",
            "Converts fruit-processing waste into a potential bioresource",
            87
        )
    ]

    for item in data:

        cursor.execute("""
            INSERT OR IGNORE INTO waste
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    conn.close()


# ---------------------------------------------------
# GET DATA
# ---------------------------------------------------

def get_waste():

    conn = sqlite3.connect(DB_NAME)

    data = conn.execute(
        "SELECT * FROM waste"
    ).fetchall()

    conn.close()

    return data


# ---------------------------------------------------
# ADD WASTE
# ---------------------------------------------------

def add_waste(data):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO waste
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()


# ---------------------------------------------------
# IMAGE INFORMATION
# ---------------------------------------------------

image_files = {

    "BW001": "banana.jpg",
    "BW002": "corn.jpg",
    "BW003": "eggshell.jpg",
    "BW004": "coffee.jpg",
    "BW005": "orange.jpg",
    "BW006": "potato.jpg",
    "BW007": "mango.jpg"
}


# ---------------------------------------------------
# RECOMMENDED PATHWAY
# ---------------------------------------------------

def recommended_pathway(waste_id):

    pathways = {

        "BW001":
        "🍌 Banana Peel → Biomass Recovery → Biochar / Fiber Biomaterial",

        "BW002":
        "🌽 Corn Husk → Fiber Recovery → Biodegradable Composite / Packaging",

        "BW003":
        "🥚 Eggshell → Calcium Recovery → Soil Amendment / Calcium-Based Material",

        "BW004":
        "☕ Coffee Waste → Biomass Recovery → Compost / Biochar",

        "BW005":
        "🍊 Orange Peel → Pectin Recovery → Bio-Based Material / Extract",

        "BW006":
        "🥔 Potato Peel → Starch Recovery → Biofilm / Biomaterial Research",

        "BW007":
        "🥭 Mango Peel → Pectin / Bioactive Recovery → Bio-Based Material"
    }

    return pathways.get(
        waste_id,
        "♻️ Characterization → Processing → Useful Product / Output"
    )

# ---------------------------------------------------
# EXPLAINABLE WASTE VALUE SCORING
# ---------------------------------------------------

def calculate_value_score(waste_row):

    waste_id = waste_row[0]

    components = waste_row[4].lower()
    applications = waste_row[6].lower()
    products = waste_row[7].lower()
    environmental = waste_row[8].lower()

    # 1. RECOVERABILITY / PROCESSING EASE
    easy_process_words = [
        "washing", "drying", "grinding",
        "cutting", "cleaning"
    ]

    recovery_points = sum(
        3 for word in easy_process_words
        if word in waste_row[5].lower()
    )

    recoverability = min(20, 8 + recovery_points)

    # 2. USEFUL COMPONENTS
    component_keywords = [
        "cellulose", "hemicellulose", "lignin",
        "pectin", "starch", "calcium carbonate",
        "essential oils", "polyphenolic",
        "organic matter"
    ]

    component_count = sum(
        1 for word in component_keywords
        if word in components
    )

    useful_components = min(
        20,
        5 + (component_count * 3)
    )

    # 3. PRODUCT POTENTIAL
    product_keywords = [
        "biochar", "compost", "biomaterial",
        "packaging", "paper", "board",
        "composite", "film", "extract",
        "essential oil", "soil amendment",
        "adsorbent", "mushroom substrate",
        "biofilm", "starch"
    ]

    product_count = sum(
        1 for word in product_keywords
        if word in products
    )

    product_potential = min(
        20,
        5 + (product_count * 3)
    )

    # 4. ENVIRONMENTAL BENEFIT
    environmental_keywords = [
        "reduces", "reduce", "waste",
        "burning", "resource recovery",
        "organic waste", "agricultural residue",
        "useful biomass"
    ]

    environmental_count = sum(
        1 for word in environmental_keywords
        if word in environmental
    )

    environmental_benefit = min(
        20,
        8 + (environmental_count * 2)
    )

    # 5. AVAILABILITY
    availability_by_id = {
        "BW001": 17,  # Banana Peel
        "BW002": 18,  # Corn Husk
        "BW003": 17,  # Eggshell
        "BW004": 16,  # Coffee Waste
        "BW005": 17,  # Orange Peel
        "BW006": 18,  # Potato Peel
        "BW007": 15   # Mango Peel
    }

    availability = availability_by_id.get(
        waste_id,
        10
    )

    total_score = (
        recoverability
        + useful_components
        + product_potential
        + environmental_benefit
        + availability
    )

    return {
        "Recoverability": recoverability,
        "Useful Components": useful_components,
        "Product Potential": product_potential,
        "Environmental Benefit": environmental_benefit,
        "Availability": availability,
        "Total": total_score
    }


# ---------------------------------------------------
# PRODUCT INFORMATION
# ---------------------------------------------------

product_info = {

    "BW001": [
        ("🔥 Biochar", "Biomass can be converted into carbon-rich biochar."),
        ("🧵 Fiber Biomaterial", "Plant fibers can be explored for biomaterial applications."),
        ("🌱 Compost", "Organic matter can be biologically decomposed into compost.")
    ],

    "BW002": [
        ("📦 Fiber Packaging", "Corn husk fiber can be explored for packaging materials."),
        ("📄 Paper / Board", "Recovered fibers can be investigated for board or paper."),
        ("🧱 Biocomposite", "Fiber can reinforce biodegradable composite materials.")
    ],

    "BW003": [
        ("🌱 Soil Amendment", "Calcium-rich eggshell material can have agricultural applications."),
        ("⚪ Calcium Carbonate Material", "Eggshell is rich in calcium carbonate."),
        ("🧪 Adsorbent Research", "Processed eggshell can be studied as an adsorbent material.")
    ],

    "BW004": [
        ("🌱 Compost", "Coffee waste can be biologically processed into compost."),
        ("🔥 Biochar", "Dried biomass can be investigated for biochar production."),
        ("🍄 Mushroom Substrate", "Coffee waste can be studied as a substrate component.")
    ],

    "BW005": [
        ("🧪 Pectin Material", "Pectin recovered from citrus peel can be studied for biomaterials."),
        ("📦 Bio-based Film", "Pectin can be investigated in biodegradable film formulations."),
        ("🍊 Essential Oil", "Citrus peel contains essential oils that can be recovered.")
    ],

    "BW006": [
        ("📦 Biofilm", "Potato peel starch can be investigated for biodegradable films."),
        ("🌱 Compost", "Organic potato peel waste can be composted."),
        ("🧪 Starch Recovery", "Starch can be recovered and studied for biomaterial applications.")
    ],

    "BW007": [
        ("🧪 Pectin Material", "Mango peel contains pectin that can be recovered for research."),
        ("🔬 Bioactive Extract", "Polyphenolic compounds can be investigated through extraction."),
        ("🌱 Compost / Biochar", "Mango peel biomass can be processed through biological or thermal pathways.")
    ]
}


# ---------------------------------------------------
# DATABASE START
# ---------------------------------------------------

create_database()

waste_data = get_waste()


# ===================================================
# QR PARAMETER
# ===================================================

qr_page = st.query_params.get("page")
qr_waste_id= None


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("♻️ R-BIOWASTE")

st.sidebar.write(
    "Biological Waste → Data → Value"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🔎 Explore Waste",
        "➕ Add New Waste",
        "📊 Compare Waste"
    ]
)


# ===================================================
# QR SCAN REDIRECT
# ===================================================

if qr_page=="explore":

    page = "🔎 Explore Waste"


# ===================================================
# DASHBOARD
# ===================================================

if page == "🏠 Dashboard":

    st.title("♻️ R-BIOWASTE")

    st.subheader(
        "Biological Waste → Data → Value"
    )

    st.write(
        "A student innovation prototype that connects "
        "physical biological waste samples with digital "
        "information and potential waste-to-value pathways."
    )

    st.divider()

    categories = sorted(
        list(set(row[2] for row in waste_data))
    )

    average_score = (
        sum(row[9] for row in waste_data)
        / len(waste_data)
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Waste Types", len(waste_data))

    with col2:
        st.metric("Categories", len(categories))

    with col3:
        st.metric(
            "Average Value Score",
            f"{average_score:.0f}/100"
        )

    with col4:
        st.metric("System Status", "WORKING")

    st.divider()

    st.header("🔄 How R-Biowaste Works")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 1️⃣ Identify")
        st.write(
            "Give each biological waste sample a unique ID."
        )

    with col2:
        st.markdown("### 2️⃣ Characterize")
        st.write(
            "Record source, composition and important properties."
        )

    with col3:
        st.markdown("### 3️⃣ Recover")
        st.write(
            "Explore possible processing and recovery pathways."
        )

    with col4:
        st.markdown("### 4️⃣ Create Value")
        st.write(
            "Identify possible useful products and outputs."
        )

    st.divider()

    st.header("🌱 Waste → Value")

    st.success(
        "Physical Waste → Unique ID → Digital Profile → "
        "Component → Recovery → Possible Product"
    )

    st.divider()

    st.header("💡 Project Innovation")

    st.info(
        "R-Biowaste gives physical biological waste samples "
        "a unique digital identity and connects them with "
        "composition, processing, possible products and "
        "an experimental Waste Value Score."
    )


# ===================================================
# EXPLORE WASTE
# ===================================================

elif page == "🔎 Explore Waste":

    st.title("🔎 Explore Biological Waste")

    search = st.text_input(
        "Search waste",
        placeholder="Example: Orange"
    )

    categories = sorted(
        list(set(row[2] for row in waste_data))
    )

    category = st.selectbox(
        "Filter by category",
        ["All"] + categories
    )

    # ------------------------------------------------
    # QR SCAN SELECTION
    # ------------------------------------------------

    if qr_waste_id:

        qr_match = [
            row for row in waste_data
            if row[0] == qr_waste_id
        ]

        if qr_match:

            filtered = qr_match

            st.success(
                f"📱 QR Scan Successful — "
                f"Digital Waste ID: {qr_waste_id}"
            )

        else:

            filtered = []

            st.error(
                "❌ Waste ID from QR was not found."
            )

    else:

        filtered = []

        for row in waste_data:

            name_match = (
                search.lower() in row[1].lower()
                if search
                else True
            )

            category_match = (
                category == "All"
                or category == row[2]
            )

            if name_match and category_match:
                filtered.append(row)

    st.write(
        f"Showing {len(filtered)} waste type(s)"
    )

    if filtered:

        # ------------------------------------------------
        # SELECTION
        # ------------------------------------------------

        if qr_waste_id:

            selected_row = filtered[0]

        else:

            names = [
                f"{row[0]} — {row[1]}"
                for row in filtered
            ]

            selected = st.selectbox(
                "Select waste",
                names
            )

            selected_id = selected.split(" — ")[0]

            selected_row = next(
                row for row in waste_data
                if row[0] == selected_id
            )

        st.divider()

        # ------------------------------------------------
        # WASTE IMAGE
        # ------------------------------------------------

        image_path = image_files.get(
            selected_row[0]
        )

        if image_path and os.path.exists(image_path):

            col_image, col_title = st.columns([1, 2])

            with col_image:

                st.image(
                    image_path,
                    width="stretch"
                )

            with col_title:

                st.header(
                    f"♻️ {selected_row[1]}"
                )

                st.info(
                    f"Digital Waste ID: {selected_row[0]}"
                )

        else:

            st.header(
                f"♻️ {selected_row[1]}"
            )

            st.info(
                f"Digital Waste ID: {selected_row[0]}"
            )

            st.caption(
                "📷 Add the corresponding image to the "
                "'images' folder."
            )

        st.divider()

        # ------------------------------------------------
        # BASIC INFORMATION
        # ------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### 📂 Category")
            st.write(selected_row[2])

            st.markdown("### 🌱 Source")
            st.write(selected_row[3])

            st.markdown("### 🧪 Major Components")
            st.write(selected_row[4])

        with col2:

            st.markdown("### ⚙️ Processing Pathway")
            st.write(selected_row[5])

            st.markdown("### ♻️ Potential Applications")
            st.write(selected_row[6])

            st.markdown("### 🌍 Environmental Benefit")
            st.write(selected_row[8])

        st.divider()

        # ------------------------------------------------
        # WASTE TO VALUE FLOW
        # ------------------------------------------------

        st.subheader(
            "🔬 From Waste to Possible Product"
        )

        flow1, flow2, flow3, flow4 = st.columns(4)

        with flow1:
            st.markdown("### ♻️ Waste")
            st.write(selected_row[1])

        with flow2:
            st.markdown("### 🧪 Component")
            st.write(selected_row[4])

        with flow3:
            st.markdown("### ⚙️ Recovery")
            st.write(selected_row[5])

        with flow4:
            st.markdown("### 🏭 Possible Output")
            st.write(selected_row[7])

        st.divider()

        # ------------------------------------------------
        # PRODUCT CARDS
        # ------------------------------------------------

        st.subheader(
            "🏭 What Can This Waste Potentially Become?"
        )

        products = product_info.get(
            selected_row[0],
            []
        )

        if products:

            product_columns = st.columns(
                len(products)
            )

            for column, product in zip(
                product_columns,
                products
            ):

                with column:

                    st.markdown(
                        f"### {product[0]}"
                    )

                    st.write(
                        product[1]
                    )

        st.divider()

        # ------------------------------------------------
        # RECOMMENDED PATHWAY
        # ------------------------------------------------

        st.subheader(
            "🎯 Recommended Value Pathway"
        )

        st.success(
            recommended_pathway(
                selected_row[0]
            )
        )

        st.caption(
            "Prototype recommendation based on the selected waste type."
        )

        st.divider()

        # ------------------------------------------------
        # POSSIBLE PRODUCTS
        # ------------------------------------------------

        st.subheader(
            "🏭 Possible Useful Products / Outputs"
        )

        st.write(
            selected_row[7]
        )

        st.divider()

        # ------------------------------------------------
        # VALUE SCORE
        # ------------------------------------------------

      st.subheader(
            "♻️ Prototype Waste Value Score"
        )

        score_details = calculate_value_score(selected_row)
        score = score_details["Total"]

        st.progress(score / 100)

        st.metric(
            "Value Score",
            f"{score}/100"
        )

       st.markdown("### 📊 Why this score?")

for factor, points in score_details.items():
    if factor != "Total":
        st.write(f"**{factor}:** {points}/20")

st.caption(
    "Score is calculated using a prototype rule-based "
    "methodology. Each factor contributes a maximum of 20 points."
)

        st.divider()

        # =================================================
        # QR CODE
        # =================================================

        st.subheader(
            "📱 Digital Waste Identity"
        )

        # Public URL containing waste ID
        waste_url = APP_URL + "?page=explore"

        qr = qrcode.make(waste_url)

        buffer = BytesIO()

        qr.save(
            buffer,
            format="PNG"
        )

        col_qr, col_info = st.columns([1, 2])

        with col_qr:

            st.image(
                buffer.getvalue(),
                width=220
            )

        with col_info:

            st.markdown(
                "### 🔗 Scan to Open Digital Profile"
            )

            st.write(
                "Judge can scan this QR code using "
                "the phone camera or Google Lens."
            )

            st.code(
                waste_url,
                language="text"
            )

            st.success(
                "QR → Digital Waste Profile → "
                "Image + Components + Processing + Products + Score"
            )

        st.caption(
            "Each biological waste sample has a unique digital identity."
        )

    else:

        st.warning(
            "No matching waste found."
        )


# ===================================================
# ADD NEW WASTE
# ===================================================

elif page == "➕ Add New Waste":

    st.title(
        "➕ Add New Biological Waste"
    )

    st.write(
        "Create a new digital identity for a biological waste sample."
    )

    with st.form("add_waste_form"):

        waste_id = st.text_input(
            "Waste ID",
            placeholder="Example: BW008"
        )

        name = st.text_input(
            "Waste Name",
            placeholder="Example: Apple Peel"
        )

        category = st.text_input(
            "Category",
            placeholder="Example: Food / Plant Waste"
        )

        source = st.text_input(
            "Source",
            placeholder="Where does this waste come from?"
        )

        components = st.text_area(
            "Major Components",
            placeholder="Example: Cellulose, pectin..."
        )

        processing = st.text_area(
            "Processing Pathway",
            placeholder="Example: Washing → Drying → Grinding"
        )

        applications = st.text_area(
            "Potential Applications",
            placeholder="Example: Composting, biomaterial research..."
        )

        products = st.text_area(
            "Possible Useful Products / Outputs",
            placeholder="Example: Biofilm, compost, biochar..."
        )

        environmental_benefit = st.text_area(
            "Environmental Benefit"
        )

        score = st.slider(
            "Prototype Waste Value Score",
            0,
            100,
            70
        )

        submitted = st.form_submit_button(
            "➕ Add Waste"
        )

    if submitted:

        if not waste_id or not name:

            st.error(
                "Waste ID and Waste Name are required."
            )

        else:

            try:

                add_waste(
                    (
                        waste_id,
                        name,
                        category,
                        source,
                        components,
                        processing,
                        applications,
                        products,
                        environmental_benefit,
                        score
                    )
                )

                st.success(
                    f"{name} successfully added as {waste_id}!"
                )

                st.rerun()

            except sqlite3.IntegrityError:

                st.error(
                    "This Waste ID already exists. Use a new ID."
                )


# ===================================================
# COMPARE WASTE
# ===================================================

elif page == "📊 Compare Waste":

    st.title(
        "📊 Compare Biological Waste"
    )

    st.write(
        "Compare biological wastes based on their "
        "components, processing pathways, useful products, "
        "applications and prototype value score."
    )

    conn = sqlite3.connect(DB_NAME)

    compare_df = pd.read_sql_query(
        """
        SELECT
            id,
            name,
            category,
            source,
            components,
            processing,
            applications,
            products,
            environmental_benefit,
            score
        FROM waste
        ORDER BY name
        """,
        conn
    )

    conn.close()

    if compare_df.empty:

        st.error(
            "❌ No waste data found in the database."
        )

    else:

        st.success(
            f"♻️ {len(compare_df)} waste types available for comparison."
        )

        st.divider()

        waste_options = [
            f"{row['id']} — {row['name']}"
            for _, row in compare_df.iterrows()
        ]

        selected_wastes = st.multiselect(
            "♻️ Select 2 or more waste types",
            waste_options,
            default=waste_options[:2]
        )

        if len(selected_wastes) >= 2:

            selected_ids = [
                item.split(" — ")[0]
                for item in selected_wastes
            ]

            selected_df = compare_df[
                compare_df["id"].isin(selected_ids)
            ].copy()

            selected_df = selected_df.sort_values(
                by="score",
                ascending=False
            )

            st.divider()

            st.subheader(
                "🏆 Value Score Comparison"
            )

            score_columns = st.columns(
                len(selected_df)
            )

            for column, (_, row) in zip(
                score_columns,
                selected_df.iterrows()
            ):

                with column:

                    st.metric(
                        row["name"],
                        f"{row['score']}/100"
                    )

            st.divider()

            st.subheader(
                "📋 Detailed Comparison"
            )

            display_df = selected_df[
                [
                    "name",
                    "category",
                    "components",
                    "processing",
                    "applications",
                    "products",
                    "environmental_benefit",
                    "score"
                ]
            ].copy()

            display_df.columns = [
                "Waste",
                "Category",
                "Major Components",
                "Processing",
                "Applications",
                "Possible Products",
                "Environmental Benefit",
                "Value Score"
            ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader(
                "📊 Prototype Waste Value Score"
            )

            chart_data = selected_df[
                ["name", "score"]
            ].set_index("name")

            st.bar_chart(
                chart_data
            )

            st.divider()

            best_row = selected_df.iloc[0]

            st.subheader(
                "🏆 Highest Value Potential"
            )

            st.success(
                f"**{best_row['name']}** has the highest "
                f"prototype value score: "
                f"**{best_row['score']}/100**"
            )

            st.subheader(
                f"💡 Recommended Waste: {best_row['name']}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### 🧪 Major Components")

                st.write(
                    best_row["components"]
                )

                st.markdown("### ⚙️ Processing Pathway")

                st.write(
                    best_row["processing"]
                )

                st.markdown("### 📦 Possible Products")

                st.write(
                    best_row["products"]
                )

            with col2:

                st.markdown("### 🔬 Potential Applications")

                st.write(
                    best_row["applications"]
                )

                st.markdown("### 🌱 Environmental Benefit")

                st.write(
                    best_row["environmental_benefit"]
                )

                st.metric(
                    "Prototype Value Score",
                    f"{best_row['score']}/100"
                )

            st.divider()

            st.caption(
                "⚠️ The Value Score is an experimental "
                "student-project scoring system and is "
                "not an official scientific standard."
            )

        else:

            st.info(
                "👆 Select at least 2 waste types to start comparison."
            )


# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.divider()

st.caption(
    "R-Biowaste | Student Innovation Prototype | "
    "Biological Waste → Data → Value"
)
