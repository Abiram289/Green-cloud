# Enhanced VM Placement Simulation System

This project simulates data-center VM placement and demonstrates the superiority of a multi-objective, AI-enhanced strategy over traditional heuristics.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.10+
*   pip
*   venv (recommended)
*   Git

### Cloning the Repository

1.  Open a terminal or command prompt.
2.  Navigate to the directory where you want to clone the project.
3.  Run the following command:

    ```bash
    git clone https://github.com/your-username/your-repository.git
    ```

### Installation and Setup

1.  Navigate to the project's root directory:

    ```bash
    cd your-repository
    ```

2.  Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  Run the Flask web application:

    ```bash
    python app.py
    ```

2.  Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Configuration

The application's configuration is managed through environment variables or a configuration file. This allows you to customize settings without modifying the source code.

### Environment Variables

You can set the following environment variables to configure the application:

*   `FLASK_APP`: The main application file (default: `app.py`).
*   `FLASK_ENV`: The environment (e.g., `development`, `production`).
*   `SECRET_KEY`: A secret key for session management.

### Configuration File

You can also use a configuration file (e.g., `config.py`) to store your settings. To use a configuration file, you can load it in `app.py`.

## Project Structure

*   `app.py`: The main Flask web application file.
*   `src/`: Core Python modules for the simulation engine.
*   `templates/`: HTML templates for the web dashboard.
*   `static/`: Static files (CSS, JavaScript).
*   `models/`: Saved AI models and scalers.
*   `data/`: Datasets for training and simulation.

## AI-Powered Placement

The core of this project is the `HybridAIPredictorPlacement` algorithm, which uses a multi-objective approach to optimize VM placement. It considers factors like energy consumption, cost, resource utilization, and SLA compliance to make intelligent decisions.

For more details on the AI model and algorithms, please refer to the documentation in the `src/` directory.
