# powercut_reporting_system
1.Ensure the virtual environment is activated:.venv/bin/active
2.Install dependencies: pip install -r requirements.txt 
3.Run the application: python3 main.py
This will launch the GUI window. The app includes tabs for reporting power cuts, viewing reports, and analytics. If you encounter display issues, ensure you're running in an environment with GUI support.

4. Set the database credentials before starting the app:
    export POWERCUT_DB_USER=root
export POWERCUT_DB_PASSWORD='your_root_password'
export POWERCUT_DB_HOST=localhost
export POWERCUT_DB_PORT=3306
export POWERCUT_DB_NAME=powercut_db
python3 main.py
