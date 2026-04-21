# Cook County Property Assessment: Data Systems & Predictive Modeling

### Project Overview
A comprehensive two-part analysis of property valuation data for the Cook County Assessor’s Office (CCAO). This project spans the full data science lifecycle, from large-scale data ingestion and cleaning to advanced predictive modeling and model auditing.

### Technical Skills Demonstrated
* **Modeling:** Scikit-Learn (Linear Regression), Cross-Validation, Residual Analysis.
* **Data Engineering:** Pandas (500k+ records), Feature Engineering (Log-scaling, Categorical Encoding).
* **Visualization:** Matplotlib/Seaborn (Spatial Disparity Mapping).

### Key Results
* **Project A1:** Conducted exploratory data analysis on a 500k+ record dataset, identifying key drivers of valuation variance.
* **Project A2:** Developed an optimized regression model achieving a **Training RMSE of 0.465**. Implemented feature importance analysis to ensure model transparency and interpretability.

---
*Developed at UC Berkeley.*


# Local Color: California Artist Recommender

This project explores the intersection of regional music scenes and relational database design. It was built as a collaborative experiment using Cursor (Claude), serving as an early case study in orchestrating AI for rapid software prototyping—or "vibe coding."

Instead of just accepting a globalized recommendation algorithm, Local Color uses a local SQLite architecture to prioritize and surface Californian musicians based on artist similarity.
## Key Features
* **Spotify API Integration:** Fetches real-time artist data and metadata for accurate recommendation mapping.
* **Optimized Data Storage:** Utilizes a custom SQLite database with SQLAlchemy to manage artist relations and genre indexing.
* **Asynchronous UI:** Built with PyQt6 to ensure a responsive, non-blocking user experience during API requests.
* **Relational Mapping:** Implemented a many-to-many junction schema to link artists with diverse musical genres.

## Technical Stack
* **Language:** Python 3.x
* **Database:** SQLite / SQLAlchemy
* **Framework:** PyQt6 (GUI & Multi-threading)
* **API:** Spotify Web API

## Database Schema
The application utilizes a relational SQLite structure to minimize redundancy and optimize retrieval:
* `artists`: Primary table storing artist metadata and geographic status.
* `genres`: Master list of musical classifications.
* `artist_genres`: Junction table implementing many-to-many relationships between artists and genres.

## Setup & Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
