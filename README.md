# 🚑 Dynamic Routing System for Emergency Response in Rohingya Refugee Camps

-------------------------------------------------------------------

## Project Overview

This project implements a cutting-edge dynamic routing system designed to optimize emergency healthcare and rescue operations in Rohingya refugee camps. Developed as part of SMT481 Smart City Operations Research Final Project by G1T2 AY24/25, this solution integrates advanced probabilistic models and network optimization algorithms to ensure rapid and safe emergency vehicle deployment during disasters.

Go to app/README.md for instructions on starting up the application.

## Key Features

- **Dynamic Routing**: Adapts to real-time environmental changes and evolving emergency scenarios.
- **Probabilistic Scenario Modeling**: Utilizes statistical analysis and GIS techniques to predict and prepare for various emergency situations.
- **Optimized Network Representation**: Leverages graph theory and network analysis to model camp environments and identify critical infrastructure.
- **Real-time Optimization**: Implements advanced algorithms for continuous route recalibration based on changing conditions.
- **Scalable Simulation Engine**: Enables comprehensive scenario testing and performance evaluation.

## Technical Approach

1. **Data Acquisition and Preparation**
   - Collects and processes geospatial data from UNHCR, OpenStreetMap, USGS, and WHO sources.
   - Cleans, aggregates, and formats data for efficient analysis.

2. **Probabilistic Scenario Modeling**
   - Develops statistical models to forecast flood risk zones, landslide susceptibility, and disease prevalence.
   - Implements GIS-based tools for visualizing high-risk areas and potential disruptions.

3. **Network Representation and Impact Assessment**
   - Constructs graph representations of camp environments using NetworkX.
   - Analyzes impact of scenarios on accessibility, population displacement, and healthcare needs.

4. **Optimization Model Formulation**
   - Defines objectives (minimize response time, maximize coverage) and constraints (road closures, resource limitations).
   - Implements mathematical models for emergency vehicle routing and resource allocation.

5. **Algorithm Selection and Implementation**
   - Employs Dijkstra's algorithm, A*, and Genetic Algorithms for optimal route finding.
   - Integrates optimization solvers for real-time decision making.

6. **Simulation and Evaluation**
   - Develops comprehensive simulation framework for scenario testing.
   - Implements performance metrics and sensitivity analysis tools.

7. **Refinement and Deployment**
   - Conducts user feedback sessions with emergency responders and community members.
   - Refines system based on evaluation results and real-world performance data.
   - Deploys system for operational use and implements continuous monitoring and improvement processes.


## Implementation Details

- Primary technologies used: Python, NetworkX, optimization libraries (e.g., PuLP, CVXPY)
- Data processing: Pandas, Geopandas
- Visualization: Matplotlib, Plotly
- Simulation framework: Custom-built using Python and network analysis libraries

## Future Enhancements

- Integration with IoT sensors for real-time environmental data
- Machine learning models for predictive maintenance of critical infrastructure
- Blockchain-based secure data sharing platform for emergency response coordination

## License

This project is licensed under the MIT License. 
