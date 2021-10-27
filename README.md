# confluence

Program that orchestrates and executes Confluence modules in AWS Batch. Submits jobs to queues associated with specific compute environments.

Note: This program uses `boto3` to interface with the AWS API.

# installation

1. Clone the repository to your file system.
2. confluence-aws is best run with Python virtual environments so install venv and create a virutal environment: https://docs.python.org/3/library/venv.html
3. Activate the virtual environment and use pip to install dependencies: `pip install -r requirements.txt`

# configuration

Edit the `confluence.yaml` file to indicate which modules you wish to run and the size of the job array if applicable. Make sure to add a log and submission file path. (Extensive documentation on configuration options coming soon.)

# execution

1. Activate your virtual environment.
2. Run `python3 run_confluence.py` 
3. Log files and a file that tracks submissions are written to the paths indicated in the configuration file.

# tests

1. Run the unit tests: `python3 -m unittest discover tests`